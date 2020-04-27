CREATE TABLE mediation_function(
   id INTEGER PRIMARY KEY,
   ip VARCHAR(100) NOT NULL
   );

CREATE TABLE target(
   id INTEGER PRIMARY KEY,
   target VARCHAR(100) NOT NULL,
   flag VARCHAR(1) NOT NULL
   );

CREATE TABLE interception(
   id INTEGER PRIMARY KEY,
   target INTEGER NOT NULL,
   mediation_function INTEGER NOT NULL,
   FOREIGN KEY (target) REFERENCES target(id),
   FOREIGN KEY (mediation_function) REFERENCES oficio(id)
   );

INSERT INTO mediation_function (id,ip)
VALUES(1,"localhost");

INSERT INTO target (id,target,flag)
VALUES(1,'bob','A');

INSERT INTO interception (id,target,mediation_function)
VALUES(1,1,1);