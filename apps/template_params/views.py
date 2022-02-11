import json
from typing import Any

from flask import Blueprint, render_template, request
from sqlalchemy import and_, func, select

from apps import cache, session

from .models import Namespace, Page, PageTemplate, Param, Template

template_params_bp = Blueprint("template_params", __name__)


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@template_params_bp.route("/")
def index():

    form = {}

    form["template"] = request.values.get("template", "")
    form["order_by"] = request.values.get("order_by", "")
    page = to_int(request.values.get("page"), 1)

    query = (
        select(PageTemplate)
        .join(Page)
        .join(Namespace)
        .join(Template)
        .where(Template.title == form["template"], Namespace.number == "0")
        .limit(50)
        .offset((page - 1) * 50)
    )

    if form["order_by"]:
        for order in form["order_by"].split(","):
            param_alias = Param.__table__.alias()

            if order.startswith("-"):
                order_by_clause = param_alias.c.value.desc()
            else:
                order_by_clause = param_alias.c.value.asc()

            query = query.join(
                param_alias,
                and_(
                    param_alias.c.page_template_id == PageTemplate.id,
                    param_alias.c.name == order.removeprefix("-"),
                ),
            ).order_by(order_by_clause)

    result: list[PageTemplate] = session.scalars(query).unique().all()

    params_cache = cache.get(form["template"])
    if params_cache:
        all_params = json.loads(params_cache)
    else:
        query = (
            select(Param.name)
            .distinct(Param.name)
            .join(PageTemplate)
            .join(Template)
            .where(Template.title == form["template"])
            .order_by(Param.name)
        )
        all_params = session.scalars(query).all()

        cache.set(form["template"], json.dumps(all_params))

    for item in result:
        item_params = {p.name: p.value for p in item.params}
        item.flat_params = []
        for param in all_params:
            item.flat_params.append(item_params.get(param, ""))

    count_cache = cache.get(f'count:{form["template"]}')
    if count_cache:
        count = count_cache
    else:
        query = (
            select(func.count())
            .select_from(PageTemplate)
            .join(Page)
            .join(Namespace)
            .join(Template)
            .where(Template.title == form["template"], Namespace.number == "0")
        )
        count = session.scalar(query)
        cache.set(f'count:{form["template"]}', count)

    return render_template(
        "template_params/index.html",
        all_params=all_params,
        result=result,
        len=len(result),
        form=form,
    )