SELECT COUNT(*) AS user FROM users;
SELECT COUNT(*) AS ret_id FROM retailerid;
SELECT COUNT(*) AS inst_id FROM institutionid;
SELECT COUNT(*) AS ret_acco FROM retaileraccount;
SELECT COUNT(*) AS enab_val FROM enablevalidations;
SELECT COUNT(*) AS ret_comm FROM retailercommissions;
SELECT COUNT(*) AS catalog FROM configurationcatalogs;
SELECT COUNT(*) AS ret_comm_onoff FROM retailercommissionsonoff;


SELECT
    institution_id AS InsId, retailer_id AS RetId, channel AS Chn, commision_type AS Type,
    commision_sub_type AS SubType, card_type AS Card, Mcc, Bin, transaction_identifier AS Iden,
    status, rubro
FROM retailercommissionrules
WHERE institution_id = "2003";

SELECT
    institution_id AS InsId, retailer_id AS RetId, channel AS Chn, message_type AS MT,
    processing_code AS PC, response_code AS RC, 
    debit_value AS Db, credit_value AS Cr, prepaid_value AS Pr, 
    mcc, mcc_debit_value AS MDb, mcc_credit_value AS MCr, mcc_prepaid_value AS MPr,
    bin, bin_value AS Bin, domestic_value AS Dv, international_value AS Iv,
    rubro, rubro_debit_value AS RDb, rubro_credit_value AS RCr, rubro_prepaid_value AS RPr
FROM retailercommissionvalues
WHERE institution_id = "0014";

SELECT
    PrimaryAcCOUNTNumberPAN AS BIN, MerchantTypeCode AS MCC, CardAcceptorIdentification AS RetId, AcquiringInstitutionIdentification AS Swt,
    MessageType AS MT, ProcessingCode AS PC, ResponseCode AS RC, ChannelType AS Chn,
    RetCardTypeCommision AS CC, RetCardTypePromotion AS CP,
    RetBinCommision AS BC, RetBinPromotion AS BP,
    RetMccCommision AS MC, RetMccPromotion AS MP,
    RetTxnIdentifierCommision AS TIC, RetTxnIdentifierPromotion AS TIP,
    RetRubroCommision AS RC, RetRubroPromotion AS RP,
    Retailer AS RetCom, Acquirer AS AcqCom, Issuer AS IssCom,
    TotalCommissions AS TotCom, TotalPromotions AS TotPro,
    Retefuente, Reteica, Cree, Reteiva,
    TotalTaxes AS TotTax, TotalDisCOUNTs AS TotDis, TransactionAmount AS TotAmt, FinalAmount AS FinAmt
FROM
    iseretailer;


