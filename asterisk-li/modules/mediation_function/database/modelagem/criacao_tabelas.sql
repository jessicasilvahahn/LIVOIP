CREATE TABLE operadora(
   cpf VARCHAR(45) PRIMARY KEY,
   nome VARCHAR(200),
   uri VARCHAR(100) NOT NULL,
   contrato INTEGER NOT NULL
   );

CREATE TABLE oficio(
   numero_oficio INTEGER PRIMARY KEY,
   autoridade VARCHAR(45),
   date_li DATE NOT NULL
   );

CREATE TABLE li_cadastro(
   liid INTEGER PRIMARY KEY,
   target VARCHAR(45) NOT NULL,
   uri VARCHAR(100) NOT NULL,
   numero_oficio INTEGER,
   FOREIGN KEY (numero_oficio) REFERENCES oficio(numero_oficio)
   );


CREATE TABLE iri(
   id INTEGER PRIMARY KEY,
   sip VARCHAR(600) NOT NULL,
   uri VARCHAR(100) NOT NULL,
   liid INTEGER,
   FOREIGN KEY (liid) REFERENCES li_cadastro(liid)
   );

CREATE TABLE cc(
   id INTEGER PRIMARY KEY,
   path_audio VARCHAR(100) NOT NULL,
   server VARCHAR(45) NOT NULL,
   liid INTEGER,
   FOREIGN KEY (liid) REFERENCES li_cadastro(liid)
   );