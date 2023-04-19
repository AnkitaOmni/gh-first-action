from model import *
from datetime import datetime

column=[NewISERetailer.TimeStamp,NewISERetailer.MessageType,NewISERetailer.PrimaryBitMap,NewISERetailer.SecondaryBitMap,NewISERetailer.PrimaryAccountNumberPAN,
        NewISERetailer.ProcessingCode,NewISERetailer.TransactionAmount,NewISERetailer.TransactionAmountCardholderBilling,NewISERetailer.TransmissionDateandTime,
        NewISERetailer.ConversionRateCardholderBilling,NewISERetailer.SystemsTraceAuditNumber,NewISERetailer.LocalTransactionTime,NewISERetailer.LocalTransactionDate,
        NewISERetailer.ExpirationDate,NewISERetailer.SettlementDate,NewISERetailer.CaptureDate,NewISERetailer.MerchantTypeCode,NewISERetailer.AcquirerInstitutionCountryCode,
        NewISERetailer.IssuerInstututionCountryCode,NewISERetailer.ForwardingInstitutionCountryCode,NewISERetailer.PointofServiceEntryModeCode,NewISERetailer.CardSequenceNumber,
        NewISERetailer.NetworkInternationalIdentifierCode,NewISERetailer.PointofServiceConditionCode,NewISERetailer.AcquiringInstitutionIdentification,
        NewISERetailer.ForwardingInstitutionIdentification,NewISERetailer.Track2Data,NewISERetailer.RetrievalReferenceNumber,NewISERetailer.AuthorizationIdentificationResponse,
        NewISERetailer.ResponseCode,NewISERetailer.CardAcceptorTerminalIdentification,NewISERetailer.CardAcceptorIdentification,NewISERetailer.CardAcceptorNameLocation,
        NewISERetailer.Track1Data,NewISERetailer.RetailerData,NewISERetailer.TransactionCurrencyCode,NewISERetailer.CurrencyCodeCardholderBilling,NewISERetailer.PersonalIdentificationNumberPINData,
        NewISERetailer.AdditionalAmount,NewISERetailer.IntegratedCircuitCardICC,NewISERetailer.CardholdersIdentificationNumberandName,NewISERetailer.AdditionalAmounts,
        NewISERetailer.TerminalData,NewISERetailer.CardData,NewISERetailer.TerminalPostalCode,NewISERetailer.Token1,NewISERetailer.Token2,NewISERetailer.Token3,
        NewISERetailer.PrimaryMessageAuthenticationCodeMAC,NewISERetailer.ChannelType,NewISERetailer.CardType,NewISERetailer.NoOfInstallment,NewISERetailer.InstallmentType,NewISERetailer.IssuerRRN,
        NewISERetailer.TxnLoggingTime,NewISERetailer.RetCardTypeCommision,NewISERetailer.RetCardTypePromotion,NewISERetailer.RetBinCommision,NewISERetailer.RetBinPromotion,NewISERetailer.RetMccCommision,
        NewISERetailer.RetMccPromotion,NewISERetailer.RetTxnIdentifierCommision,NewISERetailer.RetTxnIdentifierPromotion,NewISERetailer.RetRubroCommision,NewISERetailer.RetRubroPromotion,
        NewISERetailer.RetRegionCommision,NewISERetailer.RetRegionPromotion,NewISERetailer.Retailer,NewISERetailer.Acquirer,NewISERetailer.Issuer,NewISERetailer.TotalCommissions,
        NewISERetailer.TotalPromotions,NewISERetailer.Retefuente,NewISERetailer.Reteica,NewISERetailer.Cree,NewISERetailer.Reteiva,NewISERetailer.TotalTaxes,NewISERetailer.TotalDiscounts,NewISERetailer.FinalAmount]


def copyToNewIsToTrnxHistory(retid,channel,insid):
    try:
        NewISERetailerTranxHistory.insert_from(NewISERetailer.select(NewISERetailer.TimeStamp,NewISERetailer.MessageType,NewISERetailer.PrimaryBitMap,NewISERetailer.SecondaryBitMap,NewISERetailer.PrimaryAccountNumberPAN,NewISERetailer.ProcessingCode,
        NewISERetailer.TransactionAmount,NewISERetailer.TransactionAmountCardholderBilling,NewISERetailer.TransmissionDateandTime,NewISERetailer.ConversionRateCardholderBilling,NewISERetailer.SystemsTraceAuditNumber,NewISERetailer.LocalTransactionTime,
        NewISERetailer.LocalTransactionDate,NewISERetailer.ExpirationDate,NewISERetailer.SettlementDate,NewISERetailer.CaptureDate,NewISERetailer.MerchantTypeCode,NewISERetailer.AcquirerInstitutionCountryCode,NewISERetailer.IssuerInstututionCountryCode,
        NewISERetailer.ForwardingInstitutionCountryCode,NewISERetailer.PointofServiceEntryModeCode,NewISERetailer.CardSequenceNumber,NewISERetailer.NetworkInternationalIdentifierCode,NewISERetailer.PointofServiceConditionCode,NewISERetailer.AcquiringInstitutionIdentification,
        NewISERetailer.ForwardingInstitutionIdentification,NewISERetailer.Track2Data,NewISERetailer.RetrievalReferenceNumber,NewISERetailer.AuthorizationIdentificationResponse,NewISERetailer.ResponseCode,NewISERetailer.CardAcceptorTerminalIdentification,
        NewISERetailer.CardAcceptorIdentification,NewISERetailer.CardAcceptorNameLocation,NewISERetailer.Track1Data,NewISERetailer.RetailerData,NewISERetailer.TransactionCurrencyCode,NewISERetailer.CurrencyCodeCardholderBilling,NewISERetailer.PersonalIdentificationNumberPINData,
        NewISERetailer.AdditionalAmount,NewISERetailer.IntegratedCircuitCardICC,NewISERetailer.CardholdersIdentificationNumberandName,NewISERetailer.AdditionalAmounts,NewISERetailer.TerminalData,NewISERetailer.CardData,NewISERetailer.TerminalPostalCode,
        NewISERetailer.Token1,NewISERetailer.Token2,NewISERetailer.Token3,NewISERetailer.PrimaryMessageAuthenticationCodeMAC,NewISERetailer.ChannelType,NewISERetailer.CardType,NewISERetailer.NoOfInstallment,NewISERetailer.InstallmentType,NewISERetailer.IssuerRRN,
        NewISERetailer.TxnLoggingTime,NewISERetailer.RetCardTypeCommision,NewISERetailer.RetCardTypePromotion,NewISERetailer.RetBinCommision,NewISERetailer.RetBinPromotion,NewISERetailer.RetMccCommision,NewISERetailer.RetMccPromotion,NewISERetailer.RetTxnIdentifierCommision,
        NewISERetailer.RetTxnIdentifierPromotion,NewISERetailer.RetRubroCommision,NewISERetailer.RetRubroPromotion,NewISERetailer.RetRegionCommision,NewISERetailer.RetRegionPromotion,NewISERetailer.Retailer,NewISERetailer.Acquirer,NewISERetailer.Issuer,
        NewISERetailer.TotalCommissions,NewISERetailer.TotalPromotions,NewISERetailer.Retefuente,NewISERetailer.Reteica,NewISERetailer.Cree,NewISERetailer.Reteiva,NewISERetailer.TotalTaxes,NewISERetailer.TotalDiscounts,NewISERetailer.FinalAmount)
        .where((NewISERetailer.AcquiringInstitutionIdentification == insid) & (NewISERetailer.ChannelType == channel) & (NewISERetailer.CardAcceptorIdentification.in_(tuple(retid)))),fields=column).execute()
        

        print("All {} Channel Copied To NewISERetailertranxhistory Table at {}".format(channel,datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        print("{} Channel Not Copied To NewISERetailertranxhistory Table", e).format(channel)


def delete_to_newiseretailer(Retailer_id,channel,insid):
    try:
        NewISERetailer.delete().where((NewISERetailer.ChannelType == channel) & (NewISERetailer.AcquiringInstitutionIdentification == insid) & NewISERetailer.CardAcceptorIdentification.in_(tuple(Retailer_id))).execute()
        print("Tranx Deleted Whose Report are Generated at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        print("Tranx Deleted Whose Report are Generated Failed at {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))


def combine_data(insid,channel):
    query = (f"SELECT distinct(newiseretailer.CardAcceptorIdentification) FROM newiseretailer INNER JOIN retailercompansation ON retailercompansation.RetailerId = newiseretailer.CardAcceptorIdentification And retailercompansation.Channel = newiseretailer.ChannelType and retailercompansation.EntityId = newiseretailer.AcquiringInstitutionIdentification where (newiseretailer.ResponseCode = '00') and (newiseretailer.AcquiringInstitutionIdentification = '{insid}' ) and (newiseretailer.ChannelType = '{channel}');")
    
    cursor = myDB.execute_sql(query)
    data=[k for k in cursor]
    result = [k for k in data]
    retailer_list = [item for sublist in result for item in sublist]
    return retailer_list


def Update_pending_day():
    try:
        query= '''update retailercompansation set PendingDays = CutOverDays where PendingDays = 0 ;'''
        cursor = myDB.execute_sql(query)
        print("In RetailerCompsation Table Pending Day Update Successfylly At {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
       print("In RetailerCompsation Table Pending Day Update Failed {} {}".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S'),e))

    