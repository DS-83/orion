from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
    send_from_directory, current_app, session
)
from app.db import get_db
from app.reports_sql import (
    OrionReportAccessPoint, OrionQueryEvents, OrionQueryAccessPoints,
    UnpackData, OrionQueryPersons, OrionReportWalkwaysPerson,
    OrionReportFirtsLast
)
from app.auth import login_required
from app.xlsx_ import SaveReport
from datetime import date, timedelta


bp = Blueprint('reports', __name__, url_prefix='/reports')

# Filter return monday or sunday of current week
@bp.app_template_filter()
def dt_tw(wday):
    # Monday
    today = date.today()
    mon = today - timedelta(days = date.isoweekday(today)-1)
    if wday == 'm':
        return mon
    # Sunday
    if wday == 's':
        sun = mon + timedelta(days = 6)
        return sun
    # Today
    if wday == 't':
        return today


# Reports index
@bp.route('/')
@login_required
def index():
    return render_template('reports/reports.html')

@bp.route('/accessp', defaults={'page': 'accessp.html'})
# Report "Access points"
@bp.route('/accessp/<page>', methods=(['POST']))
@login_required
def accessp(page):
    if request.method == 'POST':

        def report(action):

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
                flash('Не пытайся обмануть меня, кожаный ублюдок', 'warning')
                return redirect(url_for('reports.accessp'))

            data = UnpackData(OrionReportAccessPoint(date_start, date_end, ap, events))

            if action == 'display':
                return render_template('reports/generatedreport.html', data=data)
            if action == 'save':
                report_name = f'Access point: {ap}'
                filename = SaveReport(date_start, date_end, data, report_name)
                folder =  current_app.config['DWNLD_FOLDER']
                return send_from_directory(folder, filename, as_attachment=True)


        # Report display
        if page == 'display' and request.form['submit'] == 'display':
            return report('display')

        # Save to file
        if page == 'display' and request.form['submit'] == 'save':
            return report('save')

        # Save Report to DB
        if page == 'savereport':
            db = get_db()
            report = "Access point"
            name = request.form["reportname"]
            period = request.form["period"]
            events = ", ".join(map(str, request.form.getlist('events[]')))
            ap = ", ".join(map(str, request.form.getlist('ap[]')))
            data = {}
            data['ap'] = ap
            data['events'] = events
            data = str(data)
            try:
                db.execute("INSERT INTO saved_reports (report_type, name, user_id, period, data)\
                            VALUES (?,?,?,?,?);", (report, name, session['user_id'], period, data))
                db.commit()
                flash('Saved', 'success')
                return redirect(url_for('reports.savedreports'))
            except Exception as err:
                flash(err, 'warning')

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
            flash('Field can not be blank', 'warning')
            return render_template('reports/person.html')
        persons = UnpackData(OrionQueryPersons())
        result = []
        for person in persons[1:]:
            if tNum == person[4]:
                result.append(person)
        if result != []:
            result.insert(0, persons[0])
        return render_template('reports/person.html', result=result)

    # Department Search
    if page == 'department':
        dept = request.form.get('department')
        if not dept:
            flash('Field can not be blank')
            return render_template('reports/person.html')
        persons = UnpackData(OrionQueryPersons())
        result = []
        for person in persons[1:]:
            if dept == person[6]:
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
            flash('Should select one or several names', 'warning')
            return render_template('reports/person.html', result=0)
        date_start = request.form['date_start']
        time_start = request.form['time_start']
        date_end = request.form['date_end']
        time_end = request.form['time_end']
        #  check time range
        date_start = date_start.replace('-', '') + time_start.replace(':', '')
        date_end = date_end.replace('-', '') + time_end.replace(':', '')
        if int(date_end) - int(date_start) <= 0:
            flash('Не пытайся обмануть меня, кожаный ублюдок', 'warning')
            return redirect(url_for('.person'))
        data = UnpackData(OrionReportWalkwaysPerson(date_start, date_end, personId))
        if action == 'display':
            return render_template('reports/generatedreport.html', data=data)
        if action == 'save':
            report_name = 'Person walkways'
            filename = SaveReport(date_start, date_end, data, report_name)
            folder =  current_app.config['DWNLD_FOLDER']
            return send_from_directory(folder, filename, as_attachment=True)

    # Report display
    if page == 'display' and request.form['submit'] == 'display':
        return report('display')

    # Save to file
    if page == 'display' and request.form['submit'] == 'save':
        return report('save')

    # Save Report
    if page == 'savereport':
        db = get_db()
        report = "Person"
        name = request.form["reportname"]
        period = request.form["period"]
        data = ", ".join(map(str, request.form.getlist('personId')))
        try:
            db.execute("INSERT INTO saved_reports (report_type, name, user_id, period, data)\
                        VALUES (?,?,?,?,?);", (report, name, session['user_id'], period, data))
            db.commit()
            flash('Saved', 'success')
        except Exception as err:
            flash(err, 'warning')
        return render_template('reports/person.html', result=0)

    # Default route
    return render_template('reports/person.html', result=0)


# Report "First enter, last exit"
@bp.route('/firstlast', defaults={'page': 'firstlast.html'})
# Search person by Name
@bp.route('/firstlast/<page>', methods=(['POST']))
@login_required
def firstlast(page):
    # TabNumber Search
    if page == 'tn':
        tNum = request.form.get('TabNumber')  # type <class 'str'>
        if not tNum:
            flash('Field can not be blank', 'warning')
            return render_template('reports/firstlast.html')
        persons = UnpackData(OrionQueryPersons())
        result = []
        for person in persons[1:]:
            if tNum == person[4]:
                result.append(person)
        if result != []:
            result.insert(0, persons[0])
        return render_template('reports/firstlast.html', result=result)

    # Department Search
    if page == 'department':
        dept = request.form.get('department')
        if not dept:
            flash('Field can not be blank')
            return render_template('reports/firstlast.html')
        persons = UnpackData(OrionQueryPersons())
        result = []
        for person in persons[1:]:
            if dept == person[6]:
                result.append(person)
        if result != []:
            result.insert(0, persons[0])
        return render_template('reports/firstlast.html', result=result)

    # Name Search
    if page == 'name':
        lName = request.form.get('LastName')  # type <class 'str'>
        fName = request.form.get('FirstName') # type <class 'str'>
        if not lName:
            flash('LastName can not be blank')
            return render_template('reports/firstlast.html', result=0)

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
        return render_template('reports/firstlast.html', result=result)

    # Report functon
    def report(action):
        personId = request.form.getlist('personId')
        if personId == "":
            flash('Should select one or several names', 'warning')
            return render_template('reports/firstlast.html', result=0)
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        #  check time range
        date_start = date_start.replace('-', '') + "000000"
        date_end = date_end.replace('-', '') + "235959"
        if int(date_end) - int(date_start) <= 0:
            flash('Time range error', 'warning')
            return redirect(url_for('.firstlast'))
        data = OrionReportFirtsLast(date_start, date_end, personId)  # Data unpack inside OrionReportFirtsLast function
        if action == 'display':
            return render_template('reports/generatedreport.html', data=data)
        if action == 'save':
            report_name = 'First enter - last exit'
            filename = SaveReport(date_start, date_end, data, report_name)
            folder =  current_app.config['DWNLD_FOLDER']
            return send_from_directory(folder, filename, as_attachment=True)

    # Report display
    if page == 'display' and request.form['submit'] == 'display':
        return report('display')

    # Save to file
    if page == 'display' and request.form['submit'] == 'save':
        return report('save')

    # Save Report
    if page == 'savereport':
        db = get_db()
        report = "Person"
        name = request.form["reportname"]
        period = request.form["period"]
        data = ", ".join(map(str, request.form.getlist('personId')))
        try:
            db.execute("INSERT INTO saved_reports (report_type, name, user_id, period, data)\
                        VALUES (?,?,?,?,?);", (report, name, session['user_id'], period, data))
            db.commit()
            flash('Saved', 'success')
        except Exception as err:
            flash(err, 'warning')
        return render_template('reports/firstlast.html', result=0)

    # Default route
    return render_template('reports/firstlast.html', result=0)


# Saved reports
@bp.route('/savedreports')
@login_required
def savedreports():
    db = get_db()
    cursor = db.execute("SELECT id AS 'N', report_type AS 'Report type',\
                        name AS 'Report name', period AS 'Time interval',\
                        data FROM saved_reports WHERE user_id = ?", (session['user_id'],))
    row = cursor.fetchone()
    data = []
    if row:
        data.append(row.keys())
        while row:

            # For person
            if row['Report type'] == 'Person':
                persons_id = row['data'].split(',')
                data_orion = UnpackData(OrionQueryPersons())
                report_data = []
                for r in data_orion:
                    for person in persons_id:
                        if int(person) == r[0]:
                            report_data.append(r[1:])

            # For access point
            elif row['Report type'] == 'Access point':
                d = eval(row['data'])
                aps_id = d['ap'].split(',')
                data_orion = UnpackData(OrionQueryAccessPoints())
                report_data = []
                l = []
                for r in data_orion:
                    for ap in aps_id:
                        if int(ap) == r[1]:
                            l.append(r[0])
                report_data.append(l)
                events_id = d['events'].split(',')
                data_orion = UnpackData(OrionQueryEvents())
                l = []
                for r in data_orion:
                    for event in events_id:
                        if int(event) == r[0]:
                            l.append(r[1])
                report_data.append(l)

            l = list(row)
            l[4] = report_data
            data.append(l)

            row = cursor.fetchone()


    return render_template('reports/savedreports.html', data=data)

# Delete report
@bp.route('/savedreports', methods=['POST'])
@login_required
def delete():
    db = get_db()
    id = request.form['hidden_id']
    try:
        row = db.execute("SELECT celery_id\
                          FROM mail_task\
                          WHERE id = ?", (id,)
                          ).fetchone()

        # # Revoke celery task
        if row['celery_id']:
            celery_app.control.revoke(row['celery_id'])
            celery_app.control.terminate(row['celery_id'])

        # Delete report
        db.execute("DELETE FROM saved_reports WHERE id = ?", (id,))

        # Delete related mail tasks
        db.execute("DELETE FROM mail_task WHERE report_id = ?", (id))
        db.commit()
        flash('success', 'success')
    except Exception as err:
        flash(err, 'warning')

    return redirect(url_for('reports.savedreports'))
