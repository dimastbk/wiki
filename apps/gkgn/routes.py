from flask import render_template, request

from apps.gkgn import bp

from .models import Settlement


@bp.route('/')
def index_gkgn():
    result = ''
    length = ''
    if request.values:
        if 'id' in request.values and request.values['id']:
            result = Settlement.query.filter_by(gkgn_id=request.values['id'])
            length = result.count()

        elif 'name' in request.values and request.values['name']:
            result = Settlement.query.filter_by(name=request.values['name'])
            length = result.count()

        elif 'district' in request.values and request.values['district']:
            result = Settlement.query.filter_by(
                     district=request.values['district'])

            # Проверяем регион, потому что есть одноимённые районы
            if 'region' in request.values and request.values['region']:
                result = result.filter_by(region=request.values['region'])

            length = result.count()

        elif 'region' in request.values and request.values['region']:
            result = Settlement.query.filter_by(
                     region=request.values['region'])
            length = result.count()

    template = 'gkgn/result.html' if request.is_xhr else 'gkgn/index.html'

    return render_template(template, result=result, len=length)
