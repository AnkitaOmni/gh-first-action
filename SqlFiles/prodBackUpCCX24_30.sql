-- * Switch Database
USE OMNICOMP_BECH_Dishant;

-- * Truncate Previous Data
TRUNCATE TABLE OMNICOMP_BECH_Dishant.estadoidpupdate;
TRUNCATE TABLE OMNICOMP_BECH_Dishant.chileidpupdate;
TRUNCATE TABLE OMNICOMP_BECH_Dishant.estado_report;
TRUNCATE TABLE OMNICOMP_BECH_Dishant.chile_report;
TRUNCATE TABLE OMNICOMP_BECH_Dishant.fulldaytransactionhistory;
TRUNCATE TABLE OMNICOMP_BECH_Dishant.fulldaytransactionretailerhistory;

-- * Insert Prod Data To Make Backup
INSERT INTO OMNICOMP_BECH_Dishant.estadoidpupdate
SELECT * FROM OMNICOMP_BECH_PROD.estadoidpupdate;

INSERT INTO OMNICOMP_BECH_Dishant.chileidpupdate
SELECT * FROM OMNICOMP_BECH_PROD.chileidpupdate;

INSERT INTO OMNICOMP_BECH_Dishant.estado_report
SELECT * FROM OMNICOMP_BECH_PROD.estado_report;

INSERT INTO OMNICOMP_BECH_Dishant.chile_report
SELECT * FROM OMNICOMP_BECH_PROD.chile_report;

INSERT INTO OMNICOMP_BECH_Dishant.fulldaytransactionhistory
SELECT * FROM OMNICOMP_BECH_PROD.fulldaytransactionhistory;

INSERT INTO OMNICOMP_BECH_Dishant.fulldaytransactionretailerhistory
SELECT * FROM OMNICOMP_BECH_PROD.fulldaytransactionretailerhistory;