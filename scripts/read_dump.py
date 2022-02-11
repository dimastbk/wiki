import bz2
from timeit import default_timer
from xml.etree import cElementTree

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from wikitextparser import parse as wtp_parse

from config import Config

from apps.template_params.models import Namespace, Page, PageTemplate, Param, Template

DUMP_PATH = (
    "/public/dumps/public/ruwiki/latest/ruwiki-latest-pages-meta-current.xml.bz2"
)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session: Session = sessionmaker(bind=engine)()


namespaces: dict[str, int] = {}


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

templates: dict[str, int] = {}
template_objs = []
page_objs = []
page_template_objs = []
param_objs = []
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
            node = node + "\n" + line
            elem = cElementTree.fromstring(node)

            text = elem.find("revision").find("text").text
            title = elem.find("title").text
            if not text or not title:
                continue

            page = wtp_parse(text)
            if not page.templates:
                continue

            c += 1

            page_id = counter.page_id()
            page_objs.append(
                {
                    "id": page_id,
                    "title": title,
                    "wiki_id": elem.find("id").text,
                    "namespace_id": namespaces[elem.find("ns").text],
                }
            )
            for template in page.templates:
                template_name = template.name.strip()
                template_name = template_name[:1].title() + template_name[1:]
                template_id = templates.get(template_name)
                if not template_id:
                    template_id = counter.template_id()
                    template_objs.append(
                        {
                            "id": template_id,
                            "title": template_name,
                        }
                    )
                    templates[template_name] = template_id

                page_template_id = counter.page_template_id()
                page_template_objs.append(
                    {
                        "id": page_template_id,
                        "page_id": page_id,
                        "template_id": template_id,
                    }
                )

                for param in template.arguments:
                    param_objs.append(
                        {
                            "id": counter.param_id(),
                            "page_template_id": page_template_id,
                            "name": param.name.strip(),
                            "value": param.value.strip(),
                        }
                    )
            if c % 5000 == 0:
                print(default_timer() - t)
                print(f"{c} ({e})")
                with engine.connect() as conn:
                    conn.execute(Page.__table__.insert(), page_objs)
                    conn.execute(Template.__table__.insert(), template_objs)
                    conn.execute(PageTemplate.__table__.insert(), page_template_objs)
                    conn.execute(Param.__table__.insert(), param_objs)
                page_objs = []
                template_objs = []
                page_template_objs = []
                param_objs = []
                print(default_timer() - t)
        else:
            node = node + "\n" + line
