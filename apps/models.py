from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

mapper_registry = registry()


class Model(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor
    __table__: sa.Table

    id = sa.Column(sa.BigInteger, primary_key=True)


class BaseModel(Model):
    __abstract__ = True

    create_at = sa.Column(
        sa.DateTime,
        default=datetime.now(),
        comment="Дата создания",
    )
    update_at = sa.Column(
        sa.DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        comment="Дата обновления",
    )
