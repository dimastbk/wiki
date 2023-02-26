from typing import Any

from pydantic import BaseModel, Field, validator


class Query(BaseModel):
    project: str = "ruwiki"
    template: str = ""
    order_by: list[str] = Field(default_factory=list)
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=500)
    with_redirects: bool = False

    @validator("project")
    def format_project(cls, v: str) -> str:
        return v.lower()

    @validator("template")
    def format_template(cls, v: str) -> str:
        return v[:1].upper() + v[1:]

    @validator("order_by", pre=True)
    def parse_order_by(cls, v: Any) -> list[str]:
        return [x.replace("%2C", ",") for x in str(v).split(",")]
