from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from pydantic import BaseModel, validator

from .constants import ExtEnum


class Query(BaseModel):
    wiki: str = "ruwiki"
    category: str = ""
    not_primary: bool = False
    ext: ExtEnum = ExtEnum.MAP

    @validator("ext", pre=True)
    def to_str(cls, v: str) -> ExtEnum:
        print(v)
        if v in {ExtEnum.GPX, ExtEnum.KML, ExtEnum.GEOJSON, ExtEnum.MAP}:
            return ExtEnum(v)
        return ExtEnum.MAP


@dataclass
class Point:
    page_title: str
    name: str
    primary: bool
    lat: Decimal
    lon: Decimal

    def __post_init__(self):
        self.page_title = self.page_title.decode()
        self.name = self.name.decode() if self.name else ""


@dataclass
class FormatSettings:
    func: Callable[[list[Point], str, str], str]
    ext: str
    content_type: str
