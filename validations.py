import queries
from model import *


def validationInstitutionExist():
    validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Institution exist")
    enabled = 0
    for i in validations:
        if(i.Val_status == 1):
            enabled = 1
    if(enabled):
        print("value of enable {}".format(enabled))
        queries.validation_institution_exist()


def validationRetailerExistAcquirer():
    try:
        validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Retailer exist")
        enabled = 0
        for i in validations:
            if(i.Val_status == 1):
                enabled = 1
        if(enabled):
            queries.acquirer_retailer_exist_validation()
        print("Acquirer Retailer Validation Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Retailer Validation Failed at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {}".format(e))


def validationRetailerExistAcquirerFullDay():
    """ CC0024 Specific """

    try:
        validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Retailer exist")
        enabled = 0
        for i in validations:
            if(i.Val_status == 1):
                enabled = 1
        if(enabled):
            queries.acquirer_retailer_exist_validation_fullday()
            #retailer_val = queries.acquirer_retailer_exist_validation()
            #if len(retailer_val) == 0:
            #    print("All retailers valid")
            #else:
            #    print("Retailers not valid: ",retailer_val)
        print("Acquirer Retailer Full Day Validation Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Retailer Full Day Validation Failed at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {}".format(e))


def validationRetailerExistIssuer():
    
    try:
        validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Retailer exist")
        enabled = 0
        for i in validations:
            if(i.Val_status == 1):
                enabled = 1
        if(enabled):
            queries.issuer_retailer_exist_validation()
        print("Issuer Retailer Validation Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Issuer Retailer Validation Failed at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {}".format(e))


def validationTerminalExist():
    validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Terminal exist")
    enabled = 0
    for i in validations:
        if(i.Val_status == 1):
            enabled = 1
    if(enabled):
        queries.validation_terminal_exist()


def validationRetailerStatus():
    validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Retailer status")
    enabled = 0
    for i in validations:
        if(i.Val_status == 1):
            enabled = 1
    if(enabled):
        queries.validation_retailer_status()


def cleanAcquirerNonValidated():
    try:
        if(AcquirerNotValid.select().count() > 0):
            queries.clean_acquirer_validated()
        print("Cleared Acquirer Non Validated Transactions at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Non Validated Transactions Not Cleared at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {} ".format(e))


def cleanAcquirerNonValidatedFullDay():
    """ CC0024 Specific """
    try:
        if(FullDayAcquirerNotValid.select().count() > 0):
            queries.clean_acquirer_validated_fullday()
        print("Cleared Acquirer Non Validated Full Day Transactions at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Non Validated Full Day Transactions Not Cleared at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {} ".format(e))


def cleanIssuerNonValidated():
    try:
        if(IssuerNotValid.select().count() > 0):
            queries.clean_issuer_validated()
        print("Cleared Issuer Non Validated Transactions at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Issuer Non Validated Transactions Not Cleared at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {} ".format(e))


def validationRetailerExistAcquirerFullDay():
    """ CC0024 Specific """
    try:
        validations = EnableValidations.select().where(EnableValidations.Val_desc == "Validation Retailer exist")
        enabled = 0
        for i in validations:
            if(i.Val_status == 1):
                enabled = 1
        if(enabled):
            queries.acquirer_retailer_exist_validation_fullday()
        print("Acquirer Retailer Full Day Validation Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Retailer Full Day Validation Failed at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {}".format(e))           


def cleanAcquirerNonValidatedFullDay():
    """ CC0024 Specific """
    try:
        if(FullDayAcquirerNotValid.select().count() > 0):
            queries.clean_acquirer_validated_fullday()
        print("Cleared Acquirer Non Validated Full Day Transactions at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e:
        print("Acquirer Non Validated Full Day Transactions Not Cleared at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {} ".format(e))


def cleanAcquireOriginalReversalSuccess():
    """
    * Mantis 728 Specific :-
    Remove Txns at Acq side whose purchase is declined  but reversal is success
    """ 
    try:
        queries.insert_reversalsuccess()
        if (AcquirerReversalSuccessPurchaceDecline.select().count() >0):
            queries.insert_to_transactionhistory()
            queries.cleanReversalSuccess()
        print("Purchase Decline Reversal Success Validation Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S'))) 
    except Exception as e:
        print("Purchase Decline Reversal Success Validation not Done at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        print("Error = {} ".format(e))

           
