-- * SHOW FUNCTION STATUS WHERE Db = 'OMNICOMP_BECH_Dishant';


DELIMITER //
CREATE FUNCTION CalcIncome ( starting_value INT ) RETURNS INT
BEGIN

   DECLARE income INT;
   SET income = 0;
   label1: 
    WHILE income <= 3000 DO
        SET income = income + starting_value;
    END WHILE label1;
   RETURN income;

END; //

DELIMITER ;
SELECT CalcIncome (1000);
DROP FUNCTION CalcIncome;


-- * ##############################################################


DELIMITER $$
CREATE FUNCTION CustomerLevel(credit DECIMAL(10,2)) 
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE customerLevel VARCHAR(20);
    IF credit > 50000 THEN SET customerLevel = 'PLATINUM';
    ELSEIF (credit >= 50000 AND credit <= 10000) THEN SET customerLevel = 'GOLD';
    ELSEIF credit < 10000 THEN SET customerLevel = 'SILVER';
    END IF;
	-- return the customer level
	RETURN (customerLevel);
END$$
DELIMITER ;


-- * ##############################################################


DROP FUNCTION IF EXISTS BrandName;
DELIMITER $$
CREATE FUNCTION BrandName(fid VARCHAR(4)) RETURNS VARCHAR(30)
DETERMINISTIC
COMMENT '
# Func Name :- BrandName
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- ForwardingInstitutionIdentification
# Desc :- Get Name Of Brand
# Exec :- SELECT BrandName("8051");
# Drop :- DROP FUNCTION IF EXISTS BrandName;
'
BEGIN
    DECLARE brandName VARCHAR(20);
    IF fid = '8051' THEN SET brandName = 'VISA';
    ELSEIF fid = '2002' THEN SET brandName = 'Maestro';
    ELSEIF fid = '2001' THEN SET brandName = 'MasterCard';
    END IF;
	RETURN (brandName);
END$$
DELIMITER ;
SELECT BrandName('2001');
SELECT BrandName('8051');
SELECT BrandName('2002');


-- * ##############################################################


DROP FUNCTION IF EXISTS SwitchName;
DELIMITER $$
CREATE FUNCTION SwitchName(aid VARCHAR(4), chName VARCHAR(6)) RETURNS VARCHAR(100)
DETERMINISTIC
COMMENT '
# Func Name :- SwitchName
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- AcquiringInstitutionIdentification + ChannelType
# Desc :- Get Name Of Switch
# Exec :- SELECT SwitchName("8051");
# Drop :- DROP FUNCTION IF EXISTS SwitchName;
'
BEGIN
    DECLARE switchName VARCHAR(100);
    IF aid = '0012' AND chName = 'GPMPOS' THEN SET switchName = 'GeoPagos SmartPOS';
    ELSEIF aid = '0012' AND chName = 'GPGMVP'  THEN SET switchName = 'Geopagos MPOS';
    ELSEIF aid = '0012' AND chName = 'GPLINK'  THEN SET switchName = 'Geopagos Payment Link';
    ELSEIF aid = '2003' AND chName = 'DA'  THEN SET switchName = 'Digital Acquirer';
    ELSEIF aid = '0014' AND chName = 'ALVI'  THEN SET switchName = 'Alvi SMU';
    END IF;
	RETURN (switchName);
END$$
DELIMITER ;
SELECT SwitchName('0012', 'GPMPOS');
SELECT SwitchName('0012', 'GPGMVP');
SELECT SwitchName('0012', 'GPLINK');
SELECT SwitchName('2003', 'DA');
SELECT SwitchName('0014', 'ALVI');


-- * ##############################################################


DROP FUNCTION IF EXISTS BankNameOnBankCode;
DELIMITER $$
CREATE FUNCTION BankNameOnBankCode(bankCode VARCHAR(4)) RETURNS VARCHAR(50)
DETERMINISTIC
COMMENT '
# Func Name :- BankNameOnBankCode
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- Bank Code
# Desc :- Get Bank Name Using Bank Code
# Exec :- SELECT BankNameOnBankCode("012");
# Drop :- DROP FUNCTION IF EXISTS BankNameOnBankCode;
'
BEGIN
    DECLARE bankName VARCHAR(50);
    IF bankCode = '009' THEN SET bankName = 'BANCO INTERNACIONAL';
    ELSEIF bankCode = '014' THEN SET bankName = 'SCOTIABANK CHILE';
    ELSEIF bankCode = '016' THEN SET bankName = 'BANCO DE CREDITO E INVERSIONES';
    ELSEIF bankCode = '017' THEN SET bankName = 'BANCO DO BRASIL S.A.';
    ELSEIF bankCode = '027' THEN SET bankName = 'CORPBANCA';
    ELSEIF bankCode = '028' THEN SET bankName = 'BANCO BICE';
    ELSEIF bankCode = '031' THEN SET bankName = 'HSBC BANK (CHILE)';
    ELSEIF bankCode = '037' THEN SET bankName = 'BANCO SANTANDER-CHILE';
    ELSEIF bankCode = '039' THEN SET bankName = 'BANCO ITAU CHILE';
    ELSEIF bankCode = '040' THEN SET bankName = 'BANCO SUDAMERICANO';
    ELSEIF bankCode = '045' THEN SET bankName = 'THE BANK OF TOKYO-MITSUBISHI UFJ';
    ELSEIF bankCode = '049' THEN SET bankName = 'BANCO SECURITY';
    ELSEIF bankCode = '051' THEN SET bankName = 'BANCO FALABELLA';
    ELSEIF bankCode = '053' THEN SET bankName = 'BANCORIPLEY';
    ELSEIF bankCode = '055' THEN SET bankName = 'BANCO CONSORCIO';
    ELSEIF bankCode = '057' THEN SET bankName = 'BANCO PARIS';
    ELSEIF bankCode = '504' THEN SET bankName = 'BANCO BILBAO VIZCAYA ARGENTARIA';
    ELSEIF bankCode = '507' THEN SET bankName = 'BANCO DEL DESARROLLO';
    ELSEIF bankCode = '672' THEN SET bankName = 'COOPEUCH';
    ELSEIF bankCode = '729' THEN SET bankName = 'PREPAGO LOS HIROES';
    ELSEIF bankCode = '012' THEN SET bankName = 'BANCOESTADO';
    ELSEIF bankCode = '001' THEN SET bankName = 'BANCO DE CHILE/EDWARDS/CREDICHILE';
    END IF;
	RETURN (bankName);
END$$
DELIMITER ;
SELECT BankNameOnBankCode('012');


-- * ##############################################################


DROP FUNCTION IF EXISTS TransactionType;
DELIMITER $$
CREATE FUNCTION TransactionType(msgType VARCHAR(4), proCode VARCHAR(6)) RETURNS VARCHAR(30)
DETERMINISTIC
COMMENT '
# Func Name :- TransactionType
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- MessageType + ProcessingCode
# Desc :- Get Type Of Trnx Base On MT & PC
# Exec :- SELECT TransactionType("0210", "200000");
# Drop :- DROP FUNCTION IF EXISTS TransactionType;
'
BEGIN
    DECLARE trnxType VARCHAR(20);
    IF msgType = '0210' AND proCode = '000000' THEN SET trnxType = 'Purchase';
    ELSEIF msgType = '0210' AND proCode = '300000' THEN SET trnxType = 'Inquiry';
    ELSEIF msgType = '0210' AND proCode = '200000' THEN SET trnxType = 'Refund';
    ELSEIF msgType = '0420' AND proCode = '000000' THEN SET trnxType = 'Reversal Purchase';
    ELSEIF msgType = '0420' AND proCode = '300000' THEN SET trnxType = 'Reversal Inquiry';
    ELSEIF msgType = '0420' AND proCode = '200000' THEN SET trnxType = 'Refund Reversal';
    ELSEIF msgType = '0430' AND proCode = '000000' THEN SET trnxType = 'Reversal Purchase';
    ELSEIF msgType = '0430' AND proCode = '300000' THEN SET trnxType = 'Reversal Inquiry';
    ELSEIF msgType = '0430' AND proCode = '200000' THEN SET trnxType = 'Refund Reversal';
    END IF;
	RETURN (trnxType);
END$$
DELIMITER ;
SELECT TransactionType('0210', '200000')


-- * ##############################################################


DROP FUNCTION IF EXISTS ResponseCodeDescription;
DELIMITER $$
CREATE FUNCTION ResponseCodeDescription(rc VARCHAR(50)) RETURNS VARCHAR(100)
DETERMINISTIC
COMMENT '
# Func Name :- ResponseCodeDescription
# Created By :- Dishant Raut [15Sep2022]
# Updated By :- Dishant Raut [15Sep2022]
# Params :- Response Code
# Desc :- Get Response Code With Its Description
# Exec :- SELECT ResponseCodeDescription("W9");
# Drop :- DROP FUNCTION IF EXISTS ResponseCodeDescription;
'
BEGIN
    DECLARE rcDesc VARCHAR(50);
    IF rc = '11' THEN SET rcDesc = '11-APPROVED - VIP';
    ELSEIF rc = '12' THEN SET rcDesc = '12-INVALID TXN';
    ELSEIF rc = '13' THEN SET rcDesc = '13-INVALID AMT';
    ELSEIF rc = '14' THEN SET rcDesc = '14-INVALID CARD NUM.';
    ELSEIF rc = '15' THEN SET rcDesc = '15-INACTIVE OR TERMINAL NOT FOUND';
    ELSEIF rc = '31' THEN SET rcDesc = '31-NO SHARING';
    ELSEIF rc = '33' THEN SET rcDesc = '33-EXPIRED CARD';
    ELSEIF rc = '36' THEN SET rcDesc = '36-RESTRICTED CARD';
    ELSEIF rc = '38' THEN SET rcDesc = '38-ALLOWABLE PIN TRIES EXCEEDED';
    ELSEIF rc = '41' THEN SET rcDesc = '41-LOST CARD';
    ELSEIF rc = '43' THEN SET rcDesc = '43-STOLEN CARD';
    ELSEIF rc = '51' THEN SET rcDesc = '51-NO SUFFICIENT FUND';
    ELSEIF rc = '54' THEN SET rcDesc = '54-EXPIRED CARD';
    ELSEIF rc = '55' THEN SET rcDesc = '55-INCORRECT PIN';
    ELSEIF rc = '56' THEN SET rcDesc = '56-CAF NOT FOUND';
    ELSEIF rc = '57' THEN SET rcDesc = '57-TXN NOT PERMITTED';
    ELSEIF rc = '61' THEN SET rcDesc = '61-EXCEED WDRL AMT.';
    ELSEIF rc = '62' THEN SET rcDesc = '62-RESTRICTED CARD';
    ELSEIF rc = '65' THEN SET rcDesc = '65-EXCEED WDRL FREQ.';
    ELSEIF rc = '68' THEN SET rcDesc = '68-RESPONSE RECEIVED TOO LATE';
    ELSEIF rc = '75' THEN SET rcDesc = '75-PIN RETRIES EXCEEDED';
    ELSEIF rc = '76' THEN SET rcDesc = '76-APPROVED - PRI ENTRY CLUB';
    ELSEIF rc = '77' THEN SET rcDesc = '77-APPROVED - PENDING IDENTIFICATION';
    ELSEIF rc = '78' THEN SET rcDesc = '78-APPROVED - BLIND';
    ELSEIF rc = '79' THEN SET rcDesc = '79-APPROVED - ADMIN TXN.';
    ELSEIF rc = '80' THEN SET rcDesc = '80-APPROVED - NAT. NEG. HIT';
    ELSEIF rc = '81' THEN SET rcDesc = '81-APPROVED - COMMERCIAL';
    ELSEIF rc = '82' THEN SET rcDesc = '82-NO SECURITY BOX';
    ELSEIF rc = '83' THEN SET rcDesc = '83-PRIVATE- NO A/C';
    ELSEIF rc = '84' THEN SET rcDesc = '84-NO PBF';
    ELSEIF rc = '85' THEN SET rcDesc = '85-PBF UPDATE ERROR';
    ELSEIF rc = '86' THEN SET rcDesc = '86-INVALID AUTH TYPE';
    ELSEIF rc = '87' THEN SET rcDesc = '87-BAD TRACK2';
    ELSEIF rc = '89' THEN SET rcDesc = '89-TXN ROUTING ISSUE';
    ELSEIF rc = '94' THEN SET rcDesc = '94-DUPLICATE TXN';
    ELSEIF rc = '00' THEN SET rcDesc = '00-SUCCESS';
    ELSEIF rc = '01' THEN SET rcDesc = '01-REFER CARD ISSUER';
    ELSEIF rc = '02' THEN SET rcDesc = '02-REFER CARD ISSUER SPE. COND.';
    ELSEIF rc = '03' THEN SET rcDesc = '03-INVALID MERCHANT';
    ELSEIF rc = '04' THEN SET rcDesc = '04-CAPTURE';
    ELSEIF rc = '05' THEN SET rcDesc = '05-UNAUTHORISED USAGE';
    ELSEIF rc = '06' THEN SET rcDesc = '06-UNABLE TO PROCESS TXN';
    ELSEIF rc = '08' THEN SET rcDesc = '08-APPROVED - HONOR WITH IDENTIFICATION';
    ELSEIF rc = 'N2' THEN SET rcDesc = 'N2-PRE AUTH FULL';
    ELSEIF rc = 'N3' THEN SET rcDesc = 'N3-PRIVATE MAX ONLINE REFUND';
    ELSEIF rc = 'N4' THEN SET rcDesc = 'N4-PRIVATE MAX OFFLINE REFUND';
    ELSEIF rc = 'N5' THEN SET rcDesc = 'N5-PRIVATE MAX CR PER REFUND';
    ELSEIF rc = 'N6' THEN SET rcDesc = 'N6-MAX REFUND CR REACHED';
    ELSEIF rc = 'N7' THEN SET rcDesc = 'N7-CUSTOM NEG REASON';
    ELSEIF rc = 'N8' THEN SET rcDesc = 'N8-OVERFLOOR LIMIT';
    ELSEIF rc = 'N9' THEN SET rcDesc = 'N9-MAX NUM REFUND CR';
    ELSEIF rc = 'O0' THEN SET rcDesc = 'O0-REF FILE FULL';
    ELSEIF rc = 'O1' THEN SET rcDesc = 'O1-NEG FILE PROBLEM';
    ELSEIF rc = 'O2' THEN SET rcDesc = 'O2-ADVANCE LESS THAN MIN';
    ELSEIF rc = 'O3' THEN SET rcDesc = 'O3-DELINQUENT';
    ELSEIF rc = 'O4' THEN SET rcDesc = 'O4-OVER LIMIT TABLE';
    ELSEIF rc = 'O5' THEN SET rcDesc = 'O5-PRIVATE PIN REQUIRED';
    ELSEIF rc = 'O6' THEN SET rcDesc = 'O6-MOD 10 CHECK';
    ELSEIF rc = 'O7' THEN SET rcDesc = 'O7-FORCE POST';
    ELSEIF rc = 'O8' THEN SET rcDesc = 'O8-BAD PBF';
    ELSEIF rc = 'O9' THEN SET rcDesc = 'O9-NEG FILE PROBLEM';
    ELSEIF rc = 'P0' THEN SET rcDesc = 'P0-CAF FILE PROBLEM';
    ELSEIF rc = 'P1' THEN SET rcDesc = 'P1-DAILY LIMIT EXCEEDS';
    ELSEIF rc = 'P2' THEN SET rcDesc = 'P2-CAPF NOT FOUND';
    ELSEIF rc = 'P5' THEN SET rcDesc = 'P5-DELINQUENT';
    ELSEIF rc = 'Q0' THEN SET rcDesc = 'Q0-INVALID TRAN DATE';
    ELSEIF rc = 'Q1' THEN SET rcDesc = 'Q1-INVALID EXPIRATION DATE';
    ELSEIF rc = 'Q2' THEN SET rcDesc = 'Q2-INVALID TRANCODE';
    ELSEIF rc = 'Q3' THEN SET rcDesc = 'Q3-ADVANCE LESS THAN MIN';
    ELSEIF rc = 'Q4' THEN SET rcDesc = 'Q4-NUM OF TIMES EXCEEDS';
    ELSEIF rc = 'Q5' THEN SET rcDesc = 'Q5-DELINQUENT';
    ELSEIF rc = 'Q6' THEN SET rcDesc = 'Q6-OVER LIMIT TABLE';
    ELSEIF rc = 'Q7' THEN SET rcDesc = 'Q7-ADVANCE LESS AMT';
    ELSEIF rc = 'Q8' THEN SET rcDesc = 'Q8-ADMIN CARD NEEDED';
    ELSEIF rc = 'Q9' THEN SET rcDesc = 'Q9-ENTER LESSER AMT';
    ELSEIF rc = 'R0' THEN SET rcDesc = 'R0-APPROVED ADMIN REQ IN WINDOW';
    ELSEIF rc = 'R1' THEN SET rcDesc = 'R1-APPROVED ADMIN REQ OUT WINDOW';
    ELSEIF rc = 'R2' THEN SET rcDesc = 'R2-APPROVED ADMIN REQ ANYTIME';
    ELSEIF rc = 'R3' THEN SET rcDesc = 'R3-CHARGEBACK CUSTOMER FILE UPDATED';
    ELSEIF rc = 'R4' THEN SET rcDesc = 'R4-CHARGEBACK CUST.FILE UPDATED ACQR. NOT FOUND';
    ELSEIF rc = 'R5' THEN SET rcDesc = 'R5-CHARGEBACK INCORRECT PREFIX NUMBER';
    ELSEIF rc = 'R6' THEN SET rcDesc = 'R6-CHARGEBACK INCORRECT RSP CODE OR CPF CON';
    ELSEIF rc = 'R7' THEN SET rcDesc = 'R7-ADMIN TXN NOT SUPPORTED';
    ELSEIF rc = 'S4' THEN SET rcDesc = 'S4-PTLF IS FULL';
    ELSEIF rc = 'S5' THEN SET rcDesc = 'S5-APPROVED, CUSTOMER FILES NOT UPDATED';
    ELSEIF rc = 'S6' THEN SET rcDesc = 'S6-APPROVED, FILES NOT UPDATED ACQ. NOT FOUND';
    ELSEIF rc = 'S7' THEN SET rcDesc = 'S7-ACCEPTED, INCORRECT DESTINATION';
    ELSEIF rc = 'S8' THEN SET rcDesc = 'S8-ADMIN FILE ERROR';
    ELSEIF rc = 'S9' THEN SET rcDesc = 'S9-SECURITY DEVICE ERROR';
    ELSEIF rc = 'T1' THEN SET rcDesc = 'T1-INVALID AMT';
    ELSEIF rc = 'T2' THEN SET rcDesc = 'T2-FORMAT ERROR';
    ELSEIF rc = 'T3' THEN SET rcDesc = 'T3-NO CARD RECRD';
    ELSEIF rc = 'T4' THEN SET rcDesc = 'T4-INVALID AMT';
    ELSEIF rc = 'T5' THEN SET rcDesc = 'T5-CAF STATUS INACTIVE';
    ELSEIF rc = 'T6' THEN SET rcDesc = 'T6-BAD UAF';
    ELSEIF rc = 'T7' THEN SET rcDesc = 'T7-RESERVED FOR PRIVATE USE';
    ELSEIF rc = 'T8' THEN SET rcDesc = 'T8-ERROR, A/C PROBLEM';
    ELSEIF rc = 'W8' THEN SET rcDesc = 'W8-CONSULTATION FOR PROD W/OUT INTEREST';
    ELSEIF rc = 'W9' THEN SET rcDesc = 'W9-INVALID MENU';
    END IF;
	-- return the customer level
	RETURN (rcDesc);
END$$
DELIMITER ;
SELECT ResponseCodeDescription('12');

-- * ##############################################################


DROP FUNCTION IF EXISTS ChileEstadoAccountType;
DELIMITER $$
CREATE FUNCTION ChileEstadoAccountType(bankCode VARCHAR(4), acType VARCHAR(4)) RETURNS VARCHAR(4)
DETERMINISTIC
COMMENT '
# Func Name :- ChileEstadoAccountType
# Created By :- Dishant Raut [21Dec2022]
# Updated By :- Dishant Raut [21Dec2022]
# Params :- BankCode + AcType
# Desc :- Get New Account Type Base On Combo Of BC & AT
# Exec :- SELECT ChileEstadoAccountType("0210", "200000");
# Drop :- DROP FUNCTION IF EXISTS ChileEstadoAccountType;
'
BEGIN
    DECLARE updatedAcType VARCHAR(4);
    -- * Banco Chile : Updated Account Type
    IF bankCode = "001" and acType = "3" THEN SET updatedAcType = "01";
    ELSEIF bankCode = "504" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "028" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "055" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "027" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "016" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "507" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "051" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "009" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "039" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "053" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "037" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "049" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "672" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "031" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "014" and acType = "3" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "001" and acType = "22" THEN SET updatedAcType = "01";
    ELSEIF bankCode = "001" and acType = "4" THEN SET updatedAcType = "06";
    ELSEIF bankCode = "504" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "504" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "028" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "028" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "055" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "055" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "027" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "027" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "016" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "016" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "507" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "507" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "051" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "051" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "009" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "009" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "039" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "039" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "053" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "053" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "037" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "037" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "049" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "049" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "672" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "672" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "031" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "031" and acType = "4" THEN SET updatedAcType = "08";
    ELSEIF bankCode = "014" and acType = "22" THEN SET updatedAcType = "07";
    ELSEIF bankCode = "014" and acType = "4" THEN SET updatedAcType = "08";
    -- * Banco Estado : Updated Account Type
    ELSEIF bankCode = "012" and acType = "3" THEN SET updatedAcType = "01";
    ELSEIF bankCode = "012" and acType = "4" THEN SET updatedAcType = "02";
    ELSEIF bankCode = "012" and acType = "22" THEN SET updatedAcType = "22";
    END IF;
	RETURN (updatedAcType);
END$$
DELIMITER ;
SELECT ChileEstadoAccountType('014', '4');
SELECT ChileEstadoAccountType('053', '4');
SELECT ChileEstadoAccountType('053', '22');
SELECT ChileEstadoAccountType('012', '3');
SELECT ChileEstadoAccountType('012', '4');
SELECT ChileEstadoAccountType('012', '22');
