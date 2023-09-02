from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, root_validator, validator


class FormatEnum(str, Enum):
    CSV = "csv"
    HTML = "html"


class Query(BaseModel):
    project: str = "ruwiki"
    template: str = ""
    order_by: list[str] = Field(default_factory=list)
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=500)
    with_redirects: bool = False
    format: FormatEnum = FormatEnum.HTML

    @validator("project")
    def format_project(cls, v: str) -> str:
        return v.lower()

    @validator("template")
    def format_template(cls, v: str) -> str:
        return v[:1].upper() + v[1:]

    @root_validator
    def update_limit(cls, values):
        if values["format"] == FormatEnum.CSV:
            values["limit"] = 5000
        return values
