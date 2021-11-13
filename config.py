import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")

    DB_GKGN_HOST = os.getenv("DB_GKGN_HOST")
    DB_GKGN_NAME = os.getenv("DB_GKGN_NAME")

    # SQLALCHEMY_DATABASE_URI = "mysql://{}:{}@{}/{}".format(
    #     DB_USER, DB_PASS, DB_GKGN_HOST, DB_GKGN_NAME
    # )
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
