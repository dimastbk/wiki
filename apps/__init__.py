from flask import Flask
from flask_migrate import Migrate
from sqlalchemy.pool import NullPool

from config import Config

from .engine import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, engine_options={"poolclass": NullPool})
migrate = Migrate(app, db)


from apps import views  # noqa: F401, E402
from apps.coord.views import coord_bp  # noqa: E402
from apps.gkgn.views import gkgn_bp  # noqa: E402

app.register_blueprint(coord_bp, url_prefix="/coord")
app.register_blueprint(gkgn_bp, url_prefix="/gkgn")

from apps.gkgn.models import *  # noqa: F401, F403, E402
