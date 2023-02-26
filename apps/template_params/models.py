from typing import cast

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from apps.models import Model

__all__ = ("Namespace", "Project", "Template", "Page", "Param", "PageTemplate")


class Namespace(Model):
    __tablename__ = "namespace"

    number = sa.Column(sa.SmallInteger)
    name = sa.Column(sa.String(191))

    pages = cast(list["Page"], relationship("Page", back_populates="namespace"))

    def __repr__(self):
        return f"<Namespace {self.name}>"


class Project(Model):
    __tablename__ = "project"

    name = sa.Column(sa.String(191))
    update_at = sa.Column(sa.DateTime)

    def __repr__(self):
        return f"<Project {self.name}>"


class BasePage(Model):
    __abstract__ = True

    title = sa.Column(sa.String(191), index=True)


class Template(BasePage):
    __tablename__ = "template"

    redirect_id = sa.Column(sa.ForeignKey("template.id"), index=True)
    # redirect = cast("Template", relationship("Template", back_populates="redirects"))
    # redirects = cast(list["Template"], relationship("Template", back_populates="redirect"))

    params = cast(
        list["PageTemplate"], relationship("PageTemplate", back_populates="template")
    )

    def __repr__(self):
        return f"<Template {self.title}>"


class Page(BasePage):
    __tablename__ = "page"

    wiki_id = sa.Column(sa.BigInteger)

    namespace_id = sa.Column(sa.ForeignKey(Namespace.id), index=True)
    namespace = cast(
        Namespace,
        relationship(Namespace, lazy="joined", back_populates="pages", uselist=False),
    )

    params = cast(
        list["PageTemplate"], relationship("PageTemplate", back_populates="page")
    )

    def __repr__(self):
        return f"<Page {self.title}>"


class PageTemplate(Model):
    __tablename__ = "page_template"

    template_id = sa.Column(sa.ForeignKey(Template.id), index=True)
    template = cast(
        Template,
        relationship(Template, lazy="joined", back_populates="params", uselist=False),
    )

    page_id = sa.Column(sa.ForeignKey(Page.id), index=True)
    page = cast(
        Page, relationship(Page, lazy="joined", back_populates="params", uselist=False)
    )

    params = cast(
        list["Param"],
        relationship("Param", lazy="joined", back_populates="page_template"),
    )

    def __repr__(self):
        return f"<PageTemplate {self.template_id}={self.page_id}>"


class Param(Model):
    __tablename__ = "param"

    page_template_id = sa.Column(sa.ForeignKey(PageTemplate.id), index=True)
    page_template = cast(
        PageTemplate,
        relationship(
            PageTemplate, lazy="joined", back_populates="params", uselist=False
        ),
    )

    name = sa.Column(sa.String(191), index=True)
    value = sa.Column(sa.String(1000))

    def __repr__(self):
        return f"<Param {self.name}={self.value}>"
