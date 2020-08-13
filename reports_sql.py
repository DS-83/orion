import pyodbc
from datetime import datetime, timedelta
from app.db import get_mssql, get_mssql_no_g
from flask import g

# Unpack Data
def UnpackData(data):
    result = []
    columns = [column[0] for column in data.description]
    result.append(columns)
    row = data.fetchone()
    while row:
        result.append(row)
        row = data.fetchone()
    return result

# Events
def OrionQueryEvents():
    db = get_mssql()
    db.execute("SELECT Event, Contents\
                FROM Events\
                WHERE Event IN (25,26,27,28,29,30,31,32,33,219,34)\
                ORDER BY Event;"
                )
    return db

# Access points
def OrionQueryAccessPoints():
    db = get_mssql()
    db.execute("SELECT Name, GIndex AS DoorIndex, ID\
                FROM AcessPoint\
                ORDER BY GIndex;"
                )
    return db

# Helper datetime
def dt(date):
    sf = '%Y%m%d%H%M%S'
    return datetime.strptime(date, sf)

# Report access point
def OrionReportAccessPoint(date_start, date_end, ap=None, event=None):
    if isinstance(date_start, str):
        date_start = dt(date_start)
        date_end = dt(date_end)
    else:
        date_start = date_start.replace(microsecond=0)
        date_end = date_end.replace(microsecond=0)

    if not ap:
        apId = []
        ap = OrionQueryAccessPoints()
        row = ap.fetchone()
        while row:
            apId.append(row[1])
            row = ap.fetchone()
        ap = ", ".join(map(str, apId))
    if not event:
        # Events ID in orion DB
        event = "25, 26, 27, 28, 29, 30, 31, 32, 33, 219, 34"
    # SQL string
    query = f"SELECT DoorIndex as 'DoorId', AcessPoint.Name as 'AcessPointName',\
        	    TimeVal as 'Time', Events.Contents as 'EventName',\
        	    pList.Name as 'LastName', pList.FirstName,\
        	    pList.MidName, pList.TabNumber, pPost.Name as 'Position',\
        	    pDivision.Name as 'Department'\
        FROM pLogData\
        LEFT JOIN Events ON pLogData.Event = Events.Event\
        LEFT JOIN pList ON pLogData.HozOrgan = pList.ID\
        LEFT JOIN pPost ON pList.Post = pPost.ID\
        LEFT JOIN AcessPoint ON pLogData.DoorIndex = AcessPoint.GIndex\
        LEFT JOIN pDivision ON pList.Section = pDivision.ID\
        WHERE TimeVal BETWEEN ? AND ?\
        	  AND DoorIndex IN ({ap})\
        	  AND pLogData.Event IN ({event})\
        	  AND tpIndex IN (8,12)\
        ORDER BY pLogData.DoorIndex, Plogdata.TimeVal;"

    if not g:
        db = get_mssql_no_g()
    else:
        db = get_mssql()

    db.execute(query, (date_start, date_end))
    return db

# All Persons in Orion DB
def OrionQueryPersons():
    db = get_mssql()
    db.execute("SELECT pList.ID, pList.Name as 'LastName', pList.FirstName,\
                	   pList.MidName, pList.TabNumber, PCompany.Name as 'Company',\
                	   pDivision.Name as 'Department',  pPost.Name as 'Position'\
                FROM pList\
                LEFT JOIN PPost ON PPost.ID = pList.Post\
                LEFT JOIN pDivision ON pList.Section = pDivision.ID\
                LEFT JOIN PCompany ON PCompany.ID = pList.Company\
                ORDER BY pList.Name;"
                )
    return db

# Report "walkways of persons"
def OrionReportWalkwaysPerson(date_start, date_end, persons):
    query = f"SELECT pList.Name as 'LastName', pList.FirstName,\
            	     pList.MidName, pList.TabNumber, PCompany.Name as 'Company',\
                	 pDivision.Name as 'Department',  pPost.Name as 'Position',\
                	 Plogdata.TimeVal as Time, pLogData.Remark as 'Direction',\
                     AccessZone.Name as 'ZoneName',\
                	 Events.Contents + DBO.AddState(tpRzdIndex) as 'Events'\
              FROM Plogdata\
              LEFT JOIN plist ON plogdata.hozorgan=plist.id\
              LEFT JOIN AccessZone ON pLogData.ZoneIndex = AccessZone.GIndex\
              LEFT JOIN Events ON Plogdata.Event = Events.Event\
              LEFT JOIN PCompany ON PCompany.ID = pList.Company\
              LEFT JOIN PPost ON PPost.ID = pList.Post\
              LEFT JOIN pDivision ON pList.Section = pDivision.ID\
              WHERE plogdata.hozorgan IN ({persons})\
              AND\
                    Plogdata.TimeVal BETWEEN ? AND ?\
              AND\
                    Plogdata.Event IN (26,28,29,32)\
              ORDER BY plist.Name, Plogdata.HozOrgan, Plogdata.TimeVal;"
    if isinstance(date_start, str):
        date_start = dt(date_start)
        date_end = dt(date_end)
    else:
        date_start = date_start.replace(microsecond=0)
        date_end = date_end.replace(microsecond=0)

    if not g:
        db = get_mssql_no_g()
    else:
        db = get_mssql()
    db.execute(query, (date_start, date_end))
    return db

# Report "first enter - last exit"
def OrionReportFirtsLast(date_start, date_end, persons):

    if isinstance(date_start, str):
        date_start = dt(date_start)
        date_end = dt(date_end)
    else:
        date_start = date_start.replace(microsecond=0)
        date_end = date_end.replace(microsecond=0)

    if not g:
        db = get_mssql_no_g()
    else:
        db = get_mssql()

    result = []

    for index, person in enumerate(persons):
        # Date Generator
        for n in range(int((date_end - date_start).days) + 1):
            date_start_new = date_start + timedelta(n)
            date_end_new = date_start_new.replace(hour=23, minute=59, second=59)
            query = f"SELECT * FROM (SELECT TOP 1 pList.Name as 'LastName', pList.FirstName,\
                                	   pList.MidName, pList.TabNumber, PCompany.Name as 'Company',\
                                	   pDivision.Name as 'Department',  pPost.Name as 'Position',\
                                	   Plogdata.TimeVal as 'Time', pLogData.Remark as 'Direction', AccessZone.Name as 'ZoneName',\
                                	   Events.Contents + DBO.AddState(tpRzdIndex)as 'Events'\
                                     FROM Plogdata\
                                     LEFT JOIN plist ON (plogdata.hozorgan=plist.id)\
                                     LEFT JOIN  AccessZone ON  (pLogData.ZoneIndex = AccessZone.GIndex)\
                                     LEFT JOIN Events ON Plogdata.Event = Events.Event\
                                     LEFT JOIN PCompany ON PCompany.ID = pList.Company\
                                     LEFT JOIN PPost ON PPost.ID = pList.Post\
                                     LEFT JOIN pDivision ON pList.Section = pDivision.ID\
                                     LEFT JOIN pmark ON (plogdata.ZReserv=pmark.id)\
                                     WHERE plogdata.hozorgan IN ({person})\
                                     AND\
                                        Plogdata.TimeVal BETWEEN ? AND ?\
                                     AND\
                        	            Plogdata.Event IN (28)\
                                     ORDER BY Plogdata.TimeVal ASC) as a\
                    UNION\
                    SELECT * FROM (SELECT TOP 1 pList.Name as 'LastName', pList.FirstName,\
                                	   pList.MidName, pList.TabNumber, PCompany.Name as 'Company',\
                                	   pDivision.Name as 'Department',  pPost.Name as 'Position',\
                                	   Plogdata.TimeVal as 'Time', pLogData.Remark as 'Direction', AccessZone.Name as 'ZoneName',\
                                	   Events.Contents + DBO.AddState(tpRzdIndex)as 'Events'\
                                    FROM Plogdata\
                                    LEFT JOIN plist ON (plogdata.hozorgan=plist.id)\
                                    LEFT JOIN  AccessZone ON  (pLogData.ZoneIndex = AccessZone.GIndex)\
                                    LEFT JOIN Events ON Plogdata.Event = Events.Event\
                                    LEFT JOIN PCompany ON PCompany.ID = pList.Company\
                                    LEFT JOIN PPost ON PPost.ID = pList.Post\
                                    LEFT JOIN pDivision ON pList.Section = pDivision.ID\
                                    LEFT JOIN pmark ON (plogdata.ZReserv=pmark.id)\
                                    WHERE plogdata.hozorgan IN ({person})\
                                    AND\
                                    	Plogdata.TimeVal BETWEEN ? AND ?\
                                    AND\
                                    	Plogdata.Event IN (28)\
                                    ORDER BY Plogdata.TimeVal DESC) as b"
            print(date_start_new, date_end_new)
            db.execute(query, (date_start_new, date_end_new, date_start_new, date_end_new))
            #Unpack data and append to result
            row = db.fetchone()
            while row:
                result.append(row)
                row = db.fetchone()
    if db.description:
        columns = [column[0] for column in db.description]
        result.insert(0, columns)

    return result


def OrionQueryDashboard(date_start, date_end):

    query = f"SELECT Events.Contents as 'EventName',\
                     COUNT(pLogData.Event) as 'Count'\
	          FROM pLogData\
              LEFT JOIN Events ON pLogData.Event = Events.Event\
              WHERE TimeVal BETWEEN ?  AND ?\
	          AND pLogData.Event IN (26, 27, 29, 34)\
	          AND tpIndex IN (8,12)\
              GROUP BY pLogData.Event, Events.Contents"

    db = get_mssql()
    db.execute(query, (date_start, date_end))
    return db

def OrionReportViolations(date_start, date_end, ap=None):

    if not ap:
        apId = []
        ap = OrionQueryAccessPoints()
        row = ap.fetchone()
        while row:
            apId.append(row[1])
            row = ap.fetchone()
        ap = ", ".join(map(str, apId))


    query = f"SELECT DoorIndex as 'DoorId', AcessPoint.Name as 'AcessPointName',\
                     Events.Contents as 'EventName', pMark.OwnerName,\
                     pLogData.TimeVal as Time, pLogData.Remark as 'AccessPoint',\
                     Events.Comment\
	          FROM pLogData\
              LEFT JOIN Events ON pLogData.Event = Events.Event\
              LEFT JOIN pMark on plogdata.ZReserv = pMark.id\
              LEFT JOIN AcessPoint ON pLogData.DoorIndex = AcessPoint.GIndex\
              WHERE TimeVal BETWEEN ?  AND ?\
              AND DoorIndex IN ({ap})\
	          AND pLogData.Event IN (26, 27, 29, 34)\
              AND tpIndex IN (8,12)\
              ORDER BY DoorIndex, Plogdata.TimeVal;"

    if isinstance(date_start, str):
        date_start = dt(date_start)
        date_end = dt(date_end)
    else:
        date_start = date_start.replace(microsecond=0)
        date_end = date_end.replace(microsecond=0)

    if not g:
        db = get_mssql_no_g()
    else:
        db = get_mssql()

    db.execute(query, (date_start, date_end))
    return db
