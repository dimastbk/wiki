import time

from flask import Flask, g
from flask_migrate import Migrate
from greenlet import getcurrent as _ident_func
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import Config

from .engine import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
migrate = Migrate(app, SQLAlchemy(app))

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine), scopefunc=_ident_func
)

cache = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

from apps import views  # noqa: F401, E402
from apps.coord.views import coord_bp  # noqa: E402
from apps.gkgn.views import gkgn_bp  # noqa: E402
from apps.template_params.views import template_params_bp  # noqa: E402

app.register_blueprint(coord_bp, url_prefix="/coord")
app.register_blueprint(gkgn_bp, url_prefix="/gkgn")
app.register_blueprint(template_params_bp, url_prefix="/template_params")

from apps.gkgn.models import *  # noqa: F401, F403, E402
from apps.template_params.models import *  # noqa: F401, F403, E402


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    diff = f"{time.time() - g.start:.2f}"
    if (
        (response.response)
        and (200 <= response.status_code < 300)
        and (response.content_type.startswith("text/html"))
    ):
        response.set_data(
            response.get_data().replace(
                b"__EXECUTION_TIME__", bytes(str(diff), "utf-8")
            )
        )
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
