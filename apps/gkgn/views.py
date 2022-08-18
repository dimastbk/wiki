import json
from dataclasses import dataclass
from typing import Any

from flask import Blueprint, render_template, request
from sqlalchemy import select

from apps.cache import cache, make_cache_key
from apps.db import session

from .constants import LevelEnum
from .models import Object, Type

gkgn_bp = Blueprint("gkgn", __name__)


def to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@dataclass
class Form:
    gkgn_id: str
    name: str
    region_id: int
    district_id: int
    type_id: int

    def sa_filters(self) -> list[Any]:
        result = []

        if self.name:
            if len(self.name) > 3:
                result.append(Object.name.like(f"{self.name}%"))
            else:
                result.append(Object.name == self.name)
        if self.gkgn_id:
            result.append(Object.gkgn_id == self.gkgn_id)
        if self.region_id:
            result.append(Object.region_id == self.region_id)
        if self.district_id:
            result.append(Object.district_id == self.district_id)
        if self.type_id:
            result.append(Object.type_id == self.type_id)
        return result

    def order_by(self) -> str:
        if request.values.get("order_by") in ("gkgn_id", "name"):
            return request.values["order_by"]
        else:
            return "name"

    def cache_key(self):
        return make_cache_key(
            "gkgn",
            "gkgn_id",
            self.gkgn_id,
            "name",
            self.name,
            "region_id",
            self.region_id,
            "district_id",
            self.district_id,
            "type_id",
            self.type_id,
        )


def get_types() -> list[Any]:
    types_cache_key = make_cache_key("gkgn", "types")

    if types_raw := cache.get(types_cache_key):
        return json.loads(types_raw)

    query = select(Type.id, Type.name).order_by(Type.name)
    types = [dict(obj._mapping) for obj in session.execute(query).all()]

    cache.set(types_cache_key, json.dumps(types), ex=60 * 60 * 24)

    return types


def get_regions() -> list[Any]:
    regions_cache_key = make_cache_key("gkgn", "regions")

    if regions_raw := cache.get(regions_cache_key):
        return json.loads(regions_raw)

    query = (
        select(Object.id, Object.name)
        .where(Object.level == LevelEnum.REGION.value)
        .order_by(Object.name)
    )
    regions = [dict(obj._mapping) for obj in session.execute(query).all()]

    cache.set(regions_cache_key, json.dumps(regions), ex=60 * 60 * 24)

    return regions


def get_districts(region_id: int) -> list[Any]:
    if not region_id:
        return []

    districts_cache_key = make_cache_key("gkgn", "districts", region_id)

    if districts_raw := cache.get(districts_cache_key):
        return json.loads(districts_raw)

    query = (
        select(Object.id, Object.name)
        .where(
            Object.level == LevelEnum.DISTRICT.value,
            Object.region_id == region_id,
        )
        .order_by(Object.name)
    )
    districts = [dict(obj._mapping) for obj in session.execute(query).all()]

    cache.set(districts_cache_key, json.dumps(districts), ex=60 * 60 * 24)

    return districts


@gkgn_bp.route("/")
def index_gkgn():
    form = Form(
        gkgn_id=request.values.get("gkgn_id", "").lstrip("0"),
        name=request.values.get("name", ""),
        region_id=to_int(request.values.get("region_id")),
        district_id=to_int(request.values.get("district_id")),
        type_id=to_int(request.values.get("type_id")),
    )

    result = []
    if filters := form.sa_filters():
        query = select(Object).where(*filters).order_by(form.order_by())
        result = session.scalars(query).all()

    return render_template(
        "gkgn/index.html",
        regions=get_regions(),
        districts=get_districts(form.region_id),
        types=get_types(),
        result=result,
        len=len(result),
        form=form,
    )
