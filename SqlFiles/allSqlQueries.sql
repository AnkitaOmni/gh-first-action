SHOW PROCEDURE STATUS
WHERE
    db = 'OMNICOMP_BECH_BLUEPROD' OR
    db = 'OMNICOMP_BECH_Dishant';

-- * ################################################################################################################################

SELECT
    DEFINER,
    ROUTINE_SCHEMA,
    ROUTINE_NAME,
    SPECIFIC_NAME,
    ROUTINE_DEFINITION
FROM
    information_schema.routines
WHERE
    routine_type = 'PROCEDURE'
    AND routine_schema = 'OMNICOMP_BECH_Dishant';

-- * ################################################################################################################################

DELIMITER $$
CREATE PROCEDURE proc_name()
COMMENT 'this is my comment'
BEGIN
SELECT COUNT(RetailerId) FROM retailerid;
END $$
DELIMITER ;
CALL proc_name;
DROP PROCEDURE IF EXISTS proc_name;


-- * ################################################################################################################################

-- * CURSOR
DELIMITER $$  
CREATE PROCEDURE ABC()
BEGIN
    DECLARE CAI, BC, EID, RID, IDP, MovT, AccNo INT DEFAULT 0;
    DECLARE is_done INT DEFAULT 0;
    DECLARE cur_1 CURSOR FOR SELECT DISTINCT (CardAcceptorIdentification) FROM iseretailer LIMIT 5;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    OPEN cur_1;
    read_loop:loop
        FETCH cur_1 INTO CAI;
        IF is_done = 1 THEN LEAVE read_loop;
        END IF;
        SELECT EntityId, RetailerId, TRIM(BankCode), TRIM(MovmentType), AccountNumber 
        INTO EID, RID, BC, MovT, AccNo
        FROM retailerid WHERE RetailerId = CAI;
        SELECT EID, RID, BC, MovT, AccNo;
    END LOOP read_loop;
    CLOSE cur_1;
END $$
DELIMITER ;
CALL ABC;
DROP PROCEDURE IF EXISTS ABC;


-- * ################################################################################################################################


-- * While Loop
DELIMITER $$  
CREATE PROCEDURE ABC()
BEGIN 
DECLARE num INT DEFAULT 5;
    WHILE num > 0 DO
        SELECT num;
        SET num = num - 1;
    END WHILE;
END $$
DELIMITER ;
CALL ABC;
DROP PROCEDURE IF EXISTS ABC;


-- * ################################################################################################################################


SELECT
    ForwardingInstitutionIdentification AS Brd,
    AcquiringInstitutionIdentification AS Swt,
    Track2Data AS CardNo,
    SystemsTraceAuditNumber AS TcId,
    MessageType AS MT,
    ProcessingCode AS PC,
    ResponseCode AS RC,
    PrimaryMessageAuthenticationCodeMAC AS DI,
    CardType AS DC,
    RetrievalReferenceNumber AS RRN,
    TransactionAmount AS TAmt,
    ChannelType AS Chn,
    CardAcceptorIdentification AS RetId,
    PrimaryAccountNumberPAN AS Bin,
    LocalTransactionDate AS LDate,
    LocalTransactionTime AS LTime
    -- BrandName(ForwardingInstitutionIdentification) AS BN,
    -- ResponseCodeDescription(ResponseCode) AS RC,
    -- SwitchName(AcquiringInstitutionIdentification, ChannelType) AS SwitchName,
    -- TransactionType(MessageType, ProcessingCode) AS TrxTyp
FROM
    iseretailer WHERE ProcessingCode = '000000'
    AND ForwardingInstitutionIdentification = '8051'
    AND LocalTransactionDate > '2022-09-22'
    AND ResponseCode = '00'
    AND SystemsTraceAuditNumber NOT IN (
        SELECT
            SystemsTraceAuditNumber
        FROM
            issuerextractcopy
        WHERE
            ProcessingCode = '000000'
            AND ForwardingInstitutionIdentification = '8051'
            AND LocalTransactionDate > '2022-09-22'
            AND ResponseCode = '00'
    );

-- * ################################################################################################################################


-- * Stats
CALL prodstats;
-- * Each Side Missing
CALL PhaseOne_AcqMoreIssMiss;
CALL PhaseOne_IssMoreAcqMiss;
-- * Acq vs Iss
CALL AcquirerOriginalDecline_IssuerReversalSuccess;
-- * Manits Case Query (Can be more dynamic)
CALL AcquirerSide_OriginalDeclineReversalSuccess('AcqOgDecline', 'AcqOgDecline', 'AcqRevSuccess');
CALL AcquirerSide_OriginalDeclineReversalSuccess('AcqRevSuccess', 'AcqOgDecline', 'AcqRevSuccess');
-- * Backup
CALL ProdEachDayDataBKToDev;
CALL ProdEachDayDataBKToBlueProd;

