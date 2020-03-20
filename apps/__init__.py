from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# blueprints ГКГН
from apps.gkgn import bp as gkgn_bp  # noqa E402

app.register_blueprint(gkgn_bp, url_prefix='/gkgn')

# blueprints GPX/KML export
from apps.coord import bp as coord_bp  # noqa E402

app.register_blueprint(coord_bp, url_prefix='/coord')


from apps import routes  # noqa E402, F401

# импортируем модели, чтобы подхватить менеджером миграций
from apps.gkgn.models import Settlement  # noqa F401
