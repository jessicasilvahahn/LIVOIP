
CREATE TABLE target(
   id INTEGER PRIMARY KEY,
   target INTEGER NOT NULL,
   FOREIGN KEY (target) REFERENCES uri(id)
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


CREATE TABLE iri(
   id INTEGER PRIMARY KEY,
   iri VARCHAR(500) NOT NULL,
   proxy VARCHAR(500),
   interception_id INTEGER NOT NULL,
   call_id VARCHAR(100) NOT NULL,
   FOREIGN KEY (interception_id) REFERENCES interception(id)
   );

CREATE TABLE cc(
   id INTEGER PRIMARY KEY,
   cc VARCHAR(500) NOT NULL,
   interception_id INTEGER NOT NULL,
   call_id VARCHAR(100) NOT NULL,
   FOREIGN KEY (interception_id) REFERENCES interception(id)
   );

INSERT INTO target (id,target,flag)
VALUES(1,'bob');

INSERT INTO interception (id,target,flag)
VALUES(1,1,'A');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'48988163769','092798173027');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'48999405246','08974676983');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'48991093349','79799452040');

INSERT INTO uri (id,uri,cpf)
VALUES(NULL,'jessica','08974676982');