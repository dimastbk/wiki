import geojson as mod_geo
import simplekml as mod_kml
from gpxpy import gpx as mod_gpx


def get_name(point):
    return point[1].decode() if point[1] else point[0].decode().replace("_", " ")


def makekml(points, cat_name, project):
    kml = mod_kml.Kml(name=cat_name)

    for point in points:
        kml.newpoint(
            name=get_name(point),
            coords=[(point[4], point[3])],
            description=point_desc(point, project),
        )

    return kml.kml()


def makegpx(points, cat_name, project=None):
    gpx = mod_gpx.GPX()

    for point in points:
        gpx.waypoints.append(
            mod_gpx.GPXWaypoint(point[3], point[4], name=get_name(point))
        )

    return gpx.to_xml()


def makejson(points, cat_name, project=None):
    features = []

    for point in points:
        geo_point = mod_geo.Point((float(point[4]), float(point[3])))
        features.append(
            mod_geo.Feature(
                geometry=geo_point,
                properties={"name": get_name(point), "title": point[0].decode()},
            )
        )

    feature_collection = mod_geo.FeatureCollection(features)

    return mod_geo.dumps(feature_collection)


def point_desc(point, project):
    return """<![CDATA[
        <b><a href="http://{}/wiki/{}">{}</a></b>
    ]]>""".format(
        project, point[0].decode(), point[0].decode().replace("_", " ")
    )
