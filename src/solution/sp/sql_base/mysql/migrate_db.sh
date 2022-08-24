#!/bin/sh

echo "Creating DB"

if [ "$DB_SSL_ENABLED" = "True" ]; then \
  mysql -h$DB_ENDPOINT -u$DB_USERNAME -p$DB_PASSWORD --ssl-ca=$DB_SSL_PATH_CERT -e \
  "CREATE DATABASE IF NOT EXISTS  ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;"; \
  echo "with SSL"; \
else \
  mysql -h$DB_ENDPOINT -u$DB_USERNAME -p$DB_PASSWORD -e \
  "CREATE DATABASE IF NOT EXISTS  ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;"; \
  echo "without SSL"; \
fi

echo "Start migrations"

alembic upgrade head