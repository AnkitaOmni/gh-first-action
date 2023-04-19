-- * Author          :- Dishant & Ankita
-- * Created Date    :- 13/Feb/2023
-- * Updated Date    :- 13/Feb/2023
-- * Description     :- Rollover for Acuirer Transaction History on BECH_BACKUP DB
-- * Usage           :- mysql -u root -pOmni123* BECH_BACKUP < /home/compsan/GREENPROD/SqlFiles/RollOverAcquirerTxnHistTable.sql


-- * Switch Database
USE BECH_BACKUP;

-- * Create New Backup Table for Acuirer Transaction History on BECH_BACKUP DB
set @sql = concat('CREATE TABLE BECH_BACKUP.acquirerhistory_', (DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH),'%b%Y')), ' LIKE OMNICOMP_BECH_GREENPROD.transactionhistory');
prepare s from @sql;
execute s;

-- * Copy Last Month Trnx from Acuirer Transaction History Table To Acuirer Transaction History Backup Table on BECH_BACKUP DB
set @sql = concat('INSERT INTO BECH_BACKUP.acquirerhistory_', (DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH),'%b%Y')), ' SELECT * FROM OMNICOMP_BECH_GREENPROD.transactionhistory WHERE LocalTransactionDate LIKE "', DATE_FORMAT(NOW() - INTERVAL 1 MONTH,'%Y-%m-'),'%"');
prepare s from @sql;
execute s;

-- * Delete Last Month Trnx from Acuirer Transaction History Table on GREENPROD DB
set @sql = concat('DELETE FROM OMNICOMP_BECH_GREENPROD.transactionhistory WHERE LocalTransactionDate LIKE "', DATE_FORMAT(NOW() - INTERVAL 1 MONTH,'%Y-%m-'),'%"');
prepare s from @sql;
execute s;

