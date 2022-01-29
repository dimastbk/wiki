from timeit import default_timer
from typing import Any

from flask import Blueprint, render_template, request

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
    t = default_timer()

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

    regions = tuple(
        Object.query.filter_by(level=LevelEnum.REGION.value)
        .order_by(Object.name)
        .values(Object.id, Object.name)
    )

    if form["region_id"]:
        districts = tuple(
            Object.query.filter_by(
                level=LevelEnum.DISTRICT.value, region_id=form["region_id"]
            )
            .order_by(Object.name)
            .values(Object.id, Object.name)
        )
    else:
        districts = []

    types = tuple(Type.query.order_by(Type.name).values(Type.id, Type.name))

    query = {key: value for key, value in form.items() if value}
    if query:
        result = Object.query.filter_by(**query).order_by(order_by).all()

    return render_template(
        "gkgn/index.html",
        regions=regions,
        districts=districts,
        types=types,
        result=result,
        len=len(result),
        time=default_timer() - t,
        form=form,
    )
