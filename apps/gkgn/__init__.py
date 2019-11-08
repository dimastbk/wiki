from flask import Blueprint

bp = Blueprint('gkgn', __name__)

from apps.gkgn import routes
