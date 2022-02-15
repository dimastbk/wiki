import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Optional
from urllib.parse import quote, unquote

from flask import Blueprint, render_template, request, url_for
from sqlalchemy import and_, func, select

from apps.cache import cache, make_cache_key
from apps.db import session

from .models import Namespace, Page, PageTemplate, Param, Template

template_params_bp = Blueprint("template_params", __name__)


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Form:
    template: str
    order_by: list[str]
    limit: int
    page: int
    page_count: int = 1


def make_pagination(form: Form) -> list:
    """Создаём пагинацию (ссылки на страницы вида 1,...,4,5,6,7,8,...,10)"""
    pagination = []

    DISABLED = {"value": "...", "disabled": True}

    page_min = max(form.page - 2, 1)
    page_max = min(page_min + 4, form.page_count)
    for page in range(page_min, page_max + 1):
        pagination.append(
            {
                "value": page,
                "link": url_for(
                    "template_params.index",
                    template=form.template,
                    order_by=",".join(form.order_by),
                    page=page,
                    limit=form.limit,
                ),
                "active": page == form.page,
            }
        )

    if form.page > 4:
        pagination.insert(0, DISABLED)

    if form.page > 3:
        pagination.insert(
            0,
            {
                "value": 1,
                "link": url_for(
                    "template_params.index",
                    template=form.template,
                    order_by=",".join(form.order_by),
                    page=1,
                    limit=form.limit,
                ),
                "active": 1 == form.page,
            },
        )

    if form.page < form.page_count - 3:
        pagination.append(DISABLED)

    if form.page < form.page_count - 2:
        pagination.append(
            {
                "value": form.page_count,
                "link": url_for(
                    "template_params.index",
                    template=form.template,
                    order_by=",".join(form.order_by),
                    page=form.page_count,
                    limit=form.limit,
                ),
                "active": form.page_count == form.page,
            }
        )

    return pagination


def make_headers(form: Form, all_params: list) -> list:
    """Создание заголовка таблицы с ссылками для сортировки."""
    table_header = []
    for param in all_params:
        order_by_list = form.order_by.copy()
        for order in order_by_list:
            if order == f"-{param}":
                order_by_list.remove(order)
                order_icon = "↑"
                break
            elif order == param:
                order_by_list.insert(order_by_list.index(order), f"-{param}")
                order_by_list.remove(order)
                order_icon = "↓"
                break
        else:
            order_by_list.append(param)
            order_icon = ""

        table_header.append(
            {
                "name": param,
                "link": url_for(
                    "template_params.index",
                    template=form.template,
                    order_by=",".join(map(quote, order_by_list)),
                    page=form.page,
                ),
                "icon": order_icon,
            }
        )
    return table_header


@template_params_bp.route("/")
def index():
    form = Form(
        template=(
            request.values.get("template", "")[:1].upper()
            + request.values.get("template", "")[1:]
        ),
        order_by=list(map(unquote, request.values.get("order_by", "").split(",")))
        if request.values.get("order_by")
        else [],
        page=to_int(request.values.get("page"), 1),
        limit=min(to_int(request.values.get("limit"), 50), 500),
    )

    params_cache = cache.get(make_cache_key("template_params", form.template))
    if params_cache:
        all_params = json.loads(params_cache)
    else:
        query = (
            select(Param.name)
            .distinct(Param.name)
            .join(PageTemplate)
            .join(Template)
            .where(Template.title == form.template)
            .order_by(Param.name)
        )
        all_params = session.scalars(query).all()

        cache.set(
            make_cache_key("template_params", form.template),
            json.dumps(all_params),
            ex=timedelta(hours=24),
        )

    query = (
        select(PageTemplate)
        .join(Page)
        .join(Namespace)
        .join(Template)
        .where(Template.title == form.template)
    )

    for order in form.order_by:
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
            isouter=True,
        ).order_by(order_by_clause)

    # Переносим параметры сортировки в начало
    for order in reversed(form.order_by):
        order_plain = order.removeprefix("-")
        if order_plain in all_params:
            all_params.remove(order_plain)
            all_params.insert(0, order_plain)

    query = (
        query.limit(form.limit)
        .offset((form.page - 1) * form.limit)
        .order_by(Page.namespace_id, Page.title)
    )
    result: list[PageTemplate] = session.scalars(query).unique().all()

    for item in result:
        item_params = {p.name: p.value for p in item.params}
        item.flat_params = []
        for param in all_params:
            item.flat_params.append(item_params.get(param, "__NONE__"))

    count_cache: Optional[bytes] = cache.get(make_cache_key("count", form.template))
    if count_cache:
        count = count_cache.decode()
    else:
        query = (
            select(func.count())
            .select_from(PageTemplate)
            .join(Template)
            .where(Template.title == form.template)
        )
        count = session.scalar(query)
        cache.set(make_cache_key("count", form.template), count, ex=timedelta(hours=24))

    form.page_count = int(count) // form.limit + 1

    return render_template(
        "template_params/index.html",
        table_header=make_headers(form, all_params),
        pagination=make_pagination(form),
        result=result,
        len=len(result),
        count=count,
        form=form,
    )
