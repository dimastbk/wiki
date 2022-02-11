from greenlet import getcurrent as _ident_func
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine), scopefunc=_ident_func
)
