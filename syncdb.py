from zeep import helpers
from app.db import get_db
from app.settings import client

# All funclions for sync DB in this LIST
SYNC_LIST = ['AddEventTypes', 'AddDevices', 'AddOrionUsers']


# Time count decorator
from functools import wraps
import time

def timing(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end-start))
        return return_value
    return wrapper



# Check connection to WSDL
def wsdlConn():
    if client.service.GetReplService() != True:
        return False
    return True

# Define Class Sync_obj
class Sync_obj:
    def __init__(self, success = 0):
        self.success = success
    # Get eventTypes
    @timing
    def AddEventTypes(self):
        eventTypes = client.service.GetEventTypes(0)
        eventTypes = list(eventTypes.OperationResult)

        # Insert DB
        db = get_db()
        # Clear old data
        db.execute(
            'DELETE FROM eventTypes'
            )

        for item in eventTypes:
            id = item.Id
            charid = item.CharId
            description = item.Description
            category = item.Category
            hexcolor = item.HexColor
            isalarm = item.IsAlarm
            comments = item.Comments
            try:
                db.execute(
                    'INSERT INTO eventTypes (id, charid, description, category, hexcolor, isalarm, comments) VALUES (?,?,?,?,?,?,?)',
                    (id, charid, description, category, hexcolor, isalarm, comments)
                )
                db.commit()
            except Exception as err:
                return err
        self.success = 1
        return True

    # Get Devices
    @timing
    def AddDevices(self):
        # Get devices
        devices = client.service.GetDevices(0)
        # Serialize to dict obj
        devices = helpers.serialize_object(devices.OperationResult)
        # Insert DB
        db = get_db()
        # Clear old data
        db.execute(
            'DELETE FROM Devices'
        )
        for device in devices:
            try:
                db.execute(
                    'INSERT INTO Devices (id, address, devtype, name, comportid, pkuid) VALUES (?,?,?,?,?,?)',
                    (device['Id'], device['Address'], device['DevType'], device['Name'], device['ComPortId'], device['PKUId'])
                )
                db.commit()
            except Exception as err:
                return err
        self.success = 1
        return True

    # Add Oroin Users to DB
    @timing
    def AddOrionUsers(self):
        # Get Users
        users = client.service.GetPersons(1, 0, 0, [], 0, 0, 0)
        # Serialize to dict obj
        users = helpers.serialize_object(users.OperationResult)
        # Insert DB
        db = get_db()
        # Clear old data
        db.execute(
            'DELETE FROM OrionUsers'
        )
        for user in users:
            try:
                db.execute(
                    'INSERT INTO OrionUsers (Id, LastName, FirstName, MiddleName, BirthDate, Company, Department, Position, CompanyId, DepartmentId, PositionId, TabNum, Phone, HomePhone, Address, Photo, AccessLevelId, Status, ContactIdIndex, IsLockedDayCrossing, IsFreeShedule, ExternalId, IsInArchive, DocumentType, DocumentSerials, DocumentNumber, DocumentIssueDate, DocumentEndingDate, DocumentIsser, DocumentIsserCode, Sex, Birthplace, EmailList, ArchivingTimeStamp, IsInBlackList, IsDismissed, BlackListComment, ChangeTime, Itn, DismissedComment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (user['Id'], user['LastName'], user['FirstName'], user['MiddleName'], user['BirthDate'], user['Company'], user['Department'], user['Position'], user['CompanyId'], user['DepartmentId'], user['PositionId'], user['TabNum'], user['Phone'], user['HomePhone'], user['Address'], user['Photo'], user['AccessLevelId'], user['Status'], user['ContactIdIndex'], user['IsLockedDayCrossing'], user['IsFreeShedule'], user['ExternalId'], user['IsInArchive'], user['DocumentType'], user['DocumentSerials'], user['DocumentNumber'], user['DocumentIssueDate'], user['DocumentEndingDate'], user['DocumentIsser'], user['DocumentIsserCode'], user['Sex'], user['Birthplace'], user['EmailList'], user['ArchivingTimeStamp'], user['IsInBlackList'], user['IsDismissed'], user['BlackListComment'], user['ChangeTime'], user['Itn'], user['DismissedComment'])
                )
                db.commit()
            except Exception as err:
                return err
        self.success = 1
        return True


# Complete sync DB
def RunSyncDb():
    # Check wsdl conn
    if not wsdlConn():
        return f"Error connection to {SOAP_URL}"
    eT_r = AddEventTypes()
    d_r = AddDevices()
    oU_r = AddOrionUsers()
    print(eT_r)
    print(d_r)
    print(oU_r)
    try:
        if eT_r * d_r * oU_r != True:
            return True
    except:
        return "Data synchronization error in syncdb.py module"
