import MySQLdb
from flask import Blueprint, render_template, request
from flask.wrappers import Response
from flask_pydantic import validate
from slugify import slugify
from werkzeug.datastructures import Headers

from config import config

from .constants import ExtEnum
from .serializers import FormatSettings, Point, Query
from .track_file import makegpx, makejson, makekml

coord_bp = Blueprint("coord", __name__)

FORMATS = (
    {"ext": ExtEnum.GPX, "label": "GPX"},
    {"ext": ExtEnum.KML, "label": "KML"},
    {"ext": ExtEnum.GEOJSON, "label": "GeoJSON"},
    {"ext": ExtEnum.MAP, "label": "На карте"},
)

FORMAT_SETTINGS = {
    ExtEnum.KML: FormatSettings(makekml, "kml", "application/vnd.google-earth.kml+xml"),
    ExtEnum.GPX: FormatSettings(makegpx, "gpx", "application/gpx+xml"),
    ExtEnum.GEOJSON: FormatSettings(makejson, "geojson", "application/vnd.geo+json"),
}


def get_project(project: str):
    lang, pr = project.split("wiki")
    if not pr:
        pr = "pedia"
    return f"{lang}.wiki{pr}.org"


@coord_bp.route("/")
@validate(query=Query)
def index_coord():
    query_params: Query = request.query_params

    if not query_params.category:
        return render_template(
            "coord.html", form=query_params.dict(), formats=FORMATS, regions={}
        )

    connection: MySQLdb.Connection = MySQLdb.Connect(
        host=config.DB_REPLICA_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASS,
        database=f"{query_params.wiki}_p",
    )

    with connection:
        cursor: MySQLdb.cursors.Cursor
        with connection.cursor() as cursor:
            sql = """SELECT `page`.`page_title`,
                            `geo_tags`.`gt_name`,
                            `geo_tags`.`gt_primary`,
                            `geo_tags`.`gt_lat`,
                            `geo_tags`.`gt_lon`
                    FROM `geo_tags`
                    JOIN `page` ON `geo_tags`.`gt_page_id` = `page`.`page_id`
                    WHERE `gt_page_id` IN
                        (SELECT `cl_from`
                         FROM `categorylinks`
                         WHERE `cl_to` = %s)
                      AND `page_namespace` = 0
                      AND `gt_globe` = "earth"
                      {};
                      """.format(
                "" if query_params.not_primary else "AND `gt_primary` = 1"
            )
            cursor.execute(sql, (query_params.category.replace(" ", "_"),))
            points = [Point(*el) for el in cursor.fetchall()]

    if query_params.ext == ExtEnum.MAP or not points:
        return render_template(
            "coord.html",
            form=query_params.dict(),
            formats=FORMATS,
            points=makejson(points, query_params.category),
            project=get_project(query_params.wiki),
        )

    elif query_params.ext in FORMAT_SETTINGS.keys():
        filename = slugify(query_params.category)
        headers = Headers()
        headers.add(
            "Content-Disposition",
            "attachment",
            filename=f"{filename}.{FORMAT_SETTINGS[query_params.ext].ext}",
        )
        response = Response(
            FORMAT_SETTINGS[query_params.ext].func(
                points, query_params.category, get_project(query_params.wiki)
            ),
            headers=headers,
            content_type=FORMAT_SETTINGS[query_params.ext].content_type,
        )
    else:
        response = render_template(
            "coord.html", form=query_params.dict(), formats=FORMATS
        )

    return response
