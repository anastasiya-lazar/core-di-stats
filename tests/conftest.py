import pytest
import warnings

import config


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
