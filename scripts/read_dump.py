import bz2
import os
import re
from datetime import date
from timeit import default_timer
from xml.etree import cElementTree

import sqlalchemy as sa
from wikitextparser import parse as wtp_parse

from config import config

from apps.models import Model
from apps.template_params.models import Namespace, Page, PageTemplate, Param, Template

DUMP_PATH = (
    "/public/dumps/public/ruwiki/latest/ruwiki-latest-pages-meta-current.xml.bz2"
)

class Counter:
    _page_id = 0
    _template_id = 0
    _param_id = 0
    _namespace_id = 0
    _page_template_id = 0

    def namespace_id(self) -> int:
        self._namespace_id += 1
        return self._namespace_id

    def page_id(self) -> int:
        self._page_id += 1
        return self._page_id

    def template_id(self) -> int:
        self._template_id += 1
        return self._template_id

    def page_template_id(self) -> int:
        self._page_template_id += 1
        return self._page_template_id

    def param_id(self) -> int:
        self._param_id += 1
        return self._param_id


counter = Counter()

project_search = re.search(
    r"/([a-z]+)-(\d{4})(\d{2})(\d{2})", os.path.realpath(DUMP_PATH)
)

assert project_search

update_date = date(
    int(project_search.group(2)),
    int(project_search.group(3)),
    int(project_search.group(4)),
)

engine = sa.create_engine(config.SQLALCHEMY_DATABASE_URI(project_search.group(1)))


# Очищаем все таблицы (код для MySQL)
Model.metadata.drop_all(
    engine,
    tables=[
        Namespace.__table__,
        Page.__table__,
        PageTemplate.__table__,
        Param.__table__,
        Template.__table__,
    ],
)
Model.metadata.create_all(
    engine,
    tables=[
        Namespace.__table__,
        Page.__table__,
        PageTemplate.__table__,
        Param.__table__,
        Template.__table__,
    ],
)


namespaces: dict[str, int] = {}
objs = []
with bz2.BZ2File(DUMP_PATH, "r") as file:
    while line := file.readline().decode():
        if line.strip().startswith("<namespace "):
            elem = cElementTree.fromstring(line.strip())
            id = counter.namespace_id()
            objs.append(
                {
                    "id": id,
                    "name": elem.text or "Основное",
                    "number": elem.get("key"),
                }
            )
            namespaces[elem.get("key")] = id
        elif line.strip() == "</namespaces>":
            with engine.connect() as conn:
                conn.execute(Namespace.__table__.insert(), objs)
            print("Namespaces created...")
            break

DUMP_RE = re.compile(
    (
        r"<title>(?P<title>.*?)</title>.*?"
        r"<ns>(?P<ns>.*?)</ns>.*?"
        r"<id>(?P<id>.*?)</id>.*?"
        r"(?:<redirect title=\"(?P<redirect>.*?)\" />.*?)?"
        r"<text[^>]+>(?P<text>.*?)</text>"
    ),
    re.DOTALL,
)

insert_page = str(
    Page.__table__.insert()
    .values(
        id=sa.bindparam("id"),
        title=sa.bindparam("title"),
        wiki_id=sa.bindparam("wiki_id"),
        namespace_id=sa.bindparam("namespace_id"),
    )
    .compile(dialect=engine.dialect)
)

insert_template = str(
    Template.__table__.insert()
    .values(
        id=sa.bindparam("id"),
        title=sa.bindparam("title"),
    )
    .compile(dialect=engine.dialect)
)

insert_page_temlplate = str(
    PageTemplate.__table__.insert()
    .values(
        id=sa.bindparam("id"),
        template_id=sa.bindparam("template_id"),
        page_id=sa.bindparam("page_id"),
    )
    .compile(dialect=engine.dialect)
)

insert_param = str(
    Param.__table__.insert()
    .values(
        id=sa.bindparam("id"),
        page_template_id=sa.bindparam("page_template_id"),
        name=sa.bindparam("name"),
        value=sa.bindparam("value"),
    )
    .compile(dialect=engine.dialect)
)

update_template_redirect = str(
    Template.__table__.update()
    .where(Template.__table__.c.id == sa.bindparam("id"))
    .values(redirect_id=sa.bindparam("redirect_id"))
    .compile(dialect=engine.dialect)
)

template_pks: dict[str, int] = {}
template_objs: list[tuple[int, str]] = []
page_objs: list[tuple[int, str, str, int]] = []
page_template_objs: list[tuple[int, int, int]] = []
param_objs: list[tuple[int, int, str, str]] = []
redirects: dict[str, str] = {}
redirect_pks: list[tuple[int, int]] = []


def save():
    print(default_timer() - t)
    print(f"{c} ({e})")

    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        cursor.executemany(insert_page, page_objs)
        cursor.executemany(insert_template, template_objs)
        cursor.executemany(insert_page_temlplate, page_template_objs)
        cursor.executemany(insert_param, param_objs)
        conn.connection.commit()

    page_objs.clear()
    template_objs.clear()
    page_template_objs.clear()
    param_objs.clear()

    print(default_timer() - t)


def normalize_template_name(title: str) -> str:
    return (
        (title[:1].upper() + title[1:])
        .strip()
        .removeprefix("Template:")
        .removeprefix("Шаблон:")
        .removeprefix("T:")
        .removeprefix("Ш:")
        .strip()
    )


with bz2.BZ2File(DUMP_PATH, "r") as file:
    c = 0
    e = 0
    t = default_timer()
    node = ""
    while line := file.readline().decode():
        if line.strip() == "<page>":
            node = line
        elif line.strip() == "</page>":
            e += 1

            matched = DUMP_RE.search(node)
            if not matched:
                continue

            text = matched.group("text")
            title = matched.group("title")
            wiki_id = matched.group("id")
            ns = matched.group("ns")
            redirect = matched.group("redirect")

            if redirect and ns == "10" and redirect.startswith("Шаблон:"):
                redirects[normalize_template_name(title)] = normalize_template_name(
                    redirect
                )

            parsed_page = wtp_parse(text)
            page_templates = parsed_page.templates

            if not page_templates:
                continue

            c += 1

            page_id = counter.page_id()
            page_objs.append((page_id, title, wiki_id, namespaces[ns]))
            for template in page_templates:
                template_name = normalize_template_name(template.name)

                template_id = template_pks.get(template_name)
                if not template_id:
                    template_id = counter.template_id()
                    template_objs.append((template_id, template_name))
                    template_pks[template_name] = template_id

                page_template_id = counter.page_template_id()
                page_template_objs.append((page_template_id, template_id, page_id))

                for param in template.arguments:
                    param_name = param.name.strip()
                    param_objs.append(
                        (
                            counter.param_id(),
                            page_template_id,
                            param_name if param_name else "__EMPTY__",
                            param.value.strip(),
                        )
                    )
            if c % 5000 == 0:
                save()
        else:
            node = node + line

save()

for k, v in redirects.items():
    if template_pks.get(k) and template_pks.get(v):
        redirect_pks.append((template_pks[v], template_pks[k]))

with engine.connect() as conn:
    cursor = conn.connection.cursor()
    cursor.executemany(update_template_redirect, redirect_pks)
    conn.connection.commit()
