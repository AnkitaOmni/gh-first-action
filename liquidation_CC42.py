from promotion import get_discount
from commission import get_commission



def liquidate_transaction(single_txn, ret_account_dict):
    newiseretailer = {}
    bin_code = single_txn.PrimaryAccountNumberPAN.strip()
    entity_id = single_txn.AcquiringInstitutionIdentification[-4:]
    
    try:
        RETEFUENTE = float(ret_account_dict[entity_id, "DEFAULT"]['Retefuente'])/100.0  # * percentage
        RETEICA, CREE, RETEIVA = 0.0, 0.0, 0.0
    except KeyError: RETEFUENTE, RETEICA, CREE, RETEIVA = 0.0, 0.0, 0.0, 0.0

    if single_txn.NetworkInternationalIdentifierCode.strip() == "AT":
        retailer_commission = 0,0,0,0,0,0
        retailer_promotions = 0,0,0,0,0,0
        # # print(f"Adjustment Trnx NCA = {single_txn.NetworkInternationalIdentifierCode.strip()}")
    else:
        caseList = (entity_id + '-' + single_txn.CardAcceptorIdentification + '-' + single_txn.ChannelType,
                entity_id + '-DEFAULT-' + single_txn.ChannelType,
                entity_id + '-' + single_txn.CardAcceptorIdentification + '-DEFAULT',
                entity_id + '-DEFAULT-DEFAULT',
                'DEFAULT-DEFAULT-DEFAULT')
        retailer_commission = get_commission(caseList,entity_id = entity_id, retailer_id = single_txn.CardAcceptorIdentification, message_type = single_txn.MessageType, processing_code = single_txn.ProcessingCode, response_code =  single_txn.ResponseCode, amount = single_txn.TransactionAmount, index_transaction = single_txn.id , mcc = single_txn.MerchantTypeCode, channel = single_txn.ChannelType, bin = bin_code, transaction_identifier = single_txn.PrimaryMessageAuthenticationCodeMAC, card_type = single_txn.CardType)
        retailer_promotions = get_discount(caseList,entity_id = entity_id, retailer_id = single_txn.CardAcceptorIdentification, message_type = single_txn.MessageType, processing_code = single_txn.ProcessingCode, response_code =  single_txn.ResponseCode, amount = single_txn.TransactionAmount, index_transaction = single_txn.id , mcc = single_txn.MerchantTypeCode, channel = single_txn.ChannelType, bin = bin_code, transaction_identifier = single_txn.PrimaryMessageAuthenticationCodeMAC, card_type = single_txn.CardType)
        # * Skip commissions when sum of discount are greater than sum of commissions
        # print(f"\n\n{retailer_commission} = {retailer_promotions}")
        if sum(retailer_promotions) > sum(retailer_commission):
            del retailer_commission, retailer_promotions
            retailer_commission = 0,0,0,0,0,0
            retailer_promotions = 0,0,0,0,0,0
        # print(f"retailer_commission = {retailer_commission} | {sum(retailer_commission)}")

    newiseretailer["TimeStamp"] = single_txn.TimeStamp
    newiseretailer["MessageType"] = single_txn.MessageType
    newiseretailer["PrimaryBitMap"] = single_txn.PrimaryBitMap
    newiseretailer["SecondaryBitMap"] = single_txn.SecondaryBitMap
    newiseretailer["PrimaryAccountNumberPAN"] = single_txn.PrimaryAccountNumberPAN
    newiseretailer["ProcessingCode"] = single_txn.ProcessingCode
    newiseretailer["TransactionAmount"]   = float(single_txn.TransactionAmount)
    newiseretailer["TransactionAmountCardholderBilling"] = single_txn.TransactionAmountCardholderBilling
    newiseretailer["TransmissionDateandTime"] = single_txn.TransmissionDateandTime
    newiseretailer["ConversionRateCardholderBilling"] = single_txn.ConversionRateCardholderBilling
    newiseretailer["SystemsTraceAuditNumber"] = single_txn.SystemsTraceAuditNumber
    newiseretailer["LocalTransactionTime"] = single_txn.LocalTransactionTime
    newiseretailer["LocalTransactionDate"] = single_txn.LocalTransactionDate
    newiseretailer["ExpirationDate"] = single_txn.ExpirationDate
    newiseretailer["SettlementDate"] = single_txn.SettlementDate
    newiseretailer["CaptureDate"] = single_txn.CaptureDate
    newiseretailer["MerchantTypeCode"] = single_txn.MerchantTypeCode
    newiseretailer["AcquirerInstitutionCountryCode"] = single_txn.AcquirerInstitutionCountryCode
    newiseretailer["IssuerInstututionCountryCode"] = single_txn.IssuerInstututionCountryCode
    newiseretailer["ForwardingInstitutionCountryCode"] = single_txn.ForwardingInstitutionCountryCode
    newiseretailer["PointofServiceEntryModeCode"] = single_txn.PointofServiceEntryModeCode
    newiseretailer["CardSequenceNumber"] = single_txn.CardSequenceNumber
    newiseretailer["NetworkInternationalIdentifierCode"] = single_txn.NetworkInternationalIdentifierCode
    newiseretailer["PointofServiceConditionCode"] = single_txn.PointofServiceConditionCode
    newiseretailer["AcquiringInstitutionIdentification"] = entity_id
    newiseretailer["ForwardingInstitutionIdentification"] = single_txn.ForwardingInstitutionIdentification[-4:]
    newiseretailer["Track2Data"] = single_txn.Track2Data
    newiseretailer["RetrievalReferenceNumber"] = single_txn.RetrievalReferenceNumber
    newiseretailer["AuthorizationIdentificationResponse"] = single_txn.AuthorizationIdentificationResponse
    newiseretailer["ResponseCode"] = single_txn.ResponseCode
    newiseretailer["CardAcceptorTerminalIdentification"] = single_txn.CardAcceptorTerminalIdentification
    newiseretailer["CardAcceptorIdentification"] = single_txn.CardAcceptorIdentification
    newiseretailer["CardAcceptorNameLocation"] = single_txn.CardAcceptorNameLocation
    newiseretailer["Track1Data"] = single_txn.Track1Data
    newiseretailer["RetailerData"] = single_txn.RetailerData
    newiseretailer["TransactionCurrencyCode"] = single_txn.TransactionCurrencyCode
    newiseretailer["CurrencyCodeCardholderBilling"] = single_txn.CurrencyCodeCardholderBilling
    newiseretailer["PersonalIdentificationNumberPINData"] = single_txn.PersonalIdentificationNumberPINData
    newiseretailer["AdditionalAmount"] = single_txn.AdditionalAmount
    newiseretailer["IntegratedCircuitCardICC"] = single_txn.IntegratedCircuitCardICC
    newiseretailer["CardholdersIdentificationNumberandName"] = single_txn.CardholdersIdentificationNumberandName
    newiseretailer["AdditionalAmounts"] = single_txn.AdditionalAmounts
    newiseretailer["TerminalData"] = single_txn.TerminalData
    newiseretailer["CardData"] = single_txn.CardData
    newiseretailer["TerminalPostalCode"] = single_txn.TerminalPostalCode
    newiseretailer["Token1"] = single_txn.Token1
    newiseretailer["Token2"] = single_txn.Token2
    newiseretailer["Token3"] = single_txn.Token3
    newiseretailer["PrimaryMessageAuthenticationCodeMAC"] = single_txn.PrimaryMessageAuthenticationCodeMAC
    newiseretailer["ChannelType"] = single_txn.ChannelType
    newiseretailer["CardType"] = single_txn.CardType
    newiseretailer["NoOfInstallment"] = single_txn.NoOfInstallment
    newiseretailer["InstallmentType"] = single_txn.InstallmentType
    newiseretailer["IssuerRRN"] = single_txn.IssuerRRN
    newiseretailer["TxnLoggingTime"] = single_txn.TxnLoggingTime

    ################ * Commissions * ################

    newiseretailer["RetCardTypeCommision"]        =   round(retailer_commission[0])
    newiseretailer["RetBinCommision"]             =   round(retailer_commission[1])
    newiseretailer["RetMccCommision"]             =   round(retailer_commission[2])
    newiseretailer["RetTxnIdentifierCommision"]   =   round(retailer_commission[3])
    newiseretailer["RetRubroCommision"]           =   round(retailer_commission[4])
    newiseretailer["RetRegionCommision"]          =   round(retailer_commission[5])

    ################ * Discounts * ################

    newiseretailer["RetCardTypePromotion"]        =   round(retailer_promotions[0])
    newiseretailer["RetBinPromotion"]             =   round(retailer_promotions[1])
    newiseretailer["RetMccPromotion"]             =   round(retailer_promotions[2])
    newiseretailer["RetTxnIdentifierPromotion"]   =   round(retailer_promotions[3])
    newiseretailer["RetRubroPromotion"]           =   round(retailer_promotions[4])
    newiseretailer["RetRegionPromotion"]          =   round(retailer_promotions[5])

    ################ * Total * ################

    newiseretailer["Retailer"]            =   sum(retailer_commission) - sum(retailer_promotions)
    newiseretailer["Acquirer"]            =   round(0)
    newiseretailer["Issuer"]              =   round(0)
    newiseretailer["TotalCommissions"]    =   newiseretailer["Retailer"] + newiseretailer["Acquirer"] + newiseretailer["Issuer"]
    newiseretailer["TotalPromotions"]     =   sum(retailer_promotions)
    del retailer_promotions, retailer_commission

    ################ * Taxes * ################

    newiseretailer["Retefuente"]      =	newiseretailer["TotalCommissions"] * RETEFUENTE	
    newiseretailer["Reteica"]         =	newiseretailer["TransactionAmount"] * RETEICA	
    newiseretailer["Cree"]            =	newiseretailer["TransactionAmount"] * CREE    	
    newiseretailer["Reteiva"]         =	newiseretailer["TransactionAmount"] * RETEIVA	
    newiseretailer["TotalTaxes"] = newiseretailer["Retefuente"] + newiseretailer["Reteica"] + newiseretailer["Cree"] + newiseretailer["Reteiva"]

    ################ * Final Amount * ################

    newiseretailer["TotalDiscounts"]      =	newiseretailer["TotalCommissions"] + newiseretailer["TotalTaxes"]
    newiseretailer["FinalAmount"]         =	newiseretailer["TransactionAmount"] - newiseretailer["TotalDiscounts"]

    # * Optimize RAM
    del RETEFUENTE, RETEICA, CREE, RETEIVA, ret_account_dict
    # * Return Calculated Transactions
    return newiseretailer



if __name__ == '__main__':
    pass
