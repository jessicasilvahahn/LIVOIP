
CREATE TABLE target(
   id INTEGER PRIMARY KEY,
   target VARCHAR(100) NOT NULL
   );

CREATE TABLE interception(
   id INTEGER PRIMARY KEY,
   target INTEGER NOT NULL,
   flag VARCHAR(1) NOT NULL,
   FOREIGN KEY (target) REFERENCES target(id)
   );

INSERT INTO target (id,target,flag)
VALUES(1,'bob');

INSERT INTO interception (id,target,flag)
VALUES(1,1,'A');