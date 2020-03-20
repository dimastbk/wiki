import geojson as mod_geo
import simplekml as mod_kml
from gpxpy import gpx as mod_gpx


def makekml(points, cat_name):
    kml = mod_kml.Kml(name=cat_name)

    for point in points:
        name = point[1].decode() if point[1] else point[0].decode()
        kml.newpoint(name=name, coords=[(point[4], point[3])], description=point_desc(point))

    return kml.kml()


def makegpx(points, cat_name):
    gpx = mod_gpx.GPX()

    for point in points:
        name = point[1].decode() if point[1] else point[0].decode()
        gpx.waypoints.append(mod_gpx.GPXWaypoint(point[3], point[4], name=name))

    return gpx.to_xml()


def makejson(points, cat_name):
    features = []

    for point in points:
        name = point[1].decode() if point[1] else point[0].decode()
        geo_point = mod_geo.Point((float(point[4]), float(point[3])))
        features.append(
            mod_geo.Feature(
                geometry=geo_point, properties={'name': name, 'title': point[0].decode()}
            )
        )

    feature_collection = mod_geo.FeatureCollection(features)

    return mod_geo.dumps(feature_collection)


def point_desc(point):
    return """<![CDATA[
        <b><a href="http://ru.wikipedia.org/wiki/{}">Статья в Википедии</a></b>
    ]]>""".format(
        point[0].decode()
    )
