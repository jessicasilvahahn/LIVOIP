CREATE TABLE target(
   cpf VARCHAR(12) PRIMARY KEY NOT NULL,
   uri VARCHAR(13) NOT NULL
   );

CREATE TABLE lea(
   id INTEGER PRIMARY KEY NOT NULL,
   user VARCHAR(50) NOT NULL,
   password VARCHAR(50) NOT NULL,
   email VARCHAR(100) NOT NULL,
   ip VARCHAR(100),
   port INTEGER,
   path_sftp VARCHAR(100)
   );

CREATE TABLE oficio(
   id INTEGER PRIMARY KEY,
   lea INTEGER NOT NULL,
   date_li DATE NOT NULL,
   FOREIGN KEY (lea) REFERENCES lea(id)
   );

CREATE TABLE li(
   id INTEGER PRIMARY KEY,
   target_id VARCHAR(12) NOT NULL,
   oficio INTEGER NOT NULL,
   flag VARCHAR(1) NOT NULL,
   FOREIGN KEY (target_id) REFERENCES target(cpf),
   FOREIGN KEY (oficio) REFERENCES oficio(id)
   );

CREATE TABLE cdr(
   id INTEGER PRIMARY KEY,
   answer_time TEXT NOT NULL,
   call_duration  INTEGER NOT NULL,
   end_call_time TEXT NOT NULL,
   call_start_time TEXT NOT NULL,
   source_uri VARCHAR(80) NOT NULL,
   destination_uri VARCHAR(80) NOT NULL,
   call_id VARCHAR(100) NOT NULL
   );


CREATE TABLE cdr_targets(
   id INTEGER PRIMARY KEY,
   target_id VARCHAR(12) NOT NULL,
   cdr_id INTEGER NOT NULL,
   alert INTEGER NOT NULL,
   FOREIGN KEY (target_id) REFERENCES target(cpf),
   FOREIGN KEY (cdr_id) REFERENCES cdr(id)
   );


INSERT INTO target VALUES('08974676982','jessica')
INSERT INTO target VALUES('08974676983','bob')

INSERT INTO cdr_target VALUES('08974676982','jessica')

INSERT INTO lea VALUES(NULL,'teste','teste123','lea.tcc.jessica@gmail.com')

INSERT INTO oficio VALUES(NULL,1,'2020-05-15')

INSERT INTO oficio VALUES(NULL,'08974676983',1,'A')

INSERT INTO cdr VALUES(NULL,'08974676983','08974676983','08974676983','08974676983','48988163769','48988320035','mBnmx7wN6m');

INSERT INTO cdr_targets VALUES(NULL,'092798173027',1,0);