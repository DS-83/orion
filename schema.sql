DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  IsAdmin INT DEFAULT 0
);

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
