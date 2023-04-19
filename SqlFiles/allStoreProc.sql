
-- * ######################## AcquirerOriginalDecline_IssuerReversalSuccess ########################## 

DROP PROCEDURE IF EXISTS AcquirerOriginalDecline_IssuerReversalSuccess;
DELIMITER $$
CREATE PROCEDURE AcquirerOriginalDecline_IssuerReversalSuccess()
COMMENT '
# Proc Name :- AcquirerOriginalDecline_IssuerReversalSuccess
# Created By :- Dishant Raut [22Jun2022]
# Updated By :- Tejaswini Somware [22Jun2022]
# Params :- No Params Required
# Desc :- Get Acquirer Side Original Decline & Issuer Side Reversal Success
# Exec :- CALL AcquirerOriginalDecline_IssuerReversalSuccess();
# Drop :- DROP PROCEDURE IF EXISTS AcquirerOriginalDecline_IssuerReversalSuccess;
'
BEGIN
SELECT
    AcqOrgDec.RRN,
    AcqOrgDec.LDate,
    AOD_MT,
    AOD_PC,
    AOD_RC,
    IRS_MT,
    IRS_PC,
    IRS_RC,
    AcqOrgDec.TrxAmt,
    AOD_LTime,
    IRS_LTime
    
FROM
    (
        SELECT
            RetrievalReferenceNumber AS RRN,
            MessageType AS AOD_MT,
            ProcessingCode AS AOD_PC,
            ResponseCode AS AOD_RC,
            TransactionAmount AS TrxAmt,
            LocalTransactionDate AS LDate,
            LocalTransactionTime AS AOD_LTime
        FROM
            iseretailer
        WHERE
            MessageType = "0210"
            AND ResponseCode != "00"
    ) AS AcqOrgDec
    INNER JOIN (
        SELECT
            RetrievalReferenceNumber AS RRN,
            MessageType AS IRS_MT,
            ProcessingCode AS IRS_PC,
            ResponseCode AS IRS_RC,
            TransactionAmount AS TrxAmt,
            LocalTransactionDate AS LDate,
            LocalTransactionTime AS IRS_LTime
        FROM
            issuerextractcopy
        WHERE
            MessageType = "0420"
            AND ResponseCode = "00"
    ) AS IssRevSuc ON AcqOrgDec.RRN = IssRevSuc.RRN
    AND AcqOrgDec.TrxAmt = IssRevSuc.TrxAmt
    AND AcqOrgDec.LDate = IssRevSuc.LDate
ORDER BY
AcqOrgDec.LDate
DESC;
END $$
DELIMITER ;
CALL AcquirerOriginalDecline_IssuerReversalSuccess;
#DROP PROCEDURE IF EXISTS AcquirerOriginalDecline_IssuerReversalSuccess;



-- * ######################## ProdStats ########################## 

DROP PROCEDURE IF EXISTS ProdStats;
DELIMITER $$
CREATE PROCEDURE ProdStats()
COMMENT '
# Proc Name :- ProdStats
# Created By :- Dishant Raut [13Jun2022]
# Updated By :- Tejaswini Somware [22Jun2022]
# Params :- No Params Required
# Desc :- Get Stats Of Prod Data Every Day
            1. Retailer Load Count
            2. Acquirer (IseRetailer) Node Count
            3. Issuer (IssuerExtractCopy) Node Count
            4. Invalid Trnx (AcquirerNotValid) Count
            5. Issuer Side More Acquirer Side Missing -> IssMoreAcqMiss
            6. Acquirer Side More Issuer Side Missing -> AcqMoreIssMiss
# Exec :- CALL ProdStats();
# Drop :- DROP PROCEDURE IF EXISTS ProdStats;
'
BEGIN
    DECLARE acqNode, issNode, retLoad, invalidTrx INT DEFAULT 0;
    SELECT COUNT(RetailerId) INTO retLoad FROM retailerid;
    SELECT COUNT(RetrievalReferenceNumber) INTO acqNode FROM iseretailer;
    SELECT COUNT(RetrievalReferenceNumber) INTO issNode FROM issuerextractcopy;
    SELECT COUNT(RetrievalReferenceNumber) INTO invalidTrx FROM acquirernotvalid WHERE ResponseCode = "00";    
    SELECT retLoad, acqNode, issNode, invalidTrx;
    -- * Issuer Side More Acquirer Side Missing
    (
        SELECT
            LocalTransactionDate AS TrnxDate,
            #RetrievalReferenceNumber AS RRN,
            COUNT(RetrievalReferenceNumber) AS AcqMissCnt
        FROM
            issuerextractcopy
        WHERE
            ResponseCode = "00"
            AND RetrievalReferenceNumber NOT IN (
                SELECT
                    RetrievalReferenceNumber
                FROM
                    iseretailer
                WHERE
                    ResponseCode = "00"
            )
        GROUP BY
            LocalTransactionDate
        ORDER BY
            LocalTransactionDate
    )
    UNION
    (
        SELECT
            "Total Count = ",
            COUNT(RetrievalReferenceNumber)
        FROM
            issuerextractcopy
        WHERE
            ResponseCode = "00"
            AND RetrievalReferenceNumber NOT IN (
                SELECT
                    RetrievalReferenceNumber
                FROM
                    iseretailer
                WHERE
                    ResponseCode = "00"
            )
    );
    -- * Acquirer Side More Issuer Side Missing
    (
        SELECT
            LocalTransactionDate AS TrnxDate,
            #RetrievalReferenceNumber AS RRN,
            COUNT(RetrievalReferenceNumber) AS IssMissCnt
        FROM
            iseretailer
        WHERE
            ResponseCode = "00"
            AND RetrievalReferenceNumber NOT IN (
                SELECT
                    RetrievalReferenceNumber
                FROM
                    issuerextractcopy
                WHERE
                    ResponseCode = "00"
            )
        GROUP BY
            LocalTransactionDate
        ORDER BY
            LocalTransactionDate
    )
    UNION
    (
        SELECT
            "Total Count = ",
            COUNT(RetrievalReferenceNumber)
        FROM
            iseretailer
        WHERE
            ResponseCode = "00"
            AND RetrievalReferenceNumber NOT IN (
                SELECT
                    RetrievalReferenceNumber
                FROM
                    issuerextractcopy
                WHERE
                    ResponseCode = "00"
            )
    );

END$$
DELIMITER ;
CALL ProdStats();
#DROP PROCEDURE IF EXISTS ProdStats;



-- * ######################## PhaseOne_AcqMoreIssMiss ########################## 

DROP PROCEDURE IF EXISTS PhaseOne_AcqMoreIssMiss;
DELIMITER $$
CREATE PROCEDURE PhaseOne_AcqMoreIssMiss()
COMMENT '
# Proc Name :- PhaseOne_AcqMoreIssMiss
# Created By :- Dishant Raut [13Jun2022]
# Updated By :- Tejaswini Somware [22Jun2022]
# Params :- No Params Required
# Desc :- Get All Issuer Side Missing Trnx
            1. Issuer Side Less Trnx
            2. Acquirer Side More Trnx
# Exec :- CALL PhaseOne_AcqMoreIssMiss();
# Drop :- DROP PROCEDURE IF EXISTS PhaseOne_AcqMoreIssMiss;
'
BEGIN
-- * Issuer Side More Acquirer Side Missing
SELECT
    MessageType AS MT,
    ProcessingCode AS PC,
    ResponseCode AS RC,
    ForwardingInstitutionIdentification AS Brand,
    AcquiringInstitutionIdentification AS Switch,
    RetrievalReferenceNumber AS RRN,
    Track2Data AS CardNo,
    CardAcceptorIdentification AS RetId,
    LocalTransactionDate AS TrxDate,
    LocalTransactionTime AS TrxTime,
    SystemsTraceAuditNumber AS TraceId,
    ChannelType AS Channel,
    TransactionAmount AS Amt
FROM
    iseretailer as acq
WHERE
    acq.ResponseCode = "00"
    AND RetrievalReferenceNumber NOT IN (
        SELECT
            RetrievalReferenceNumber
        FROM
            issuerextractcopy as isu
        WHERE
            isu.ResponseCode = "00" and acq.MessageType = isu.MessageType
    );
END$$
DELIMITER ;
CALL PhaseOne_AcqMoreIssMiss;
#DROP PROCEDURE IF EXISTS PhaseOne_AcqMoreIssMiss;



-- * ######################## PhaseOne_IssMoreAcqMiss ########################## 

DROP PROCEDURE IF EXISTS PhaseOne_IssMoreAcqMiss;
DELIMITER $$
CREATE PROCEDURE PhaseOne_IssMoreAcqMiss()
COMMENT '
# Proc Name :- PhaseOne_IssMoreAcqMiss
# Created By :- Dishant Raut [13Jun2022]
# Updated By :- Tejaswini Somware [22Jun2022]
# Params :- No Params Required
# Desc :- Get All Acquirer Side Missing Trnx
            1. Issuer Side More Trnx
            2. Acquirer Side Less Trnx
# Exec :- CALL PhaseOne_IssMoreAcqMiss();
# Drop :- DROP PROCEDURE IF EXISTS PhaseOne_IssMoreAcqMiss;
'
BEGIN
-- Issuer Side More Acquirer Side Missing
SELECT
    MessageType AS MT,
    ProcessingCode AS PC,
    ResponseCode AS RC,
    ForwardingInstitutionIdentification AS Brand,
    AcquiringInstitutionIdentification AS Switch,
    RetrievalReferenceNumber AS RRN,
    Track2Data AS CardNo,
    CardAcceptorIdentification AS RetId,
    LocalTransactionDate AS TrxDate,
    LocalTransactionTime AS TrxTime,
    SystemsTraceAuditNumber AS TraceId,
    ChannelType AS Channel,
    TransactionAmount AS Amt
FROM
    issuerextractcopy as isu
WHERE
    isu.ResponseCode = "00"
    AND RetrievalReferenceNumber NOT IN (
        SELECT
            RetrievalReferenceNumber
        FROM
            iseretailer as acq
        WHERE
            acq.ResponseCode = "00" and acq.MessageType = isu.MessageType
    );
END$$
DELIMITER ;
CALL PhaseOne_IssMoreAcqMiss;
#DROP PROCEDURE IF EXISTS PhaseOne_IssMoreAcqMiss;


-- * ######################## AcquirerSide_OriginalDeclineReversalSuccess ########################## 

DROP PROCEDURE IF EXISTS `AcquirerSide_OriginalDeclineReversalSuccess`;
DELIMITER $$ 
CREATE PROCEDURE `AcquirerSide_OriginalDeclineReversalSuccess`(
    IN vTableName VARCHAR(40),
    IN lTableName VARCHAR(40),
    IN rTableName VARCHAR(40)
) 
COMMENT '
# Proc Name :- AcquirerSide_OriginalDeclineReversalSuccess
# Created By :- Dishant Raut [13Jun2022]
# Updated By :- Tejaswini Somware [22Jun2022]
# Params :- Stored Procs With 3 IN Parameters
            1. vTableName > Table You Want To View
            2. lTableName > Left Table Name For Inner Join
            3. rTableName > Right Table Name For Inner Join
# Desc :- Get Acquirer Side Original Decline Reversal Success
# Exec :- CALL AcquirerSide_OriginalDeclineReversalSuccess();
# Drop :- DROP PROCEDURE IF EXISTS AcquirerSide_OriginalDeclineReversalSuccess;

'
BEGIN
SET @makeSqlQuery_ = CONCAT (
        'SELECT ',
        vTableName,
        '.* FROM
    (
        SELECT
            LocalTransactionDate AS LDate,
            Track2Data AS CardNo,
            RetrievalReferenceNumber AS RRN,
            SystemsTraceAuditNumber AS TraceId,
            LocalTransactionTime AS LTime,
            MessageType AS MT,
            ProcessingCode AS PC,
            ResponseCode AS RC,
            TransactionAmount AS TrxAmt
        FROM
            iseretailer
        WHERE
            ResponseCode != "00"
            AND MessageType = "0210"
            AND ProcessingCode = "000000"
    ) AS ',lTableName,'
    INNER JOIN (
        SELECT
            LocalTransactionDate AS LDate,
            Track2Data AS CardNo,
            RetrievalReferenceNumber AS RRN,
            SystemsTraceAuditNumber AS TraceId,
            LocalTransactionTime AS LTime,
            MessageType AS MT,
            ProcessingCode AS PC,
            ResponseCode AS RC,
            TransactionAmount AS TrxAmt
        FROM
            iseretailer
        WHERE
            ResponseCode = "00"
            AND MessageType = "0420"
            AND ProcessingCode = "000000"
    ) AS ',rTableName,' ON ',
        lTableName,
        '.RRN = ',
        rTableName,
        '.RRN
    AND ',
        lTableName,
        '.LDate = ',
        rTableName,
        '.LDate
    AND ',
        lTableName,
        '.LTime = ',
        rTableName,
        '.LTime
    AND ',
        lTableName,
        '.CardNo = ',
        rTableName,
        '.CardNo
ORDER BY
    ',
        vTableName,
        '.LDate DESC;
'
    );

PREPARE statement_ FROM @makeSqlQuery_;
EXECUTE statement_;
END $$ 
DELIMITER ;
CALL `AcquirerSide_OriginalDeclineReversalSuccess`('AcqRevSuccess', 'AcqOgDecline', 'AcqRevSuccess');
CALL `AcquirerSide_OriginalDeclineReversalSuccess`('AcqOgDecline', 'AcqOgDecline', 'AcqRevSuccess');
#DROP PROCEDURE IF EXISTS `AcquirerSide_OriginalDeclineReversalSuccess`;



-- * ######################## CCX30/CCX24 :- GetFinalAmtFromIdp ########################## 


DROP PROCEDURE IF EXISTS GetFinalAmtFromIdp;
DELIMITER $$
CREATE PROCEDURE GetFinalAmtFromIdp(IN idp VARCHAR(40), OUT amtBC INT(20), OUT amtAC INT(20), OUT commAmt INT(20))
COMMENT '
# Func Name :- GetFinalAmtFromIdp
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- IDP (20)
# Desc :- Get Amount Before Comm / Total Comm / After Comm Based On IDP
# Exec :- SELECT GetFinalAmtFromIdp("IDP001NAN00000000000");
# Drop :- DROP FUNCTION IF EXISTS GetFinalAmtFromIdp;
'
BEGIN

    SET @PurBC = @PurAC = @PurCom = 1;
    SET @Pur = CONCAT('SELECT IFNULL(SUM(TransactionAmount), 0) , IFNULL(SUM(FinalAmount), 0), IFNULL(SUM(TotalCommissions), 0) INTO @PurBC, @PurAC, @PurCom FROM fulldaytransactionhistory WHERE MessageType = "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND IDP = "', idp, '";');
    PREPARE statement1_ FROM @Pur;
    EXECUTE statement1_;

    SET @RefRevBC = @RefRevAC = @RefRevCom = 1;    
    SET @RefRev = CONCAT('SELECT IFNULL(SUM(TransactionAmount), 0), IFNULL(SUM(FinalAmount), 0), IFNULL(SUM(TotalCommissions), 0) INTO @RefRevBC, @RefRevAC, @RefRevCom FROM fulldaytransactionhistory WHERE MessageType = "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND IDP = "', idp, '";');
    PREPARE statement2_ FROM @RefRev;
    EXECUTE statement2_;

    SET @RefBC = @RefAC = @RefCom = 1;
    SET @Ref = CONCAT('SELECT IFNULL(SUM(TransactionAmount), 0), IFNULL(SUM(FinalAmount), 0), IFNULL(SUM(TotalCommissions), 0) INTO @RefBC, @RefAC, @RefCom  FROM fulldaytransactionhistory WHERE MessageType = "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND IDP = "', idp, '";');
    PREPARE statement3_ FROM @Ref;
    EXECUTE statement3_;
    
    SET @RevBC = @RevAC = @RevCom = 1;
    SET @Rev = CONCAT('SELECT IFNULL(SUM(TransactionAmount), 0), IFNULL(SUM(FinalAmount), 0), IFNULL(SUM(TotalCommissions), 0) INTO @RevBC, @RevAC, @RevCom FROM fulldaytransactionhistory WHERE MessageType = "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND IDP = "', idp, '";');
    PREPARE statement4_ FROM @Rev;
    EXECUTE statement4_;
    
    SET amtBC = (@PurBC+@RefRevBC)-(@RefBC+@RevBC);
    SET amtAC = (@PurAC+@RefRevAC)-(@RefAC+@RevAC);
    SET commAmt = (@PurCom+@RefRevCom)-(@RefCom+@RevCom);

END$$
DELIMITER ;
CALL GetFinalAmtFromIdp('IDP002NAN15214307a70', @amtBc, @amtAc);
SELECT @amtBc;
SELECT @amtAc;  
SELECT @commAmt;  
-- DROP PROCEDURE IF EXISTS GetFinalAmtFromIdp;



-- * ######################## PhaseOne_MissingAtAcquirerExtract ########################## 

DROP PROCEDURE IF EXISTS PhaseOne_MissingAtAcquirerExtract;
DELIMITER $$
CREATE PROCEDURE PhaseOne_MissingAtAcquirerExtract()
COMMENT '
# Proc Name :- PhaseOne_MissingAtAcquirerExtract
# Created By :- Ankita Harad [26Sep2022]
# Updated By :- Ankita Harad [26Sep2022]
# Params :- No Params Required
# Desc :- Get All Issuer Side Missing Trnx
            1. Issuer Side More Trnx
            2. Acquirer Side Less Trnx
# Exec :- CALL PhaseOne_MissingAtAcquirerExtract();
# Drop :- DROP PROCEDURE IF EXISTS PhaseOne_MissingAtAcquirerExtract;
'
BEGIN
-- * Issuer Side More Acquirer Side Missing
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
    LocalTransactionTime AS LTime,
    BrandName(ForwardingInstitutionIdentification) AS BN,
    ResponseCodeDescription(ResponseCode) AS RC,
    SwitchName(AcquiringInstitutionIdentification, ChannelType) AS SwitchName,
    TransactionType(MessageType, ProcessingCode) AS TrxTyp
FROM
    issuerextract
WHERE
    ResponseCode = "00"
    AND RetrievalReferenceNumber NOT IN (
        SELECT
            RetrievalReferenceNumber
        FROM
            acquirerextract
        WHERE
            ResponseCode = "00"
    );
END$$
DELIMITER ;
CALL PhaseOne_MissingAtAcquirerExtract;
#DROP PROCEDURE IF EXISTS PhaseOne_MissingAtAcquirerExtract;



-- * ######################## PhaseOne_MissingAtIssuerExtract ########################## 

DROP PROCEDURE IF EXISTS PhaseOne_MissingAtIssuerExtract;
DELIMITER $$
CREATE PROCEDURE PhaseOne_MissingAtIssuerExtract()
COMMENT '
# Proc Name :- PhaseOne_MissingAtIssuerExtract
# Created By :- Ankita Harad [26Sep2022]
# Updated By :- Ankita Harad [26Sep2022]
# Params :- No Params Required
# Desc :- Get All Acquirer Side Missing Trnx
            1. Issuer Side Less Trnx
            2. Acquirer Side More Trnx
# Exec :- CALL PhaseOne_MissingAtIssuerExtract();
# Drop :- DROP PROCEDURE IF EXISTS PhaseOne_MissingAtIssuerExtract;
'
BEGIN
-- Acquirer Side More Issuer Side Missing
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
    LocalTransactionTime AS LTime,
    BrandName(ForwardingInstitutionIdentification) AS BN,
    ResponseCodeDescription(ResponseCode) AS RC,
    SwitchName(AcquiringInstitutionIdentification, ChannelType) AS SwitchName,
    TransactionType(MessageType, ProcessingCode) AS TrxTyp
FROM
    acquirerextract
WHERE
    ResponseCode = "00"
    AND RetrievalReferenceNumber NOT IN (
        SELECT
            RetrievalReferenceNumber
        FROM
            issuerextract
        WHERE
            ResponseCode = "00"
    );
END$$
DELIMITER ;
CALL PhaseOne_MissingAtIssuerExtract;
#DROP PROCEDURE IF EXISTS PhaseOne_MissingAtIssuerExtract;


-- * ######################## CCX24_UpdateMoveDataIdpTable ########################## 

DELIMITER $$
CREATE PROCEDURE CCX24_UpdateMoveDataIdpTable()
COMMENT '
# Proc Name :- CCX24_UpdateMoveDataIdpTable
# Created By :- Dishant Raut [29Dec2022]
# Updated By :- Dishant Raut [29Dec2022]
# Params :- No Params Required
# Desc :- Move Records To Respective Table Based On Bank Code & Delete Wrong Bank Codes
# Exec :- CALL CCX24_UpdateMoveDataIdpTable();
# Drop :- DROP PROCEDURE IF EXISTS CCX24_UpdateMoveDataIdpTable;
'
BEGIN

DECLARE cc, ec INT DEFAULT 0;
SELECT COUNT(*) INTO cc FROM chileidpupdate WHERE BankCode = "012";
SELECT COUNT(*) INTO ec FROM estadoidpupdate WHERE BankCode != "012";

IF cc > 0 THEN
    INSERT INTO 
        estadoidpupdate
    SELECT 
        NULL, RetId, InsId, "Estado", Ruth, Dv, RetName, DocNum, EmailId, BankCode, AcType, AcNum,
        FinalAmt, "Estado", "Estado", "Estado", "Estado", DepositStatus, RetailerStatus, PaymentDate,
        DepositDate, BrodcastDate, Region
    FROM 
        chileidpupdate
    WHERE 
        BankCode = "012";

    DELETE FROM chileidpupdate WHERE BankCode = "012";
END IF;

IF ec > 0 THEN
    INSERT INTO 
        chileidpupdate
    SELECT 
        NULL, RetId, InsId, "1", Ruth, Dv, RetName, "991", IDP, FinalAmt, "", AcType, BankCode, 
        AcNum, "", EmailId, "1", DepositStatus, RetailerStatus, PaymentDate, DepositDate, 
        BrodcastDate, Region
    FROM 
        estadoidpupdate
    WHERE 
        BankCode != "012";
    
    DELETE FROM estadoidpupdate WHERE BankCode != "012";
END IF;
-- * Update Table : estadoidpupdate
UPDATE
    estadoidpupdate, retailerid
SET
    estadoidpupdate.BankCode = retailerid.BankCode,
    estadoidpupdate.AcType = ChileEstadoAccountType(retailerid.BankCode, retailerid.MovmentType)
WHERE
    estadoidpupdate.RetId = retailerid.RetailerId
    AND estadoidpupdate.InsId = retailerid.EntityId;
-- * Update Table : chileidpupdate
UPDATE
    chileidpupdate, retailerid
SET
    chileidpupdate.BankCode = retailerid.BankCode,
    chileidpupdate.AcType = ChileEstadoAccountType(retailerid.BankCode, retailerid.MovmentType)
WHERE
    chileidpupdate.RetId = retailerid.RetailerId
    AND chileidpupdate.InsId = retailerid.EntityId;

END$$
DELIMITER ;
CALL CCX24_UpdateMoveDataIdpTable;
#DROP PROCEDURE IF EXISTS CCX24_UpdateMoveDataIdpTable;
