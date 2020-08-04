-- DROP TABLE IF EXISTS user;
--
-- CREATE TABLE user (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   username TEXT UNIQUE NOT NULL,
--   firstname TEXT,
--   lastname TEXT,
--   email TEXT,
--   company TEXT,
--   password TEXT NOT NULL,
--   IsAdmin INT DEFAULT 0,
--   status TEXT DEFAULT 'active'
-- );
--
-- CREATE TABLE admin (
--   id INTEGER PRIMARY KEY,
--   username TEXT UNIQUE NOT NULL,
--   password TEXT NOT NULL,
--   IsAdmin INT DEFAULT 1,
--   status TEXT DEFAULT 'active'
-- );
-- DROP TABLE IF EXISTS saved_reports;
-- CREATE TABLE saved_reports (
--   id INTEGER PRIMARY KEY,
--   report_type TEXT NOT NULL,
--   name TEXT NOT NULL,
--   user_id INTEGER NOT NULL,
--   period TEXT NOT NULL,
--   data TEXT NOT NULL,
--   FOREIGN KEY(user_id) REFERENCES user(id)
-- );

DROP TABLE IF EXISTS mail_task;
CREATE TABLE mail_task (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  report_id INTEGER NOT NULL,
  recipient TEXT NOT NULL,
  periodicity TEXT NOT NULL,
  weekday TEXT,
  date INTEGER,
  time TEXT NOT NULL,
  celery_id TEXT,
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(report_id) REFERENCES saved_reports(id)
);

-- CREATE TABLE smtp (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   server TEXT UNIQUE NOT NULL,
--   port INT NOT NULL,
--   ssl INT NOT NULL DEFAULT 0,
--   username TEXT,
--   password TEXT
-- );

-- DROP TABLE IF EXISTS eventTypes;
--
-- CREATE TABLE eventTypes (
--   id INTEGER PRIMARY KEY,
--   charid TEXT,
--   description TEXT,
--   category TEXT,
--   hexcolor TEXT,
--   isalarm INTEGER,
--   comments TEXT
-- );
--
-- CREATE TABLE Devices (
--   id INTEGER PRIMARY KEY,
--   address INTEGER,
--   devtype INTEGER,
--   name TEXT,
--   comportid INTEGER,
--   pkuid INTEGER
-- );
--
-- CREATE TABLE OrionUsers (
--   Id INTEGER PRIMARY KEY,
--   LastName TEXT,
--   FirstName TEXT,
--   MiddleName TEXT,
--   BirthDate TEXT,
--   Company TEXT,
--   Department TEXT,
--   Position TEXT,
--   CompanyId INTEGER,
--   DepartmentId INTEGER,
--   PositionId INTEGER,
--   TabNum TEXT,
--   Phone TEXT,
--   HomePhone TEXT,
--   Address TEXT,
--   Photo TEXT,
--   AccessLevelId INTEGER,
--   Status INTEGER,
--   ContactIdIndex INTEGER,
--   IsLockedDayCrossing INTEGER,
--   IsFreeShedule INTEGER,
--   ExternalId INTEGER,
--   IsInArchive INTEGER,
--   DocumentType INTEGER,
--   DocumentSerials TEXT,
--   DocumentNumber INTEGER,
--   DocumentIssueDate TEXT,
--   DocumentEndingDate TEXT,
--   DocumentIsser TEXT,
--   DocumentIsserCode INTEGER,
--   Sex INTEGER,
--   Birthplace TEXT,
--   EmailList TEXT,
--   ArchivingTimeStamp TEXT,
--   IsInBlackList INTEGER,
--   IsDismissed INTEGER,
--   BlackListComment TEXT,
--   ChangeTime TEXT,
--   Itn TEXT,
--   DismissedComment TEXT
-- );
