from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from apps import views  # noqa: F401, E402
from apps.coord.views import coord_bp  # noqa: E402
from apps.gkgn.views import gkgn_bp  # noqa: E402

app.register_blueprint(coord_bp, url_prefix="/coord")
app.register_blueprint(gkgn_bp, url_prefix="/gkgn")

from apps.gkgn.models import *  # noqa: F401, F403, E402
from apps.oktmo.models import *  # noqa: F401, F403, E402
