from flask import Blueprint


bp = Blueprint('coord', __name__)

from apps.coord import routes  # noqa E402, F401
