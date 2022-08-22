#!/bin/sh

echo "Creating DB"

mysql -h$DB_ENDPOINT -u$DB_USERNAME -p$DB_PASSWORD --ssl-ca $DB_SSL_PATH_CERT -e \
  "CREATE DATABASE IF NOT EXISTS  ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;";

echo "Set PRIVILEGES";

mysql -h$DB_ENDPOINT -u$DB_USERNAME -p$DB_PASSWORD --ssl-ca $DB_SSL_PATH_CERT -e \
    "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USERNAME}'@'%' IDENTIFIED BY '${DB_PASSWORD}';";

mysql -h$DB_ENDPOINT -u$DB_USERNAME -p$DB_PASSWORD --ssl-ca $DB_SSL_PATH_CERT -e "FLUSH PRIVILEGES;";

echo "Start migrations"

alembic upgrade head
