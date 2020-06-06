import pyodbc
from datetime import datetime
from app.db import get_mssql

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

# Report access point
def OrionReportAccessPoint(date_start, date_end, ap=0, event=0):
    sf = '%Y%m%d%H%M%S'
    date_start = datetime.strptime(date_start, sf)
    date_end = datetime.strptime(date_end, sf)
    if not ap:
        apId = []
        ap = OrionQueryAccessPoints()
        row = ap.fetchone()
        while row:
            apId.append(row[1])
            row = ap.fetchone()
        ap = ", ".join(map(str, apId))
    if not event:
        # Events ID from orion DB
        event = "25, 26, 27, 28, 29, 30, 31, 32, 33, 219, 34"
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
    db = get_mssql()
    db.execute(query, (date_start, date_end))
    return db
