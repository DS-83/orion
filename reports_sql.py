import pyodbc
from datetime import datetime
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
def OrionReportAccessPoint(date_start, date_end, ap=0, event=0):
    if isinstance(date_start, str):
        date_start = dt(date_start)
        date_end = dt(date_end)
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
        	    TimeVal as 'Time', pLogData.Event as 'EventId', Events.Contents as 'EventName',\
        	    Hozorgan as 'UserId', pList.Name as 'LastName', pList.FirstName,\
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
    if not g:
        db = get_mssql_no_g()
    else:
        db = get_mssql()
    db.execute(query, (date_start, date_end))
    return db
