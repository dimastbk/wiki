import enum


class ExtEnum(str, enum.Enum):
    GPX = "gpx"
    KML = "kml"
    GEOJSON = "geojson"
    MAP = "map"
