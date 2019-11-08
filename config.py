import os
import sys
sys.path.append('/data/project/dimastbkbot')

import replica


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SRC_DIR = 'src'
    SRC_PATH = os.path.join(BASE_DIR, SRC_DIR)

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/s52323__GKGN'.format(
                              replica.user,
                              replica.password,
                              replica.host
                              )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
