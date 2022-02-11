from typing import Any

from flask import Blueprint, render_template, request
from sqlalchemy import select

from apps import session

from .constants import LevelEnum
from .models import Object, Type

gkgn_bp = Blueprint("gkgn", __name__)


def to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@gkgn_bp.route("/")
def index_gkgn():

    result = []
    form = {}
    order_by = "name"

    if request.values.get("order_by") in ("gkgn_id", "name"):
        order_by = request.values["order_by"]

    form["gkgn_id"] = request.values.get("gkgn_id", "").lstrip("0")
    form["name"] = request.values.get("name", "")
    form["region_id"] = to_int(request.values.get("region_id"))
    form["district_id"] = to_int(request.values.get("district_id"))
    form["type_id"] = to_int(request.values.get("type_id"))

    query = (
        select(Object.id, Object.name)
        .where(Object.level == LevelEnum.REGION.value)
        .order_by(Object.name)
    )
    regions = session.execute(query).all()

    if form["region_id"]:
        query = (
            select(Object.id, Object.name)
            .where(
                Object.level == LevelEnum.DISTRICT.value,
                Object.region_id == form["region_id"],
            )
            .order_by(Object.name)
        )
        districts = session.execute(query).all()
    else:
        districts = []

    query = select(Type.id, Type.name).order_by(Type.name)
    types = session.execute(query).all()

    params = [getattr(Object, key) == value for key, value in form.items() if value]
    if params:
        query = select(Object).where(*params).order_by(getattr(Object, order_by))
        result = session.scalars(query).all()

    return render_template(
        "gkgn/index.html",
        regions=regions,
        districts=districts,
        types=types,
        result=result,
        len=len(result),
        form=form,
    )
