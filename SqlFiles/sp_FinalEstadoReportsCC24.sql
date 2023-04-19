DROP PROCEDURE IF EXISTS BancoEstadoReports;
DELIMITER $$  
CREATE PROCEDURE BancoEstadoReports()
BEGIN

    DECLARE iseretdata, RetId, InsId, IDP, Ruth, EmailId, BankCod, MovType, AcNum VARCHAR(20) DEFAULT "NAN";
    DECLARE is_done, Pur, RefRev, Ref, Rev, FinAmt INT DEFAULT 0;
    DECLARE cur_1 CURSOR FOR SELECT DISTINCT (CONCAT(RetailerId, '#^#', EntityId)) FROM retailerid WHERE BankCode = "012" AND CONCAT(RetailerId, '#^#', EntityId) IN (SELECT DISTINCT (CONCAT(CardAcceptorIdentification, '#^#', AcquiringInstitutionIdentification)) FROM iseretailer) LIMIT 5;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    TRUNCATE TABLE estado_report;
    OPEN cur_1;

    read_loop:loop
        -- * Fetch Single Record
        FETCH cur_1 INTO iseretdata;
        SELECT SUBSTRING_INDEX(iseretdata, '#^#', 1), SUBSTRING_INDEX(iseretdata, '#^#', -1) INTO RetId, InsId;
        -- * Purchase / Financial
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Pur FROM iseretailer WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = InsId AND MessageType = "0210" AND ProcessingCode = "000000";
        -- * Refund_Reversal
        SELECT IFNULL(SUM(FinalAmount), 0) INTO RefRev FROM iseretailer WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = InsId AND MessageType = "0420" AND ProcessingCode = "200000";
        -- * Refund
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Ref FROM iseretailer WHERE CardAcceptorIdentification = RetId  AND ResponseCode = "00" AND AcquiringInstitutionIdentification = InsId AND MessageType = "0210" AND ProcessingCode = "200000";
        -- * Reversal
        SELECT IFNULL(SUM(FinalAmount), 0) INTO Rev FROM iseretailer WHERE CardAcceptorIdentification = RetId AND ResponseCode = "00" AND AcquiringInstitutionIdentification = InsId AND MessageType = "0420" AND ProcessingCode = "000000";
        -- * Store Values In Variables
        SELECT (Pur+RefRev)-(Ref+Rev), IdentificationNumber, EmailAddress, BankCode, MovmentType, AccountNumber INTO FinAmt, Ruth, EmailId, BankCod, MovType, AcNum FROM retailerid WHERE (RetailerId = RetId AND EntityId = InsId);
        -- * Check IF Cursor Is Empty
        IF is_done = 1 THEN LEAVE read_loop;
        END IF;
        -- SELECT RetId, InsId, Pur, RefRev, Ref, Rev, FinAmt, Ruth, EmailId, BankCod, MovType, AcNum;
        -- * Insert Data Into Table Estado
        INSERT INTO estado_report (RetId, InsId, Ruth, RetName, EmailId, BankCode, AcType, AcNum, FinalAmt) VALUES (RetId, InsId, Ruth, "IDP001", EmailId, BankCod, MovType, AcNum, FinAmt);
    END LOOP read_loop;
    CLOSE cur_1;

END $$
DELIMITER ;
CALL BancoEstadoReports;
DROP PROCEDURE IF EXISTS BancoEstadoReports;

