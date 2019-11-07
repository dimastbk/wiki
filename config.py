import os


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SRC_DIR = 'src'
    SRC_PATH = os.path.join(BASE_DIR, SRC_DIR)
