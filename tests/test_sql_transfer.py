from sql_transfer.sql_transfer import transfer
import pytest
import psycopg2
import docker
import logging
from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import pyodbc
from time import sleep
import os

# CONSTANTS ============================================================================================================
POSTGRES_IMAGE = os.getenv('POSTGRES_TEST_IMAGE')
POSTGRES_CONTAINER_NAME = 'postgres-database-01'
POSTGRES_PASSWORD = 'postgres'

SQL_SERVER_IMAGE = os.getenv('SQL_SERVER_IMAGE')
SQL_SERVER_CONTAINER_NAME = 'sql-server-database-01'
SQL_SERVER_PASSWORD = 'yourStrong(!)Password'

CARS_DF = pd.DataFrame({
    'make': ['Toyota', 'Subaru', 'Ford'],
    'model': ['RAV4', 'Crosstrek', 'Explorer'],
    'cyl': [4, 4, 6],
    'hp': [135, 120, 160]
})

# LOGGING CONFIGURATION ================================================================================================
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def kill_container(client, *args):
    try:
        c = client.containers.get(*args)
        c.remove(force=True)
    except docker.errors.NotFound:
        pass


@pytest.fixture(scope='module')
def postgres_db():
    client = docker.from_env()

    kill_container(client, POSTGRES_CONTAINER_NAME)
    log.info(f"Spinning up Postgres Docker image: {POSTGRES_IMAGE}")
    client.containers.run(POSTGRES_IMAGE,
                          name=POSTGRES_CONTAINER_NAME,
                          detach=True,
                          remove=True,
                          ports={5432: 5432},
                          environment={'POSTGRES_PASSWORD': POSTGRES_PASSWORD})
    yield f"postgresql+psycopg2://postgres:{POSTGRES_PASSWORD}@localhost:5432/postgres"
    kill_container(client, POSTGRES_CONTAINER_NAME)


@pytest.fixture(scope='module')
def sql_server_db():
    client = docker.from_env()

    kill_container(client, SQL_SERVER_CONTAINER_NAME)
    log.info(f"Spinning up SQL Server Docker image: {SQL_SERVER_IMAGE}")
    client.containers.run(SQL_SERVER_IMAGE,
                          name=SQL_SERVER_CONTAINER_NAME,
                          detach=True,
                          remove=True,
                          ports={1433: 1433},
                          environment={'SA_PASSWORD': SQL_SERVER_PASSWORD,
                                       'ACCEPT_EULA': 'Y'})
    sleep(10)
    yield f"mssql+pyodbc://sa:{SQL_SERVER_PASSWORD}@localhost:1433/master?driver=ODBC+Driver+17+for+SQL+Server"
    kill_container(client, SQL_SERVER_CONTAINER_NAME)


@pytest.fixture(scope='module')
def postgres_engine(postgres_db):
    log.info(postgres_db)
    eng = create_engine(postgres_db, pool_pre_ping=True)
    while (attempt := 0) < 10:
        try:
            eng.connect()
            break
        except sqlalchemy.exc.InterfaceError:
            attempt += 1
            sleep(1)
    eng.execute("CREATE SCHEMA test")
    return eng


@pytest.fixture(scope='module')
def sql_server_engine(sql_server_db):
    log.info(sql_server_db)
    eng = create_engine(sql_server_db, pool_pre_ping=True)
    while (attempt := 0) < 10:
        try:
            eng.connect()
            break
        except sqlalchemy.exc.InterfaceError:
            attempt += 1
            sleep(1)
    eng.execute("CREATE SCHEMA test")
    return eng


@pytest.fixture(scope='module')
def cars_db(sql_server_engine):
    connection = sql_server_engine.connect()
    trans = connection.begin()

    create_sql = """CREATE TABLE cars (
    make VARCHAR(16) not null,
    model VARCHAR(16) not null,
    cyl INT not null,
    hp INT not null
)"""
    insert_sql = """INSERT INTO cars VALUES 
('Toyota', 'RAV4', 4, 135),
('Subaru', 'Crosstrek', 4, 120),
('Ford', 'Explorer', 6, 160)"""

    connection.execute(create_sql)
    connection.execute(insert_sql)
    trans.commit()

    return sql_server_engine


@pytest.mark.timeout(60)
def test_postgres_fixture(postgres_db):
    """
    For each test_ def, when a fixture starting with 'dockerpy' is supplied, the plugin overrides pytest's setup and teardown.
    pytest_runtest_setup = will pull / start container(s).
    pytest_runtest_teardown = will kill container(s).
    """

    assert postgres_db is not None

    client = docker.from_env()
    container_found = False
    for container in client.containers.list():
        for tag in container.image.tags:
            if tag == POSTGRES_IMAGE:
                container_found = True

    assert container_found


@pytest.mark.timeout(60)
def test_sql_server_fixture(sql_server_db):
    assert sql_server_db is not None

    client = docker.from_env()
    container_found = False
    for container in client.containers.list():
        for tag in container.image.tags:
            if tag == SQL_SERVER_IMAGE:
                container_found = True

    assert container_found


def test_cars_db(cars_db):
    df = pd.read_sql("SELECT * FROM cars", cars_db.connect())
    assert df.equals(CARS_DF)


def test_transfer(postgres_db, sql_server_db, postgres_engine):
    transfer(sql_server_db, postgres_db, "SELECT * FROM cars", 'cars', 'replace')
    df = pd.read_sql("SELECT * FROM cars", postgres_engine)
    assert df.equals(CARS_DF)

    transfer(sql_server_db, postgres_db, "SELECT * FROM cars", 'cars', 'replace', schema='test')
    df = pd.read_sql("SELECT * FROM test.cars", postgres_engine)
    assert df.equals(CARS_DF)

    transfer(sql_server_db, postgres_db, "SELECT * FROM cars WHERE 0 = 1", 'empty_cars', 'replace')

    tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';",
                         postgres_engine)['table_name'].tolist()
    log.info(f"table variable: {tables}")
    log.info(f"Tables: {', '.join(tables)}")
    assert 'empty_cars' not in tables
    assert 'cars' in tables

