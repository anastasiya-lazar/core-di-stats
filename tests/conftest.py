import pytest
import warnings
from fastapi.testclient import TestClient

from solution.channel.fastapi.main import app
import config
from solution.sp.sql_base.models import SubscriberStatusEnum

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


@pytest.fixture
def get_valid_message(request_id="test", total_record_count=0, total_failed_count=0, total_success_count=0):
    """ Get valid message """
    return {
        "request_id": request_id,
        "source_id": "str",
        "file_uri": "str",
        "subscriber": "str",
        "status": SubscriberStatusEnum.RUNNING.value,
        "is_error": False,
        "message": "str",
        "total_record_count": total_record_count,
        "total_failed_count": total_failed_count,
        "total_success_count": total_success_count,
        "status_url": "str"
    }


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


def pytest_configure():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    from solution.profile import profile
    pytest._db = profile.db_client
    pytest._client = TestClient(app).__enter__()


def pytest_unconfigure():
    """
    called before test process is exited.
    """

    try:
        pytest._db.session.close_all()
        pytest._db.engine.dispose()
        pytest._db.engine = None
        pytest._db.session = None
        pytest._client.__exit__()
        import gc
        gc.collect()
    except Exception as e:
        print(e)
