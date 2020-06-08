from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
    send_from_directory, current_app
)
from app.db import get_db
from app.reports_sql import (
    OrionReportAccessPoint, OrionQueryEvents, OrionQueryAccessPoints,
    UnpackData, OrionQueryPersons, OrionReportWalkwaysPerson
)
from app.auth import login_required
from app.xlsx_ import SaveReport


bp = Blueprint('reports', __name__, url_prefix='/reports')


# Reports index
@bp.route('/')
@login_required
def index():
    return render_template('reports/reports.html')

# Report "Access points"
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
        #  check time range
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


# Report "Person"
@bp.route('/person', defaults={'page': 'person.html'})
# Search person by Name
@bp.route('/person/<page>', methods=(['POST']))
@login_required
def person(page):
    # TabNumber Search
    if page == 'tn':
        tNum = request.form.get('TabNumber')  # type <class 'str'>
        if not tNum:
            flash('Field can not be blank')
            return render_template('reports/person.html')
        persons = UnpackData(OrionQueryPersons())
        result = []
        for person in persons[1:]:
            if tNum == person[4]:
                result.append(person)
        if result != []:
            result.insert(0, persons[0])
        return render_template('reports/person.html', result=result)

    # Name Search
    if page == 'name':
        lName = request.form.get('LastName')  # type <class 'str'>
        fName = request.form.get('FirstName') # type <class 'str'>
        if not lName:
            flash('LastName can not be blank')
            return render_template('reports/person.html', result=0)

        # Convert first char upper other lower
        lName = lName[0].upper() + lName[1:].lower()
        # Case: user put FirstName
        if fName:
            # Convert first char upper other lower
            fName = fName[0].upper() + fName[1:].lower()
            persons = UnpackData(OrionQueryPersons())
            result = []
            for person in persons[1:]:
                if lName == person[1]:
                    if fName == person[2]:
                        result.append(person)
        # Case: only LastName
        else:
            persons = UnpackData(OrionQueryPersons())
            result = []
            for person in persons[1:]:
                if lName == person[1]:
                    result.append(person)
        if result != []:
            result.insert(0, persons[0])
        return render_template('reports/person.html', result=result)

    # Report functon
    def report(action):
        personId = ", ".join(map(str, request.form.getlist('personId')))
        if personId == "":
            flash('Should select one or several names')
            return render_template('reports/person.html', result=0)
        date_start = request.form['date_start']
        time_start = request.form['time_start']
        date_end = request.form['date_end']
        time_end = request.form['time_end']
        #  check time range
        date_start = date_start.replace('-', '') + time_start.replace(':', '')
        date_end = date_end.replace('-', '') + time_end.replace(':', '')
        if int(date_end) - int(date_start) <= 0:
            flash('Не пытайся обмануть меня, кожаный ублюдок')
            return redirect(url_for('.person'))
        data = UnpackData(OrionReportWalkwaysPerson(date_start, date_end, personId))
        if action == 'display':
            return render_template('reports/generatedreport.html', data=data)
        if action == 'save':
            filename = SaveReport(date_start, date_end, data)
            folder =  current_app.config['DWNLD_FOLDER']
            return send_from_directory(folder, filename, as_attachment=True)

    # Report display
    if page == 'display' and request.form['submit'] == 'display':
        return report('display')

    # Save to file
    if page == 'display' and request.form['submit'] == 'save':
        return report('save')

    # Default route
    return render_template('reports/person.html', result=0)
