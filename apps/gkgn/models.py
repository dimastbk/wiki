from typing import List, cast

from sqlalchemy.orm import relationship

from apps import db
from apps.engine import BaseModel, Model

__all__ = ("Settlement", "ATE", "Type", "Object")


class Settlement(Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    okato_name = db.Column(db.String(256))
    oktmo_name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))
    district = db.Column(db.String(256))
    c_lat = db.Column(db.Float(precision=6))
    c_lon = db.Column(db.Float(precision=6))
    okato = db.Column(db.String(11))
    oktmo = db.Column(db.String(11))
    oktmo_up = db.Column(db.String(11))

    def __repr__(self):
        return "<Settlement {}>".format(self.name)


class ATE(Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    okato_name = db.Column(db.String(256))
    oktmo_name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))
    okato = db.Column(db.String(11))
    oktmo = db.Column(db.String(11))
    oktmo_up = db.Column(db.String(11))

    def __repr__(self):
        return "<ATE {}>".format(self.name)


class Type(BaseModel):
    __tablename__ = "gkgn_type"

    name = db.Column(db.String(255), comment="Тип")

    objects = cast(List["Object"], relationship("Object", back_populates="type"))


class Object(BaseModel):
    __tablename__ = "gkgn_object"

    gkgn_id = db.Column(db.String(8), comment="Код ГКГН", index=True)
    name = db.Column(db.String(255), comment="Название", index=True)

    type_id = db.Column(db.ForeignKey(Type.id), comment="Тип")
    type = cast(
        Type, relationship(Type, back_populates="objects", lazy="joined", uselist=False)
    )
    level = db.Column(db.String(10), comment="Уровень", index=True)

    lat = db.Column(db.Float(precision=6), comment="Широта")
    lon = db.Column(db.Float(precision=6), comment="Долгота")

    region_id = db.Column(db.ForeignKey("gkgn_object.id"), index=True)
    region = cast(
        "Object",
        relationship(
            "Object", lazy="joined", foreign_keys=[region_id], remote_side="Object.id"
        ),
    )

    district_id = db.Column(db.ForeignKey("gkgn_object.id"), index=True)
    district = cast(
        "Object",
        relationship("Object", foreign_keys=[district_id], remote_side="Object.id"),
    )
