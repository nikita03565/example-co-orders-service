import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig()
logger = logging.getLogger("exampleco.sqltime")
logger.setLevel(logging.DEBUG)

Base = declarative_base()

session_maker = sessionmaker()


def get_db_config():
    return {
        "DB_USER": "admin",
        "DB_PASSWORD": "password",
        "DB_HOST": "localhost",
        "DB_NAME": "db",
    }


def get_session_maker():
    try:
        engine = create_engine(
            "mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(**get_db_config()),
            isolation_level="READ COMMITTED",
        )
        engine.connect()
    except SQLAlchemyError as error:
        logger.error("Error connecting to DB")
        logger.error(error)
    else:
        session_maker.configure(bind=engine)
    return session_maker
