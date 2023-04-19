-- ################################################################################################### 
-- * ################################## DepositReports Verification ################################## 
-- ################################################################################################### 
DROP PROCEDURE IF EXISTS DepositReports;
DELIMITER $$
CREATE PROCEDURE DepositReports()
COMMENT '
# Proc Name :- DepositReports
# Created By :- Ankita Harad [07Jul2022]
# Updated By :- Ankita Harad [07Jul2022]
# Params :- No Params Required
# Desc :- Get Final Amount For Each Institution ID
# Exec :- CALL DepositReports();
# Drop :- DROP PROCEDURE IF EXISTS DepositReports;
'
BEGIN
    DECLARE gpgmvpPurchase, gpgmvpRefundReversal, gpgmvpRefund, gpgmvpReversal, gpgmvpTotalAmt INT DEFAULT 0;
    DECLARE alviPurchase, alviRefundReversal, alviRefund, alviReversal, alviTotalAmt INT DEFAULT 0; 
    DECLARE is_done, daPurchase, daRefundReversal, daRefund, daReversal, daEachRetAmt, daTotalAmt INT DEFAULT 0;
    DECLARE retId VARCHAR(25) DEFAULT "NONE";

    DECLARE cur_1 CURSOR FOR select distinct (CardAcceptorIdentification) from iseretailer where AcquiringInstitutionIdentification = "2003";
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    OPEN cur_1;

    -- * GPGMVP Credit Amt (Puchase & Refund Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0012";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0012";
    -- * GPGMVP Debit Amt (Refund & Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0012";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0012";
    -- * GPGMVP Final Amt (Credit - Debit)
    SELECT (gpgmvpPurchase+gpgmvpRefundReversal)-(gpgmvpRefund+gpgmvpReversal) INTO gpgmvpTotalAmt;
    SELECT gpgmvpTotalAmt AS GPGMVP_TotalAmt;

    -- * ALVI Credit Amt (Puchase & Refund Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0014";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0014";
    -- * ALVI Debit Amt (Refund & Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0014";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND AcquiringInstitutionIdentification = "0014";
    -- * ALVI Final Amt (Credit - Debit)
    SELECT (alviPurchase+alviRefundReversal)-(alviRefund+alviReversal) INTO alviTotalAmt;
    SELECT alviTotalAmt AS ALVI_TotalAmt;

    read_loop:loop
        -- * Fetch Single Record
        FETCH cur_1 INTO retId;
         -- * DA Credit Amt (Puchase & Refund Reversal)
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND AcquiringInstitutionIdentification = "2003";
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND AcquiringInstitutionIdentification = "2003";
        -- * DA Debit Amt (Refund & Reversal)
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND AcquiringInstitutionIdentification = "2003";
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND AcquiringInstitutionIdentification = "2003";
        SELECT (daPurchase+daRefundReversal)-(daRefund+daReversal) INTO daEachRetAmt;
        -- * DA Final Amt (Credit - Debit)
        SELECT daEachRetAmt+daTotalAmt INTO daTotalAmt;
        IF is_done = 1 THEN LEAVE read_loop;
        END IF;
        SELECT retId, daEachRetAmt, daTotalAmt;
    END LOOP read_loop;
    SELECT daTotalAmt-daEachRetAmt AS DA_TotalAmt;
    CLOSE cur_1;

END$$
DELIMITER ;
CALL DepositReports();
DROP PROCEDURE IF EXISTS DepositReports

-- ################################################################################################### 
-- * ################################## DepositReports Verification Based on Channel ################################## 
-- ################################################################################################### 
DROP PROCEDURE IF EXISTS DepositReports;
DELIMITER $$
CREATE PROCEDURE DepositReports()
COMMENT '
# Proc Name :- DepositReports
# Created By :- Ankita Harad [29Aug2022]
# Updated By :- Ankita Harad [29Aug2022]
# Params :- No Params Required
# Desc :- Get Final Amount For Each Institution ID Based on Channel
# Exec :- CALL DepositReports();
# Drop :- DROP PROCEDURE IF EXISTS DepositReports;
'
BEGIN
    DECLARE gpgmvpPurchase, gpgmvpRefundReversal, gpgmvpRefund, gpgmvpReversal, gpgmvpTotalAmt INT DEFAULT 0;
    DECLARE alviPurchase, alviRefundReversal, alviRefund, alviReversal, alviTotalAmt INT DEFAULT 0; 
    DECLARE is_done, daPurchase, daRefundReversal, daRefund, daReversal, daEachRetAmt, daTotalAmt INT DEFAULT 0;
    DECLARE retId VARCHAR(25) DEFAULT "NONE";

    DECLARE cur_1 CURSOR FOR select distinct (CardAcceptorIdentification) from iseretailer where ChannelType = "DA";
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    OPEN cur_1;

    -- * GPGMVP Credit Amt (Puchase & Refund Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND ChannelType = "GPGMVP";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND ChannelType = "GPGMVP";
    -- * GPGMVP Debit Amt (Refund & Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND ChannelType = "GPGMVP";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO gpgmvpReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND ChannelType = "GPGMVP";
    -- * GPGMVP Final Amt (Credit - Debit)
    SELECT (gpgmvpPurchase+gpgmvpRefundReversal)-(gpgmvpRefund+gpgmvpReversal) INTO gpgmvpTotalAmt;
    SELECT gpgmvpTotalAmt AS GPGMVP_TotalAmt;

    -- * ALVI Credit Amt (Puchase & Refund Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND ChannelType = "ALVI";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND ChannelType = "ALVI";
    -- * ALVI Debit Amt (Refund & Reversal)
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND ChannelType = "ALVI";
    SELECT IFNULL(SUM(FinalAmount), 0) INTO alviReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND ChannelType = "ALVI";
    -- * ALVI Final Amt (Credit - Debit)
    SELECT (alviPurchase+alviRefundReversal)-(alviRefund+alviReversal) INTO alviTotalAmt;
    SELECT alviTotalAmt AS ALVI_TotalAmt;

    read_loop:loop
        -- * Fetch Single Record
        FETCH cur_1 INTO retId;
         -- * DA Credit Amt (Puchase & Refund Reversal)
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daPurchase FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "000000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND ChannelType = "DA";
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daRefundReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "200000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND ChannelType = "DA";
        -- * DA Debit Amt (Refund & Reversal)
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daRefund FROM iseretailer WHERE MessageType= "0210" AND ProcessingCode = "200000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND ChannelType = "DA";
        SELECT IFNULL(SUM(FinalAmount), 0) INTO daReversal FROM iseretailer WHERE MessageType= "0420" AND ProcessingCode = "000000" AND ResponseCode = "00" AND CardAcceptorIdentification = retId AND ChannelType = "DA";
        SELECT (daPurchase+daRefundReversal)-(daRefund+daReversal) INTO daEachRetAmt;
        -- * DA Final Amt (Credit - Debit)
        SELECT daEachRetAmt+daTotalAmt INTO daTotalAmt;
        IF is_done = 1 THEN LEAVE read_loop;
        END IF;
        SELECT retId, daEachRetAmt, daTotalAmt;
    END LOOP read_loop;
    SELECT daTotalAmt-daEachRetAmt AS DA_TotalAmt;
    CLOSE cur_1;

END$$
DELIMITER ;
CALL DepositReports();
DROP PROCEDURE IF EXISTS DepositReports

-- ################################################################################################### 
-- ################################################################################################### 
