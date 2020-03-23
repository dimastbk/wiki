from flask import Response
from flask import current_app as app
from flask import render_template, request

import pymysql
from slugify import slugify
from werkzeug.datastructures import Headers

from apps.coord import bp

from .track_file import makegpx, makejson, makekml


def get_project(project):
    lang, pr = project.split('wiki')
    if not pr:
        pr = 'pedia'
    return '{}.wiki{}.org'.format(lang, pr)


@bp.route('/')
def index_coord():

    form = {}

    formats = {
        'kml': {'func': makekml, 'ext': 'kml', 'ct': 'application/vnd.google-earth.kml+xml'},
        'gpx': {'func': makegpx, 'ext': 'gpx', 'ct': 'application/gpx+xml'},
        'geojson': {'func': makejson, 'ext': 'geojson', 'ct': 'application/vnd.geo+json'},
    }

    wiki = request.values.get('wiki', 'ruwiki')
    category = request.values.get('category', '')
    recursive = request.values.get('recursive')
    not_primary = request.values.get('not_primary')
    ext = request.values.get('ext', 'map')

    for key in ('wiki', 'category', 'recursive', 'not_primary', 'ext'):
        form[key] = locals()[key]

    if not (category and ext in ('map', 'kml', 'gpx', 'geojson')):
        return render_template('coord/index.html', form=form)

    connection = pymysql.connect(
        app.config['DB_HOST'], app.config['DB_USER'], app.config['DB_PASS'], '{}_p'.format(wiki)
    )

    try:
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
                '' if not_primary else 'AND `gt_primary` = 1'
            )
            cursor.execute(sql, (category.replace(' ', '_'),))
            points = cursor.fetchall()
    finally:
        connection.close()

    if ext == 'map' or not points:
        return render_template(
            'coord/index.html',
            form=form,
            points=makejson(points, category),
            project=get_project(wiki),
        )

    if ext in formats.keys():
        filename = slugify(category)
        headers = Headers()
        headers.add(
            'Content-Disposition',
            'attachment',
            filename='{}.{}'.format(filename, formats[ext]['ext']),
        )
        response = Response(
            formats[ext]['func'](points, category, project=get_project(wiki)),
            headers=headers,
            content_type=formats[ext]['ct'],
        )

    return response
