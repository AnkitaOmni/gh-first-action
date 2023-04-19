from model import *
from datetime import datetime



def copyToAcquirerExtract():
    query = """INSERT INTO acquirerextract SELECT * FROM acquireroriginal;"""
    try:
        cursor = myDB.execute_sql(query)
        print("Copied Transactions To AcquirerExtract Table at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        # print("ExtarctFileOriginal To ExtarctFile Copying Failed", e)
        print("Transactions Not Copied To AcquirerExtract Table", e)


def copyToFullDayAcquirerExtract():
    """ CC0024 Specific """
    query = """INSERT INTO fulldayacquirerextract SELECT * FROM fulldayacquireroriginal;"""
    try:
        cursor = myDB.execute_sql(query)
        print("Copied Transactions To Full Day AcquirerExtract Table at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        # print("ExtarctFileOriginal To ExtarctFile Copying Failed", e)
        print("Transactions Not Copied To Full Day AcquirerExtract Table", e)


def copyToIssuerExtract():
    query = """INSERT INTO issuerextract SELECT * FROM issueroriginal;"""
    try:
        cursor = myDB.execute_sql(query)
        print("Copied Transactions To IssuerExtract Table at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        # print("ExtarctFileOriginal To ExtarctFile Copying Failed", e)
        print("Transactions Not Copied To IssuerExtract Table", e)


def copyToIssuerExtractCopy():
    query = """
INSERT IGNORE INTO issuerextractcopy	
(id,TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime,
LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode,
ForwardingInstitutionCountryCode, PointofServiceEntryModeCode,CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode,
AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse,
ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData,
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC,
CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3,
PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType,IssuerRRN)
SELECT 	
NULL, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime,
LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode,
ForwardingInstitutionCountryCode, PointofServiceEntryModeCode,CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode,
AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse,
ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData,
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC,
CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3,
PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType,IssuerRRN
FROM issueroriginal;
"""
    try:
        cursor = myDB.execute_sql(query)
        print("Copied Transactions To IssuerExtractCopy Table at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        del cursor
    except Exception as e:
        # print("ExtarctFileOriginal To ExtarctFile Copying Failed", e)
        print("Transactions Not Copied To IssuerExtractCopy Table", e)
        del e


def copyToIssuerHistory():
    query = """
INSERT IGNORE INTO transactionhistoryissuer	
(id,TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime,
LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode,
ForwardingInstitutionCountryCode, PointofServiceEntryModeCode,CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode,
AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse,
ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData,
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC,
CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3,
PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType,IssuerRRN)
SELECT 	
NULL, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime,
LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode,
ForwardingInstitutionCountryCode, PointofServiceEntryModeCode,CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode,
AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse,
ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData,
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC,
CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3,
PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType,IssuerRRN
FROM issuerextractcopy;
"""
    try:
        cursor = myDB.execute_sql(query)
        print("Copied Transactions To TransactionHistoryIssuer Table at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        del cursor
    except Exception as e:
        # print("ExtarctFileOriginal To ExtarctFile Copying Failed", e)
        print("Transactions Not Copied To TransactionHistoryIssuer Table", e)
        del e


def acquirer_retailer_exist_validation():
    query="""
INSERT INTO acquirernotvalid 
(TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, Validation, ExtarctFileId)
select
e.TimeStamp, e.MessageType, e.PrimaryBitMap, e.SecondaryBitMap, e.PrimaryAccountNumberPAN, e.ProcessingCode, e.TransactionAmount, e.TransactionAmountCardholderBilling, e.TransmissionDateandTime, e.ConversionRateCardholderBilling, e.SystemsTraceAuditNumber, e.LocalTransactionTime, e.LocalTransactionDate, e.ExpirationDate, e.SettlementDate, e.CaptureDate, e.MerchantTypeCode, e.AcquirerInstitutionCountryCode, e.IssuerInstututionCountryCode, e.ForwardingInstitutionCountryCode, e.PointofServiceEntryModeCode, e.CardSequenceNumber, e.NetworkInternationalIdentifierCode, e.PointofServiceConditionCode, e.AcquiringInstitutionIdentification, e.ForwardingInstitutionIdentification, e.Track2Data, e.RetrievalReferenceNumber, e.AuthorizationIdentificationResponse, e.ResponseCode, e.CardAcceptorTerminalIdentification, e.CardAcceptorIdentification, e.CardAcceptorNameLocation, e.Track1Data, e.RetailerData, e.TransactionCurrencyCode, e.CurrencyCodeCardholderBilling, e.PersonalIdentificationNumberPINData, e.AdditionalAmount, e.IntegratedCircuitCardICC, e.CardholdersIdentificationNumberandName, e.AdditionalAmounts, e.TerminalData, e.CardData, e.TerminalPostalCode, e.Token1, e.Token2, e.Token3, e.PrimaryMessageAuthenticationCodeMAC, e.ChannelType, e.CardType, e.NoOfInstallment, e.InstallmentType, e.IssuerRRN
,CONCAT("Retailer ", e.CardAcceptorIdentification ," does not exists, ") as Validation
, e.id
FROM acquireroriginal as e
LEFT JOIN retailerid as r ON 
e.CardAcceptorIdentification =  r.retailerId
AND e.AcquiringInstitutionIdentification =  r.EntityId
WHERE r.retailerId is null
"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Acquirer Retailer Exist Validation Failed",e)


def acquirer_retailer_exist_validation_fullday():
    """ CC0024 Specific """
    query="""
INSERT INTO fulldayacquirernotvalid 
(TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, Validation, ExtarctFileId)
select
e.TimeStamp, e.MessageType, e.PrimaryBitMap, e.SecondaryBitMap, e.PrimaryAccountNumberPAN, e.ProcessingCode, e.TransactionAmount, e.TransactionAmountCardholderBilling, e.TransmissionDateandTime, e.ConversionRateCardholderBilling, e.SystemsTraceAuditNumber, e.LocalTransactionTime, e.LocalTransactionDate, e.ExpirationDate, e.SettlementDate, e.CaptureDate, e.MerchantTypeCode, e.AcquirerInstitutionCountryCode, e.IssuerInstututionCountryCode, e.ForwardingInstitutionCountryCode, e.PointofServiceEntryModeCode, e.CardSequenceNumber, e.NetworkInternationalIdentifierCode, e.PointofServiceConditionCode, e.AcquiringInstitutionIdentification, e.ForwardingInstitutionIdentification, e.Track2Data, e.RetrievalReferenceNumber, e.AuthorizationIdentificationResponse, e.ResponseCode, e.CardAcceptorTerminalIdentification, e.CardAcceptorIdentification, e.CardAcceptorNameLocation, e.Track1Data, e.RetailerData, e.TransactionCurrencyCode, e.CurrencyCodeCardholderBilling, e.PersonalIdentificationNumberPINData, e.AdditionalAmount, e.IntegratedCircuitCardICC, e.CardholdersIdentificationNumberandName, e.AdditionalAmounts, e.TerminalData, e.CardData, e.TerminalPostalCode, e.Token1, e.Token2, e.Token3, e.PrimaryMessageAuthenticationCodeMAC, e.ChannelType, e.CardType, e.NoOfInstallment, e.InstallmentType, e.IssuerRRN
,CONCAT("Retailer ", e.CardAcceptorIdentification ," does not exists, ") as Validation
, e.id
FROM fulldayacquireroriginal as e
LEFT JOIN retailerid as r ON 
e.CardAcceptorIdentification =  r.retailerId
AND e.AcquiringInstitutionIdentification =  r.EntityId
WHERE r.retailerId is null
"""
    try:
        myDB.execute_sql(query)
        #validated = cursor.fetchall()
        #validated = list(validated)
        #return validated
    except Exception as e:
        print("Acquirer Retailer Full Day Exist Validation Failed",e)


def issuer_retailer_exist_validation():
    query="""
INSERT INTO issuernotvalid 
(TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, Validation, ExtarctFileId)
select
e.TimeStamp, e.MessageType, e.PrimaryBitMap, e.SecondaryBitMap, e.PrimaryAccountNumberPAN, e.ProcessingCode, e.TransactionAmount, e.TransactionAmountCardholderBilling, e.TransmissionDateandTime, e.ConversionRateCardholderBilling, e.SystemsTraceAuditNumber, e.LocalTransactionTime, e.LocalTransactionDate, e.ExpirationDate, e.SettlementDate, e.CaptureDate, e.MerchantTypeCode, e.AcquirerInstitutionCountryCode, e.IssuerInstututionCountryCode, e.ForwardingInstitutionCountryCode, e.PointofServiceEntryModeCode, e.CardSequenceNumber, e.NetworkInternationalIdentifierCode, e.PointofServiceConditionCode, e.AcquiringInstitutionIdentification, e.ForwardingInstitutionIdentification, e.Track2Data, e.RetrievalReferenceNumber, e.AuthorizationIdentificationResponse, e.ResponseCode, e.CardAcceptorTerminalIdentification, e.CardAcceptorIdentification, e.CardAcceptorNameLocation, e.Track1Data, e.RetailerData, e.TransactionCurrencyCode, e.CurrencyCodeCardholderBilling, e.PersonalIdentificationNumberPINData, e.AdditionalAmount, e.IntegratedCircuitCardICC, e.CardholdersIdentificationNumberandName, e.AdditionalAmounts, e.TerminalData, e.CardData, e.TerminalPostalCode, e.Token1, e.Token2, e.Token3, e.PrimaryMessageAuthenticationCodeMAC, e.ChannelType, e.CardType, e.NoOfInstallment, e.InstallmentType, e.IssuerRRN
,CONCAT("Retailer ", e.CardAcceptorIdentification ," does not exists, ") as Validation
, e.id
FROM issueroriginal as e
LEFT JOIN retailerid as r ON 
e.CardAcceptorIdentification =  r.retailerId
AND e.AcquiringInstitutionIdentification =  r.EntityId
WHERE r.retailerId is null
"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Issuer Retailer Exist Validation Failed",e)


def clean_acquirer_validated():
    query="""
DELETE acquireroriginal
FROM acquireroriginal
LEFT JOIN acquirernotvalid 
ON acquireroriginal.id = acquirernotvalid.ExtarctFileId
WHERE acquirernotvalid.ExtarctFileId IS NOT null
"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Acquirer Non Validated Cleaning Failed",e)


def clean_acquirer_validated_fullday():
    """ CC0024 Specific """
    query="""
DELETE fulldayacquireroriginal
FROM fulldayacquireroriginal
LEFT JOIN fulldayacquirernotvalid 
ON fulldayacquireroriginal.id = fulldayacquirernotvalid.ExtarctFileId
WHERE fulldayacquirernotvalid.ExtarctFileId IS NOT null
"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Acquirer Non Validated Cleaning Failed",e)


def clean_issuer_validated():
    query="""
DELETE issueroriginal
FROM issueroriginal
LEFT JOIN issuernotvalid 
ON issueroriginal.id = issuernotvalid.ExtarctFileId
WHERE issuernotvalid.ExtarctFileId IS NOT null
"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Isuuer Non Validated Cleaning Failed",e)


def clean_file_adjustments():
    query="""truncate fileadjustments"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Cleaning adj",e)


def clean_manual_adjustments():
    query="""truncate manualadjustmentsextractfile"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Cleaning adj",e)


def clean_all_adjustments():
    query="""truncate alladjustments"""
    try:
        myDB.execute_sql(query)
    except Exception as e:
        print("Cleaning all adj",e)


def clean_acquirer_extract_tables():
    try:
        query1 = """truncate acquirerduplicates;"""
        myDB.execute_sql(query1)
        query2 = """truncate acquireroriginal;"""
        myDB.execute_sql(query2)
        query3 = """truncate acquirernotvalid;"""
        myDB.execute_sql(query3)
        query4 = """truncate acquirerextract;"""
        myDB.execute_sql(query4)
        query5 = """truncate acquirerreversalsuccesspurchacedecline;"""
        myDB.execute_sql(query5)
        del query1, query2, query3, query4, query5
        # * Commented By Dishant [27 Sep 2021] :- Error with truncate_tables()
        # myDB.truncate_tables([AcquirerExtract, ExtractFileOriginal, ExtractFileNotValidated, ExtractReversals])
        print(f"Cleared Previous Acquirer Transactions at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    except Exception as e:
        print(f"Error In Clearing Previous Acquirer Transactions - {e}")
        del e


def fullday_clean_acquirer_extract_tables():
    """ CC0024 Specific """
    try:
        query1 = """truncate fulldayacquirerduplicates;"""
        myDB.execute_sql(query1)
        query2 = """truncate fulldayacquireroriginal;"""
        myDB.execute_sql(query2)
        query3 = """truncate fulldayacquirernotvalid;"""
        myDB.execute_sql(query3)
        query4 = """truncate fulldayacquirerextract;"""
        myDB.execute_sql(query4)
        query5 = """truncate currentdatetransactionhistory;"""
        myDB.execute_sql(query5)
        del query1, query2, query3, query4, query5
        print(f"Cleared Previous Full Day Acquirer Transactions at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    except Exception as e:
        print(f"Error In Clearing Full Day Previous Acquirer Transactions - {e}")
        del e


def clean_issuer_extract_tables():
    try:
        query1 = """truncate issuerduplicates;"""
        myDB.execute_sql(query1)
        query2 = """truncate issueroriginal;"""
        myDB.execute_sql(query2)
        query3 = """truncate issuernotvalid;"""
        myDB.execute_sql(query3)
        query4 = """truncate issuerextract;"""
        myDB.execute_sql(query4)
        del query1, query2, query3, query4
        print(f"Cleared Previous Issuer Transactions at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    except Exception as e:
        print(f"Error In Clearing Previous Issuer Transactions - {e}")
        del e


def clean_liquidation_tables():
    try:
        myDB.execute_sql("""truncate iseretailer""")
        # myDB.truncate_tables([ISERetailer])
        # myDB.truncate_tables([iseacquirer,isedeposit,iseinterchange,iseissuer,iseretailer,isetransaction,iseuser,tcr,depositfile])
        # myDB.truncate_tables([localnetinterchangeinc,localnetinterchangenet,localnetinterchangeout])
        print(f"Cleared Previous Liquidated Transactions at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    except Exception as e:
        print(f"Previous Liquidated Transactions Not Cleared at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
        print(f"Error = {e}")
        del e


def truncate_issuerextractcopy_table():
    """ Clear Issuer Table i.e issuerextractcopy """
    try:
        myDB.execute_sql("""truncate issuerextractcopy;""")
        print(f"Cleared Previous Transactions Of Issuer Extract Copy at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    except Exception as e:
        print(f"Previous Transactions Of Issuer Extract Copy Not Cleared at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
        print("Error = {}".format(e))
        del e


def insert_reversalsuccess():
    """
    * Mantis 728 Specific :-
    Insert Reversal success of declined purchase txn of Acq side into acquirerreversalsuccesspurchacedecline table 
    """
    query = """
INSERT IGNORE INTO acquirerreversalsuccesspurchacedecline
SELECT * FROM acquireroriginal
WHERE
    ResponseCode = "00"
    AND MessageType = "0420"
    AND ProcessingCode = "000000"
    AND (
        RetrievalReferenceNumber,
        TransmissionDateandTime,
        Track2Data,
        CardAcceptorIdentification,
        ForwardingInstitutionIdentification,
        AcquiringInstitutionIdentification
    ) IN (
        SELECT
            RetrievalReferenceNumber,
            TransmissionDateandTime,
            Track2Data,
            CardAcceptorIdentification,
            ForwardingInstitutionIdentification,
            AcquiringInstitutionIdentification
        FROM
            acquireroriginal
        WHERE
            ResponseCode != "00"
            AND MessageType = "0210"
            AND ProcessingCode = "000000"
    );
"""

    try:
        myDB.execute_sql(query)
       
    except Exception as e:
        print("Reversal Success From AcquirerOriginal Inserted into New table Failed", e)


def insert_to_transactionhistory():
    """
    * Mantis 728 Specific :-
    Insert Reversal success of declined purchase txn into history table i.e. transactionhistory table 
    from acquirerreversalsuccesspurchacedecline   
    """ 
    query = """
INSERT IGNORE INTO transactionhistory
        (id, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
        TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
        LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
        AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
        CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
        ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
        CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
        TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
        IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
        Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN)
SELECT        
        NULL, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
        TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
        LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
        AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
        CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
        ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
        CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
        TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
        IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
        Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN
FROM acquirerreversalsuccesspurchacedecline;
    """    
    myDB.execute_sql(query)


def cleanReversalSuccess():
    """
    * Mantis 728 Specific :-
    Delete Reversal success of declined purchase txn FROM acquireroriginal table
    """ 
    query = """
DELETE FROM acquireroriginal
WHERE ResponseCode = "00" AND MessageType = "0420" AND ProcessingCode = "000000"
AND RetrievalReferenceNumber IN 
(SELECT RetrievalReferenceNumber FROM acquirerreversalsuccesspurchacedecline);
"""
    try: myDB.execute_sql(query)
    except Exception as e: print(f"Cleaning declined Failed : {e}")


def UI_HomeTab():
    try:
        query1 = """SELECT COUNT(*) FROM retailerid;"""
        retLoad = myDB.execute_sql(query1).fetchall()[0][0]
        # print(f"retLoad : {retLoad}")
        query2 = """SELECT COUNT(*) FROM acquirernotvalid WHERE ResponseCode = "00";"""
        invAppCnt=myDB.execute_sql(query2).fetchall()[0][0]
        # print(f"invAppCnt : {invAppCnt}")
        query3 = """SELECT DISTINCT (ResponseCode) FROM acquirernotvalid;"""
        disResCodes=[distRespCode[0] for distRespCode in myDB.execute_sql(query3).fetchall()]
        # print(f"disResCodes : {disResCodes}")
        query4 = """SELECT COUNT(*) FROM iseretailer;"""
        iseRet=myDB.execute_sql(query4).fetchall()[0][0]
        # print(f"iseRet : {iseRet}")
        query5 = """SELECT COUNT(*) FROM issuerextractcopy;"""
        issExtCp=myDB.execute_sql(query5).fetchall()[0][0]
        # print(f"issExtCp : {issExtCp}")
        query6 = """SELECT table1.Brand, AppCnt, DecCnt FROM(SELECT ForwardingInstitutionIdentification AS Brand,COUNT(ForwardingInstitutionIdentification) AS AppCnt FROM iseretailer WHERE ResponseCode = "00" GROUP BY ForwardingInstitutionIdentification) as table1 INNER JOIN (SELECT ForwardingInstitutionIdentification AS Brand,COUNT(ForwardingInstitutionIdentification) AS DecCnt FROM iseretailer WHERE ResponseCode != "00" GROUP BY ForwardingInstitutionIdentification) as table2 ON table1.Brand = table2.Brand;"""
        brCnt=myDB.execute_sql(query6).fetchall()
        # print(f"brCnt : {brCnt}")
        query7 = """SELECT table1.Brand, AppCnt, DecCnt FROM(SELECT AcquiringInstitutionIdentification AS Brand,COUNT(AcquiringInstitutionIdentification) AS AppCnt FROM iseretailer WHERE ResponseCode = "00" GROUP BY AcquiringInstitutionIdentification) as table1 INNER JOIN (SELECT AcquiringInstitutionIdentification AS Brand,COUNT(AcquiringInstitutionIdentification) AS DecCnt FROM iseretailer WHERE ResponseCode != "00" GROUP BY AcquiringInstitutionIdentification) as table2 ON table1.Brand = table2.Brand;"""
        swCnt=myDB.execute_sql(query7).fetchall()
        # print(f"swCnt : {swCnt}")
        return retLoad, invAppCnt, disResCodes, iseRet, issExtCp, brCnt, swCnt
    except Exception:
        pass


###################### * CCX24 * ######################

CCX24_query1 = """
-- * CCX24 Update Retailer Data For [ fulldaytransactionretailerhistory ] Rechazado IDP 
WITH cte_two AS (
    WITH cte_one AS (
        SELECT DISTINCT CONCAT(RetId,"#^#",InsId) AS RetId_InsId, IDP
        FROM fulldaytransactionretailerhistory
        WHERE IDP IN (SELECT DISTINCT DocNum FROM chileidpupdate)
    UNION
        SELECT DISTINCT CONCAT(RetId,"#^#",InsId) AS RetId_InsId, IDP
        FROM fulldaytransactionretailerhistory
        WHERE IDP IN (SELECT DISTINCT IDP FROM estadoidpupdate)
    )
    SELECT
        IDP, RetailerId AS RetId, EntityId AS InsId, IdentificationNumber AS Ruth, 
        SUBSTRING_INDEX (IdentificationNumber, '-', -1) AS Dv, Name, AccountNumber AS AcNum, 
        CASE WHEN BankCode = "012" THEN "Estado" ELSE "991" END AS DocType, 
        IFNULL(ChileEstadoAccountType(BankCode, MovmentType), "  ") AS AcType,
        BankCode AS BankCode
    FROM
    (
        SELECT * FROM cte_one cto 
        INNER JOIN retailerid rid 
        ON CONCAT(rid.RetailerId, "#^#", rid.EntityId) = cto.RetId_InsId
    )
    AS LatestData
)
UPDATE fulldaytransactionretailerhistory AS fthr, cte_two AS ct2
SET
    fthr.Ruth = ct2.Ruth,
    fthr.Dv = ct2.Dv,
    fthr.RetName = ct2.Name,
    fthr.AcNum = ct2.AcNum,
    fthr.DocType = ct2.DocType,
    fthr.AcType = ct2.AcType,
    fthr.BankCode = ct2.BankCode
WHERE
fthr.IDP = ct2.IDP;
"""

###################### * CCX35 * ######################

CCX35_query1 = """
SELECT RetId, InsId, COUNT(IDP) FROM estadoidpupdate
GROUP BY CONCAT(RetId, "#^#", InsId)
HAVING COUNT(CONCAT(RetId, "#^#", InsId)) > 1;
"""

CCX35_query2 = """
SELECT RetId, InsId, COUNT(DocNum) FROM chileidpupdate
GROUP BY CONCAT(RetId, "#^#", InsId)
HAVING COUNT(CONCAT(RetId, "#^#", InsId)) > 1;
"""

###################### * base_liquidation.py * ######################

makeIseretailerCopy = """
INSERT IGNORE INTO iseretailercopy
SELECT * FROM iseretailer;
"""

insertIgnoreToTransactionHistory = """
INSERT IGNORE INTO transactionhistory
        
(id, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, 
RetCardTypeCommision,RetCardTypePromotion, RetBinCommision,RetBinPromotion, RetMccCommision,
RetMccPromotion,RetTxnIdentifierCommision,RetTxnIdentifierPromotion,RetRubroCommision, RetRubroPromotion,RetRegionCommision,RetRegionPromotion ,Retailer, Acquirer, Issuer, TotalCommissions, 
Retefuente, Reteica, Cree, Reteiva, TotalTaxes, TotalDiscounts, FinalAmount)

SELECT 
        
NULL, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, RetCardTypeCommision,RetCardTypePromotion, RetBinCommision,RetBinPromotion, RetMccCommision,
RetMccPromotion,RetTxnIdentifierCommision,RetTxnIdentifierPromotion,RetRubroCommision, RetRubroPromotion,RetRegionCommision,RetRegionPromotion
, Retailer, Acquirer, Issuer, TotalCommissions, 
Retefuente, Reteica, Cree, Reteiva, TotalTaxes, TotalDiscounts, FinalAmount

FROM iseretailercopy;
"""


insertToUpdate_TH_ISERetailer = """
INSERT INTO
    update_th_iseretailer
SELECT
    isecp.*
FROM
    iseretailercopy AS isecp
    JOIN transactionhistory AS th ON isecp.RetrievalReferenceNumber = th.RetrievalReferenceNumber
    AND isecp.TransmissionDateandTime = th.TransmissionDateandTime
    AND isecp.Track2Data = th.Track2Data
    AND isecp.MessageType = th.MessageType
    AND isecp.ProcessingCode = th.ProcessingCode
    AND isecp.ResponseCode = th.ResponseCode
    AND isecp.CardAcceptorIdentification = th.CardAcceptorIdentification;
"""


deleteCommonTrnx = """
DELETE isecp
FROM
    iseretailercopy AS isecp
    INNER JOIN transactionhistory AS th ON isecp.RetrievalReferenceNumber = th.RetrievalReferenceNumber
    AND isecp.TransmissionDateandTime = th.TransmissionDateandTime
    AND isecp.Track2Data = th.Track2Data
    AND isecp.MessageType = th.MessageType
    AND isecp.ProcessingCode = th.ProcessingCode
    AND isecp.ResponseCode = th.ResponseCode
    AND isecp.CardAcceptorIdentification = th.CardAcceptorIdentification
"""


insertToTHAfterInner = """
INSERT IGNORE INTO transactionhistory
        
(id, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, 
RetCardTypeCommision,RetCardTypePromotion, RetBinCommision,RetBinPromotion, RetMccCommision,
RetMccPromotion,RetTxnIdentifierCommision,RetTxnIdentifierPromotion,RetRubroCommision, RetRubroPromotion,RetRegionCommision,RetRegionPromotion, Retailer, Acquirer, Issuer, TotalCommissions, 
Retefuente, Reteica, Cree, Reteiva, TotalTaxes, TotalDiscounts, FinalAmount)

SELECT 
        
NULL, TimeStamp, MessageType, PrimaryBitMap, SecondaryBitMap, PrimaryAccountNumberPAN, ProcessingCode, TransactionAmount, 
TransactionAmountCardholderBilling, TransmissionDateandTime, ConversionRateCardholderBilling, SystemsTraceAuditNumber, 
LocalTransactionTime, LocalTransactionDate, ExpirationDate, SettlementDate, CaptureDate, MerchantTypeCode, 
AcquirerInstitutionCountryCode, IssuerInstututionCountryCode, ForwardingInstitutionCountryCode, PointofServiceEntryModeCode, 
CardSequenceNumber, NetworkInternationalIdentifierCode, PointofServiceConditionCode, AcquiringInstitutionIdentification, 
ForwardingInstitutionIdentification, Track2Data, RetrievalReferenceNumber, AuthorizationIdentificationResponse, ResponseCode, 
CardAcceptorTerminalIdentification, CardAcceptorIdentification, CardAcceptorNameLocation, Track1Data, RetailerData, 
TransactionCurrencyCode, CurrencyCodeCardholderBilling, PersonalIdentificationNumberPINData, AdditionalAmount, 
IntegratedCircuitCardICC, CardholdersIdentificationNumberandName, AdditionalAmounts, TerminalData, CardData, TerminalPostalCode, 
Token1, Token2, Token3, PrimaryMessageAuthenticationCodeMAC, ChannelType, CardType, NoOfInstallment, InstallmentType, IssuerRRN, 
RetCardTypeCommision,RetCardTypePromotion, RetBinCommision,RetBinPromotion, RetMccCommision,
RetMccPromotion,RetTxnIdentifierCommision,RetTxnIdentifierPromotion,RetRubroCommision, RetRubroPromotion,RetRegionCommision,RetRegionPromotion, Retailer, Acquirer, Issuer, TotalCommissions, 
Retefuente, Reteica, Cree, Reteiva, TotalTaxes, TotalDiscounts, FinalAmount

FROM iseretailercopy;
"""


updateTH = """
UPDATE transactionhistory th, update_th_iseretailer uth_ise SET 
    th.RetCardTypeCommision = uth_ise.RetCardTypeCommision,
    th.RetCardTypePromotion = uth_ise.RetCardTypePromotion,
    th.RetBinCommision = uth_ise.RetBinCommision,
    th.RetBinPromotion = uth_ise.RetBinPromotion,
    th.RetMccCommision = uth_ise.RetMccCommision,
    th.RetMccPromotion = uth_ise.RetMccPromotion,
    th.RetTxnIdentifierCommision = uth_ise.RetTxnIdentifierCommision,
    th.RetTxnIdentifierPromotion = uth_ise.RetTxnIdentifierPromotion,
    th.RetRubroCommision = uth_ise.RetRubroCommision,
    th.RetRubroPromotion = uth_ise.RetRubroPromotion,
    th.RetRegionCommision = uth_ise.RetRegionCommision,
    th.RetRegionPromotion = uth_ise.RetRegionPromotion,
    th.Retailer = uth_ise.Retailer,
    th.Acquirer = uth_ise.Acquirer,
    th.Issuer = uth_ise.Issuer,
    th.TotalCommissions = uth_ise.TotalCommissions,
    th.Retefuente = uth_ise.Retefuente,
    th.Reteica = uth_ise.Reteica,
    th.Cree = uth_ise.Cree,
    th.Reteiva = uth_ise.Reteiva,
    th.TotalTaxes = uth_ise.TotalTaxes,
    th.TotalDiscounts = uth_ise.TotalDiscounts,
    th.FinalAmount = uth_ise.FinalAmount,
    th.PrimaryBitMap = uth_ise.PrimaryBitMap
WHERE 
    uth_ise.RetrievalReferenceNumber = th.RetrievalReferenceNumber and
    uth_ise.TransmissionDateandTime = th.TransmissionDateandTime and
    uth_ise.Track2Data = th.Track2Data and
    uth_ise.MessageType = th.MessageType and
    uth_ise.ProcessingCode = th.ProcessingCode and
    uth_ise.ResponseCode = th.ResponseCode and 
    uth_ise.CardAcceptorIdentification = th.CardAcceptorIdentification;
"""



if __name__ == '__main__':
    pass