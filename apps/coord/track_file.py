import geojson as mod_geo
import simplekml as mod_kml
from gpxpy import gpx as mod_gpx

from .serializers import Point


def get_name(point: Point):
    return point.name if point.name else point.page_title.replace("_", " ")


def makekml(points: list[Point], cat_name: str, project: str = ""):
    kml = mod_kml.Kml(name=cat_name)

    for point in points:
        kml.newpoint(
            name=get_name(point),
            coords=[(point.lon, point.lat)],
            description=point_desc(point, project),
        )

    return kml.kml()


def makegpx(points: list[Point], cat_name: str, project: str = ""):
    gpx = mod_gpx.GPX()
    gpx.name = cat_name

    for point in points:
        gpx.waypoints.append(
            mod_gpx.GPXWaypoint(
                float(point.lat), float(point.lon), name=get_name(point)
            )
        )

    return gpx.to_xml()


def makejson(points: list[Point], cat_name: str, project: str = ""):
    features = []

    for point in points:
        geo_point = mod_geo.Point((float(point.lon), float(point.lat)))
        features.append(
            mod_geo.Feature(
                geometry=geo_point,
                properties={"name": get_name(point), "title": point.page_title},
            )
        )

    feature_collection = mod_geo.FeatureCollection(features)

    return mod_geo.dumps(feature_collection)


def point_desc(point: Point, project: str):
    return """<![CDATA[
        <b><a href="http://{}/wiki/{}">{}</a></b>
    ]]>""".format(
        project, point.page_title, point.page_title.replace("_", " ")
    )
