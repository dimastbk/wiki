import csv
from datetime import datetime
from typing import cast

import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

from apps.gkgn.constants import LevelEnum
from config import config

engine = sa.create_engine(config.SQLALCHEMY_DATABASE_URI())
LocalSession = sessionmaker(bind=engine)
session: Session = LocalSession()

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    create_at = sa.Column(
        sa.DateTime,
        default=datetime.now(),
        server_default=sa.func.now(),
        comment="Дата создания",
    )
    update_at = sa.Column(
        sa.DateTime,
        default=datetime.now(),
        server_default=sa.func.now(),
        onupdate=datetime.now(),
        comment="Дата обновления",
    )


class Type(BaseModel):
    __tablename__ = "gkgn_type"

    name = sa.Column(sa.String(255), comment="Тип")

    objects = cast(list["Object"], relationship("Object", back_populates="type"))


class Object(BaseModel):
    __tablename__ = "gkgn_object"

    gkgn_id = sa.Column(sa.String(8), comment="Код ГКГН")
    name = sa.Column(sa.String(255), comment="Название")

    type_id = sa.Column(sa.ForeignKey(Type.id), comment="Тип")
    type = cast(
        Type, relationship(Type, back_populates="objects", lazy="joined", uselist=False)
    )
    level = sa.Column(sa.String(10), comment="Уровень")

    lat = sa.Column(sa.Float(precision=6), comment="Широта")
    lon = sa.Column(sa.Float(precision=6), comment="Долгота")

    region_id = sa.Column(sa.ForeignKey("gkgn_object.id"))
    region = cast(
        "Object",
        relationship(
            "Object", lazy="joined", foreign_keys=[region_id], remote_side="Object.id"
        ),
    )

    district_id = sa.Column(sa.ForeignKey("gkgn_object.id"))
    district = cast(
        "Object",
        relationship("Object", foreign_keys=[district_id], remote_side="Object.id"),
    )


with open("../data/goskatalog_Spisok_NP_i_ATE_na_vsu_RF_1.csv", encoding="cp1251") as f:
    reader = csv.DictReader(
        f.readlines(),
        fieldnames=("gkgn_id", "name", "type", "region", "district", "lat", "lon"),
        delimiter="\t",
    )

print("Чтение файла")

catalog = list(reader)
types = {row["type"] for row in catalog}
regions = [row for row in catalog if row["type"] == "субъект Российской Федерации"]
objects = [row for row in catalog if row["type"] != "субъект Российской Федерации"]
objects_district = {row["gkgn_id"]: row["district"] for row in objects}

print("Создание типов")
session.add_all(Type(name=name) for name in types)
session.commit()

query = select(Type)
result: list[Type] = session.execute(query).scalars().all()
types = {t.name: t.id for t in result}

print("Создание регионов")
region_objs = [
    Object(
        gkgn_id=row["gkgn_id"],
        name=row["name"].replace(
            "Кемеровская область - Кузбасс", "Кемеровская область"
        ),
        level=LevelEnum.REGION.value,
        type_id=types["субъект Российской Федерации"],
        lat=float(row["lat"].replace(",", ".")),
        lon=float(row["lon"].replace(",", ".")),
    )
    for row in regions
]
session.add_all(region_objs)
session.flush()

regions = {t.name: t.id for t in region_objs}

print("Создание объектов")
object_objs = [
    Object(
        gkgn_id=row["gkgn_id"],
        name=row["name"],
        level=LevelEnum.OBJECT.value,
        type_id=types[row["type"]],
        region_id=regions[row["region"]],
        lat=float(row["lat"].replace(",", ".")),
        lon=float(row["lon"].replace(",", ".")),
    )
    for row in objects
]
session.add_all(object_objs)
session.flush()

print("Заполнение районов")
districts = {}
for row in object_objs:
    districts.setdefault(row.region_id, {})
    districts[row.region_id][f"{row.name} {row.type.name}"] = row.id
    districts[row.region_id][f"{row.type.name} {row.name}"] = row.id

for row in object_objs:
    if row.gkgn_id in objects_district.keys():
        row.district_id = districts[row.region_id].get(objects_district[row.gkgn_id])

session.commit()

print("Заполнение районов")
squery = select(Object).with_only_columns(Object.district_id).distinct()
query = (
    update(Object).where(Object.id.in_(squery)).values(level=LevelEnum.DISTRICT.value)
)
engine.execute(query)
