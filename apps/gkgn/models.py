from typing import cast

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from apps.models import BaseModel, Model

__all__ = ("Settlement", "ATE", "Type", "Object")


class Settlement(Model):
    __tablename__ = "settlement"

    gkgn_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(256))
    okato_name = sa.Column(sa.String(256))
    oktmo_name = sa.Column(sa.String(256))
    types = sa.Column(sa.String(100))
    region = sa.Column(sa.String(256))
    district = sa.Column(sa.String(256))
    c_lat = sa.Column(sa.Float(precision=6))
    c_lon = sa.Column(sa.Float(precision=6))
    okato = sa.Column(sa.String(11))
    oktmo = sa.Column(sa.String(11))
    oktmo_up = sa.Column(sa.String(11))

    def __repr__(self):
        return f"<Settlement {self.name}>"


class ATE(Model):
    __tablename__ = "ATE"

    gkgn_id = sa.Column(sa.Integer)
    name = sa.Column(sa.String(256))
    okato_name = sa.Column(sa.String(256))
    oktmo_name = sa.Column(sa.String(256))
    types = sa.Column(sa.String(100))
    region = sa.Column(sa.String(256))
    okato = sa.Column(sa.String(11))
    oktmo = sa.Column(sa.String(11))
    oktmo_up = sa.Column(sa.String(11))

    def __repr__(self):
        return f"<ATE {self.name}>"


class Type(BaseModel):
    __tablename__ = "gkgn_type"

    name = sa.Column(sa.String(191), comment="Тип")

    objects = cast(list["Object"], relationship("Object", back_populates="type"))


class Object(BaseModel):
    __tablename__ = "gkgn_object"

    gkgn_id = sa.Column(sa.String(8), comment="Код ГКГН", index=True)
    name = sa.Column(sa.String(191), comment="Название", index=True)

    type_id = sa.Column(sa.ForeignKey(Type.id), comment="Тип", index=True)
    type = cast(
        Type, relationship(Type, back_populates="objects", lazy="joined", uselist=False)
    )
    level = sa.Column(sa.String(10), comment="Уровень", index=True)

    lat = sa.Column(sa.Float(precision=6), comment="Широта")
    lon = sa.Column(sa.Float(precision=6), comment="Долгота")

    region_id = sa.Column(sa.ForeignKey("gkgn_object.id"), index=True)
    region = cast(
        "Object",
        relationship(
            "Object", lazy="joined", foreign_keys=[region_id], remote_side="Object.id"
        ),
    )

    district_id = sa.Column(sa.ForeignKey("gkgn_object.id"), index=True)
    district = cast(
        "Object",
        relationship("Object", foreign_keys=[district_id], remote_side="Object.id"),
    )
