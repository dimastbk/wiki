import csv
import json
from dataclasses import dataclass
from datetime import timedelta
from io import StringIO
from typing import Any, Optional

from flask import Blueprint, Response, render_template, request, url_for
from flask_pydantic import validate
from slugify import slugify
from sqlalchemy import and_, func, or_, select
from werkzeug.datastructures import Headers

from apps.cache import cache, make_cache_key
from apps.db import session_for_db

from .models import Namespace, Page, PageTemplate, Param, Template
from .serializers import FormatEnum, Query

template_params_bp = Blueprint("template_params", __name__)


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Form:
    project: str
    template: str
    order_by: list[str]
    limit: int
    page: int
    with_redirects: bool
    format: FormatEnum
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
                    with_redirects=form.with_redirects,
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
                    with_redirects=form.with_redirects,
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
                    with_redirects=form.with_redirects,
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
                    order_by=order_by_list,
                    page=form.page,
                ),
                "icon": order_icon,
            }
        )
    return table_header


@template_params_bp.route("/")
@validate(query=Query)
def index():
    query_params: Query = request.query_params
    form = Form(**query_params.dict())
    all_templates = []

    with session_for_db(query_params.project) as session:
        query = select(Template).where(Template.title == func.binary(form.template))
        template = session.scalars(query).one_or_none()

        if not template:
            return render_template(
                "template_params/index.html",
                table_header=[],
                pagination=[],
                result=[],
                len=0,
                count=0,
                form=form,
            )

        if form.with_redirects:
            query = (
                select(Template.id)
                .where(
                    or_(
                        Template.id == template.redirect_id,
                        Template.redirect_id == template.redirect_id,
                    )
                )
                .order_by(Template.redirect_id)
                .distinct()
            )
            all_templates_ids = session.scalars(query).all()
        else:
            all_templates_ids = [template.id]

        params_cache = cache.get(
            make_cache_key("template_params", template.id, form.with_redirects)
        )
        if params_cache:
            all_params: list[str] = json.loads(params_cache)
        else:
            query = (
                select(Param.name)
                .distinct(Param.name)
                .join(PageTemplate)
                .where(PageTemplate.template_id.in_(all_templates_ids))
                .order_by(Param.name)
            )
            all_params: list[str] = session.scalars(query).all()

            cache.set(
                make_cache_key("template_params", template.id, form.with_redirects),
                json.dumps(all_params),
                ex=timedelta(hours=24),
            )

        query = (
            select(PageTemplate)
            .join(Page)
            .join(Namespace)
            .where(PageTemplate.template_id.in_(all_templates_ids))
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
        result = session.scalars(query).unique().all()

        for item in result:
            item_params = {p.name: p.value for p in item.params}
            item.flat_params = []
            for param in all_params:
                item.flat_params.append(item_params.get(param, "_X_"))

        count_cache: Optional[bytes] = cache.get(
            make_cache_key("count", template.id, form.with_redirects)
        )
        if count_cache:
            count = count_cache.decode()
        else:
            query = (
                select(func.count())
                .select_from(PageTemplate)
                .where(PageTemplate.template_id.in_(all_templates_ids))
            )
            count = session.scalar(query)

            cache.set(
                make_cache_key("count", template.id, form.with_redirects),
                count,
                ex=timedelta(hours=24),
            )

        form.page_count = int(count) // form.limit + 1

    if form.format == FormatEnum.HTML:
        return render_template(
            "template_params/index.html",
            table_header=make_headers(form, all_params),
            pagination=make_pagination(form),
            result=result,
            len=len(result),
            count=count,
            form=form,
            redirects=all_templates,
        )
    else:
        filename = slugify(form.template)
        headers = Headers()
        headers.add("Content-Disposition", "attachment", filename=f"{filename}.csv")

        io = StringIO()

        writer = csv.writer(io)
        writer.writerow(["Статья"] + all_params)
        writer.writerows([[item.page.title] + item.flat_params for item in result])

        return Response(io.getvalue(), headers=headers, content_type="text/csv")
