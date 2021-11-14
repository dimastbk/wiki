from datetime import datetime

from sqlalchemy.orm.query import Query

from . import db


class Model(db.Model):
    __abstract__ = True
    query: Query


class BaseModel(Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(
        db.DateTime,
        default=datetime.now(),
        comment="Дата создания",
    )
    update_at = db.Column(
        db.DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        comment="Дата обновления",
    )
