from promotion import get_discount
from commission import get_commission



def liquidate_transaction(single_txn, ret_account_dict):
    iseretailer = {}
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

    iseretailer["TimeStamp"] = single_txn.TimeStamp
    iseretailer["MessageType"] = single_txn.MessageType
    iseretailer["PrimaryBitMap"] = single_txn.PrimaryBitMap
    iseretailer["SecondaryBitMap"] = single_txn.SecondaryBitMap
    iseretailer["PrimaryAccountNumberPAN"] = single_txn.PrimaryAccountNumberPAN
    iseretailer["ProcessingCode"] = single_txn.ProcessingCode
    iseretailer["TransactionAmount"]   = float(single_txn.TransactionAmount)
    iseretailer["TransactionAmountCardholderBilling"] = single_txn.TransactionAmountCardholderBilling
    iseretailer["TransmissionDateandTime"] = single_txn.TransmissionDateandTime
    iseretailer["ConversionRateCardholderBilling"] = single_txn.ConversionRateCardholderBilling
    iseretailer["SystemsTraceAuditNumber"] = single_txn.SystemsTraceAuditNumber
    iseretailer["LocalTransactionTime"] = single_txn.LocalTransactionTime
    iseretailer["LocalTransactionDate"] = single_txn.LocalTransactionDate
    iseretailer["ExpirationDate"] = single_txn.ExpirationDate
    iseretailer["SettlementDate"] = single_txn.SettlementDate
    iseretailer["CaptureDate"] = single_txn.CaptureDate
    iseretailer["MerchantTypeCode"] = single_txn.MerchantTypeCode
    iseretailer["AcquirerInstitutionCountryCode"] = single_txn.AcquirerInstitutionCountryCode
    iseretailer["IssuerInstututionCountryCode"] = single_txn.IssuerInstututionCountryCode
    iseretailer["ForwardingInstitutionCountryCode"] = single_txn.ForwardingInstitutionCountryCode
    iseretailer["PointofServiceEntryModeCode"] = single_txn.PointofServiceEntryModeCode
    iseretailer["CardSequenceNumber"] = single_txn.CardSequenceNumber
    iseretailer["NetworkInternationalIdentifierCode"] = single_txn.NetworkInternationalIdentifierCode
    iseretailer["PointofServiceConditionCode"] = single_txn.PointofServiceConditionCode
    iseretailer["AcquiringInstitutionIdentification"] = entity_id
    iseretailer["ForwardingInstitutionIdentification"] = single_txn.ForwardingInstitutionIdentification[-4:]
    iseretailer["Track2Data"] = single_txn.Track2Data
    iseretailer["RetrievalReferenceNumber"] = single_txn.RetrievalReferenceNumber
    iseretailer["AuthorizationIdentificationResponse"] = single_txn.AuthorizationIdentificationResponse
    iseretailer["ResponseCode"] = single_txn.ResponseCode
    iseretailer["CardAcceptorTerminalIdentification"] = single_txn.CardAcceptorTerminalIdentification
    iseretailer["CardAcceptorIdentification"] = single_txn.CardAcceptorIdentification
    iseretailer["CardAcceptorNameLocation"] = single_txn.CardAcceptorNameLocation
    iseretailer["Track1Data"] = single_txn.Track1Data
    iseretailer["RetailerData"] = single_txn.RetailerData
    iseretailer["TransactionCurrencyCode"] = single_txn.TransactionCurrencyCode
    iseretailer["CurrencyCodeCardholderBilling"] = single_txn.CurrencyCodeCardholderBilling
    iseretailer["PersonalIdentificationNumberPINData"] = single_txn.PersonalIdentificationNumberPINData
    iseretailer["AdditionalAmount"] = single_txn.AdditionalAmount
    iseretailer["IntegratedCircuitCardICC"] = single_txn.IntegratedCircuitCardICC
    iseretailer["CardholdersIdentificationNumberandName"] = single_txn.CardholdersIdentificationNumberandName
    iseretailer["AdditionalAmounts"] = single_txn.AdditionalAmounts
    iseretailer["TerminalData"] = single_txn.TerminalData
    iseretailer["CardData"] = single_txn.CardData
    iseretailer["TerminalPostalCode"] = single_txn.TerminalPostalCode
    iseretailer["Token1"] = single_txn.Token1
    iseretailer["Token2"] = single_txn.Token2
    iseretailer["Token3"] = single_txn.Token3
    iseretailer["PrimaryMessageAuthenticationCodeMAC"] = single_txn.PrimaryMessageAuthenticationCodeMAC
    iseretailer["ChannelType"] = single_txn.ChannelType
    iseretailer["CardType"] = single_txn.CardType
    iseretailer["NoOfInstallment"] = single_txn.NoOfInstallment
    iseretailer["InstallmentType"] = single_txn.InstallmentType
    iseretailer["IssuerRRN"] = single_txn.IssuerRRN

    ################ * Commissions * ################

    iseretailer["RetCardTypeCommision"]        =   round(retailer_commission[0])
    iseretailer["RetBinCommision"]             =   round(retailer_commission[1])
    iseretailer["RetMccCommision"]             =   round(retailer_commission[2])
    iseretailer["RetTxnIdentifierCommision"]   =   round(retailer_commission[3])
    iseretailer["RetRubroCommision"]           =   round(retailer_commission[4])
    iseretailer["RetRegionCommision"]          =   round(retailer_commission[5])

    ################ * Discounts * ################

    iseretailer["RetCardTypePromotion"]        =   round(retailer_promotions[0])
    iseretailer["RetBinPromotion"]             =   round(retailer_promotions[1])
    iseretailer["RetMccPromotion"]             =   round(retailer_promotions[2])
    iseretailer["RetTxnIdentifierPromotion"]   =   round(retailer_promotions[3])
    iseretailer["RetRubroPromotion"]           =   round(retailer_promotions[4])
    iseretailer["RetRegionPromotion"]          =   round(retailer_promotions[5])

    ################ * Total * ################

    iseretailer["Retailer"]            =   sum(retailer_commission) - sum(retailer_promotions)
    iseretailer["Acquirer"]            =   round(0)
    iseretailer["Issuer"]              =   round(0)
    iseretailer["TotalCommissions"]    =   iseretailer["Retailer"] + iseretailer["Acquirer"] + iseretailer["Issuer"]
    iseretailer["TotalPromotions"]     =   sum(retailer_promotions)
    del retailer_promotions, retailer_commission

    ################ * Taxes * ################

    iseretailer["Retefuente"]      =	iseretailer["TotalCommissions"] * RETEFUENTE	
    iseretailer["Reteica"]         =	iseretailer["TransactionAmount"] * RETEICA	
    iseretailer["Cree"]            =	iseretailer["TransactionAmount"] * CREE    	
    iseretailer["Reteiva"]         =	iseretailer["TransactionAmount"] * RETEIVA	
    iseretailer["TotalTaxes"] = iseretailer["Retefuente"] + iseretailer["Reteica"] + iseretailer["Cree"] + iseretailer["Reteiva"]

    ################ * Final Amount * ################

    iseretailer["TotalDiscounts"]      =	iseretailer["TotalCommissions"] + iseretailer["TotalTaxes"]
    iseretailer["FinalAmount"]         =	iseretailer["TransactionAmount"] - iseretailer["TotalDiscounts"]

    # * Optimize RAM
    del RETEFUENTE, RETEICA, CREE, RETEIVA, ret_account_dict
    # * Return Calculated Transactions
    return iseretailer



if __name__ == '__main__':
    pass
