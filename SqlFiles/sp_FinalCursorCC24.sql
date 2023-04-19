DROP PROCEDURE IF EXISTS BancoEstadoReports;
DELIMITER $$  
CREATE PROCEDURE BancoEstadoReports()
BEGIN
    -- TRUNCATE TABLE estado;
    DECLARE iseretdata, RetId, EntId, IDP, Ruth, EmailId, BnkCd, MovTy, AcNo VARCHAR(20) DEFAULT "NAN";
    DECLARE is_done, Pur, RefRev, Ref, Rev, FinAmt INT DEFAULT 0;
    DECLARE cur_1 CURSOR FOR SELECT DISTINCT (CONCAT(RetailerId, '#^#', EntityId)) FROM retailerid WHERE BankCode = "012" AND CONCAT(RetailerId, '#^#', EntityId) IN (SELECT DISTINCT (CONCAT(CardAcceptorIdentification, '#^#', AcquiringInstitutionIdentification)) FROM currentdatetransactionhistory) LIMIT 5;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    OPEN cur_1;

    read_loop:loop
        -- * Fetch Single Record
        FETCH cur_1 INTO iseretdata;
        SELECT SUBSTRING_INDEX(iseretdata, '#^#', 1), SUBSTRING_INDEX(iseretdata, '#^#', -1) INTO RetId, EntId;
        -- * Purchase / Financial
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Pur FROM currentdatetransactionhistory WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = EntId AND MessageType = "0210" AND ProcessingCode = "000000";
        -- * Refund_Reversal
        SELECT IFNULL(SUM(FinalAmount), 0) INTO RefRev FROM currentdatetransactionhistory WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = EntId AND MessageType = "0420" AND ProcessingCode = "200000";
        -- * Refund
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Ref FROM currentdatetransactionhistory WHERE CardAcceptorIdentification = RetId  AND ResponseCode = "00" AND AcquiringInstitutionIdentification = EntId AND MessageType = "0210" AND ProcessingCode = "200000";
        -- * Reversal
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Rev FROM currentdatetransactionhistory WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = EntId AND MessageType = "0420" AND ProcessingCode = "000000";
        -- * Store Values In Variables
        SELECT (Pur+RefRev)-(Ref+Rev), IdentificationNumber, EmailAddress, BankCode, MovmentType, AccountNumber 
        #INTO FinAmt, Ruth, EmailId, BnkCd, MovTy, AcNo 
        FROM retailerid WHERE (RetailerId = RetId AND EntityId = EntId);
        -- * Check IF Cursor Is Empty
        IF is_done = 1 THEN LEAVE read_loop;
        END IF;
        -- * Insert Data Into Table Estado
        -- INSERT INTO estado (RID, EID, FinAmt, RNAME, RUTH, EMAIL_ID, BNK_CODE, AC_TYPE, AC_NO) VALUES (RetId, EntId, FinAmt, "", Ruth, EmailId, BnkCd, MovTy, AcNo);
    END LOOP read_loop;
    CLOSE cur_1;
END $$
DELIMITER ;
CALL BancoEstadoReports;
DROP PROCEDURE IF EXISTS BancoEstadoReports;
