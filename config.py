import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")

    DB_GKGN_HOST = os.getenv("DB_GKGN_HOST")
    DB_GKGN_NAME = os.getenv("DB_GKGN_NAME")

    SQLALCHEMY_DATABASE_URI = (
        "mysql://{user}:{password}@{host}:{port}/{database}".format(
            user=DB_USER,
            password=DB_PASS,
            host=DB_GKGN_HOST,
            port=DB_PORT,
            database=DB_GKGN_NAME,
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
