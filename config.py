import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SRC_DIR = 'src'
    SRC_PATH = os.path.join(BASE_DIR, SRC_DIR)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
