from flask import render_template, request

from apps.gkgn import bp

from .models import Settlement

@bp.route('/')
def index_gkgn():

    length = ''
    resp = ''
    form = {}

    for key in ('gkgn_id', 'name', 'district', 'region'):
        form[key] = request.values[key] if (key in request.values
                                            and request.values[key]) else ''

    if request.values:
        query = {key: value for key, value in form.items() if value != ''}
        resp = Settlement.query.filter_by(**query)
        length = resp.count()

    return render_template(
        'gkgn/index.html',
        result=resp or '',
        len=length or '',
        form=form,
    )
