import MySQLdb
from flask import Blueprint
from flask import current_app as app
from flask import render_template, request
from flask.wrappers import Response
from slugify import slugify
from werkzeug.datastructures import Headers

from .constants import ExtEnum
from .track_file import makegpx, makejson, makekml

coord_bp = Blueprint("coord", __name__)

FORMATS = (
    {"ext": ExtEnum.GPX.value, "label": "GPX", "active": True},
    {"ext": ExtEnum.KML.value, "label": "KML"},
    {"ext": ExtEnum.GEOJSON.value, "label": "GeoJSON"},
    {"ext": ExtEnum.MAP.value, "label": "На карте"},
)


def get_project(project):
    lang, pr = project.split("wiki")
    if not pr:
        pr = "pedia"
    return "{}.wiki{}.org".format(lang, pr)


@coord_bp.route("/")
def index_coord():

    form = {}

    formats = {
        ExtEnum.KML.value: {
            "func": makekml,
            "ext": "kml",
            "ct": "application/vnd.google-earth.kml+xml",
        },
        ExtEnum.GPX.value: {
            "func": makegpx,
            "ext": "gpx",
            "ct": "application/gpx+xml",
        },
        ExtEnum.GEOJSON.value: {
            "func": makejson,
            "ext": "geojson",
            "ct": "application/vnd.geo+json",
        },
    }

    wiki = request.values.get("wiki", "ruwiki")
    category = request.values.get("category", "")
    not_primary = request.values.get("not_primary")
    ext = request.values.get("ext", "map")

    form["wiki"] = wiki
    form["category"] = category
    form["not_primary"] = not_primary
    form["ext"] = ext

    if not (category and ext in ("map", "kml", "gpx", "geojson")):
        return render_template("coord.html", form=form, formats=FORMATS, regions={})

    connection: MySQLdb.Connection = MySQLdb.Connect(
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASS"],
        database="{}_p".format(wiki),
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
                      {};
                      """.format(
                "" if not_primary else "AND `gt_primary` = 1"
            )
            cursor.execute(sql, (category.replace(" ", "_"),))
            points = cursor.fetchall()

    if ext == ExtEnum.MAP.value or not points:
        return render_template(
            "coord.html",
            form=form,
            formats=FORMATS,
            points=makejson(points, category),
            project=get_project(wiki),
        )

    elif ext in formats.keys():
        filename = slugify(category)
        headers = Headers()
        headers.add(
            "Content-Disposition",
            "attachment",
            filename="{}.{}".format(filename, formats[ext]["ext"]),
        )
        response = Response(
            formats[ext]["func"](points, category, project=get_project(wiki)),
            headers=headers,
            content_type=formats[ext]["ct"],
        )
    else:
        response = render_template("coord.html", form=form, formats=FORMATS)

    return response
