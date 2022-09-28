import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy_utils import create_database, database_exists, drop_database
from exampleco.models.database import Base
from exampleco.models.database.services import Service
from exampleco.models.database.orders import Order, OrderItem


DB_ROOT_USER = "root"
DB_ROOT_PASSWORD = "rootpassword"
DB_HOST = "localhost"
TEST_DB_NAME = "db_test"
db_config = {
    "DB_USER": DB_ROOT_USER,
    "DB_PASSWORD": DB_ROOT_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_NAME": TEST_DB_NAME,
}
db_url = "mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
    **db_config
)


@pytest.fixture(scope="session")
def connection():
    if database_exists(db_url):
        drop_database(db_url)
    create_database(db_url)
    engine = create_engine(db_url, isolation_level="READ COMMITTED")
    return engine.connect()


@pytest.fixture(scope="session")
def setup_database(connection):
    Base.metadata.bind = connection
    Base.metadata.create_all()
    return


@pytest.fixture
def db_session(setup_database, connection):
    return scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
