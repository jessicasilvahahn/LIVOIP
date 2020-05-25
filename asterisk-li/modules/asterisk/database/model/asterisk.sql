
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

CREATE TABLE uri(
   id INTEGER PRIMARY KEY,
   uri VARCHAR(100) NOT NULL,
   cpf VARCHAR(12) NOT NULL
   );

INSERT INTO target (id,target,flag)
VALUES(1,'bob');

INSERT INTO interception (id,target,flag)
VALUES(1,1,'A');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'bob','08974676983');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'jessica','08974676982');