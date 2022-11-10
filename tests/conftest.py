import asyncio
from unittest.mock import patch

import pytest
import warnings

import pytest_asyncio
from httpx import AsyncClient

from solution.channel.fastapi.main import app
import config

pytest_plugins = [
    'tests.plugins.configure_plugin',
]


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    if config.DB_TYPE in [config.DBType.mysql, config.DBType.mariadb]:
        import alembic
        from alembic.config import Config
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        conf = Config("./solution/sp/sql_base/migrations/alembic.ini", ini_section=config.DB_TYPE.value.lower())

        conf.set_main_option('script_location', './solution/sp/sql_base/migrations/')
        conf.set_main_option(
            'version_locations',
            f'./solution/sp/sql_base/migrations/{conf.get_main_option("version_locations")}'
        )
        alembic.command.upgrade(conf, "head")
        yield
        alembic.command.downgrade(conf, "base")
    else:
        raise Exception("Unsupported DB")


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def get_ingest_data_payload():
    """ Get ingest data payload """
    return {
        "tenant_id": "string",
        "app_id": "string",
        "entity_type": "string",
        "src_type": "string",
        "is_batch_required": True,
        "batch_size": 0,
        "subscriber_name": [],
        "enrich_oncreation": True,
        "filters": []
    }


@pytest.fixture(scope="session")
def get_db():
    # apply_migrations()
    from solution.profile import profile
    db = profile.db_client
    yield db
    try:
        db.session.close_all()
        db.engine.dispose()
        db.engine = None
        db.session = None
        import gc
        gc.collect()
    except Exception as e:
        print(e)


@pytest_asyncio.fixture
async def get_api_client() -> AsyncClient:
    with patch("solution.channel.fastapi.auth_controller.Client"):
        with patch("solution.channel.fastapi.auth_controller.AuthTokenValidator"):
            async with AsyncClient(app=app, base_url="http://test") as ac:
                yield ac
