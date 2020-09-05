DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  firstname TEXT,
  lastname TEXT,
  email TEXT,
  company TEXT,
  password TEXT NOT NULL,
  IsAdmin INT DEFAULT 0,
  status TEXT DEFAULT 'active',
  first_logon INT DEFAULT 1
);

DROP TABLE IF EXISTS admin;
CREATE TABLE admin (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  IsAdmin INT DEFAULT 1,
  status TEXT DEFAULT 'active',
  first_logon INT DEFAULT 1
);
-- Create Administrator
INSERT INTO admin (id, username, password)
VALUES (10000000000, 'Admin', 'pbkdf2:sha256:150000$byO3eeDs$8a8d305977f9905d9f86514658790eed25356e7b004e0c76fabc1a61b352a2d1');

DROP TABLE IF EXISTS saved_reports;
CREATE TABLE saved_reports (
  id INTEGER PRIMARY KEY,
  report_type TEXT NOT NULL,
  name TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  period TEXT NOT NULL,
  data TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

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

DROP TABLE IF EXISTS mssql;
CREATE TABLE mssql (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  server TEXT UNIQUE NOT NULL,
  database TEXT NOT NULL,
  username TEXT NOT NULL,
  password TEXT NOT NULL
);

DROP TABLE IF EXISTS smtp;
CREATE TABLE smtp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  server TEXT UNIQUE NOT NULL,
  port INT NOT NULL,
  ssl INT NOT NULL DEFAULT 0,
  username TEXT,
  password TEXT
);
