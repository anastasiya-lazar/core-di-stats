FROM python:3.9-buster as base
ARG PIP_EXTRA_INDEX_URL


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/

COPY requirements/requirements.txt /requirements.txt

RUN pip3 install --no-cache-dir -r /requirements.txt


FROM base as dev
ARG PIP_EXTRA_INDEX_URL

#Azure related libs
RUN apt-get update && apt-get install -y musl-dev libmariadb-dev && apt-get clean
COPY requirements/requirements.azure.txt /requirements.azure.txt
RUN pip3 install --no-cache-dir -r /requirements.azure.txt

COPY requirements/requirements.dev.txt /requirements.dev.txt
RUN pip3 install --no-cache-dir -r /requirements.dev.txt

CMD bash

FROM mysql:8.0.21 as mysql_migration


RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 467B942D3A79BD29
RUN apt-get update && apt install -y python3 python3-pip musl-dev libmariadb-dev  && apt-get clean
RUN pip3 install  sqlalchemy[asyncio]==1.4.31 mysqlclient==2.0.3 pymysql==1.0.2 alembic==1.7.1 asyncmy==0.2.3

RUN mkdir /migrations
WORKDIR /migrations
ENV DB_TYPE=MYSQL

COPY src/solution/sp/sql_base/migrations /migrations


ENTRYPOINT ["bash","./migrate_db.sh"]


FROM mariadb:10.3.32 as mariadb_migration

RUN apt-get update && apt install -y python3 python3-pip musl-dev libmariadb-dev  && apt-get clean
RUN pip3 install sqlalchemy[asyncio]==1.4.31 mysqlclient==2.0.3 pymysql==1.0.2 alembic==1.7.1 mariadb==1.0.9 asyncmy==0.2.3

RUN mkdir /migrations
WORKDIR /migrations
ENV DB_TYPE=MARIADB

COPY src/solution/sp/sql_base/migrations /migrations

ENTRYPOINT ["bash","./migrate_db.sh"]

FROM base as azure_service
ARG PIP_EXTRA_INDEX_URL

#Azure related libs
RUN apt-get update && apt-get install -y musl-dev libmariadb-dev && apt-get clean
COPY requirements/requirements.azure.txt /requirements.azure.txt
RUN pip3 install --no-cache-dir -r /requirements.azure.txt
RUN apt-get update && apt-get install -y vim

COPY src /usr/src/app

ENTRYPOINT ["python", "./solution/channel/fastapi/main.py"]