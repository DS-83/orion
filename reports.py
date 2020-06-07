from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.db import get_db
from app.reports_sql import (
    OrionReportAccessPoint, OrionQueryEvents, OrionQueryAccessPoints,
    UnpackData
)
from app.auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')


# Reports index
@bp.route('/')
@login_required
def index():
    return render_template('reports/reports.html')

# Report Access points
@bp.route('/accessp', methods=('GET', 'POST'))
@login_required
def accessp():
    if request.method == 'POST':
        date_start = request.form['date_start']
        time_start = request.form['time_start']
        date_end = request.form['date_end']
        time_end = request.form['time_end']
        events = ", ".join(map(str, request.form.getlist('events[]')))
        ap = ", ".join(map(str, request.form.getlist('ap[]')))
        date_start = date_start.replace('-', '') + time_start.replace(':', '')
        date_end = date_end.replace('-', '') + time_end.replace(':', '')
        if int(date_end) - int(date_start) <= 0:
            flash('Не пытайся обмануть меня, кожаный ублюдок')
            return redirect(url_for('reports.accessp'))

        data = UnpackData(OrionReportAccessPoint(date_start, date_end, ap, events))
        return render_template('reports/generatedreport.html', data=data)

    events = UnpackData(OrionQueryEvents())
    access_p = UnpackData(OrionQueryAccessPoints())
    return render_template('reports/accessp.html', events=events, access_p=access_p)
