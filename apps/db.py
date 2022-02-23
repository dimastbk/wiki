from contextlib import contextmanager

from greenlet import getcurrent as _ident_func
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI(), poolclass=NullPool)
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine), scopefunc=_ident_func
)


@contextmanager
def session_for_db(database: str):
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI(database), poolclass=NullPool)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
