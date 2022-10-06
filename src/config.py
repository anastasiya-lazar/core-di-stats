import os
from enum import Enum


class CloudProvidersTypes(Enum):
    aws = 1
    azure = 2


CLOUD_PROVIDER_TYPE = CloudProvidersTypes[os.environ.get("CLOUD_PROVIDER_TYPE", "azure")]

LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", "DEBUG").lower()

REST_SERVER_PORT = int(os.environ.get("REST_SERVER_PORT", 6786))
REST_SERVER_HOST = os.environ.get("REST_SERVER_HOST", "0.0.0.0")

DEBUG = os.environ.get("DEBUG", False)

DB_SSL_PATH_CERT = os.environ.get("DB_SSL_PATH_CERT", "")
DB_ENDPOINT = os.environ.get("DB_ENDPOINT", "")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USERNAME = os.environ.get("DB_USERNAME", "")
DB_USER_HOST = os.environ.get("DB_USER_HOST", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "")

if DB_USER_HOST:
    DB_USERNAME += f"@{DB_USER_HOST}"


class DBType(Enum):
    mysql = "MYSQL"
    mariadb = "MARIADB"


DB_DRIVERS = {
    DBType.mysql: "mysql",
    DBType.mariadb: "mariadb",
}

DB_TYPE = DBType(os.environ.get("DB_TYPE", "").upper())
db_driver = DB_DRIVERS[DB_TYPE]

REQUEST_DB_CONNECTION_STRING = f"{db_driver}+asyncmy://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}"

AUTHENTICATOR_URL = os.environ.get("AUTHENTICATOR_URL")

# Keep the URL empty to use ConsoleSpanExporter or set http://otel-collector:4317 for local OTLPSpanExporter
OTEL_COLLECTOR_URL = os.environ.get('OTEL_COLLECTOR_URL')

OTEL_CONTEXT_NAME = b'OTEL-CONTEXT'
