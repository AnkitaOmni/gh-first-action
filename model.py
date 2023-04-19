import peewee as pw
from datetime import datetime
from database import DatabaseConnections
from peewee import SQL
from playhouse.mysql_ext import JSONField

db = DatabaseConnections()
myDB = db.peewee_connection()
today = datetime.now().strftime(r"%d-%m-%Y")


class MySQLModel(pw.Model):
    """
    Summary:
        A base model that will use our MySQL database

    Args:
        pw (_type_): Peewee Model
    """
    class Meta:
        database = myDB


class Users(MySQLModel):

    username = pw.CharField()
    created_date = pw.DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    status = pw.BooleanField(default=True)
    email = pw.CharField()
    role = pw.CharField()
    institution = pw.CharField()
    permissions = pw.TextField()
    pw_hash = pw.CharField()


class CommissionProfiles(MySQLModel):

    profile_name = pw.CharField()
    message_type = pw.CharField(max_length=4)
    transaction_type = pw.CharField(max_length=2)
    response_code = pw.CharField(max_length=2)
    is_fixed_value = pw.BooleanField(default=True)
    is_percentage = pw.BooleanField(default=False)
    is_slabs = pw.BooleanField(default=False)
    value = pw.DecimalField(decimal_places=2)


class CommissionSlabs(MySQLModel):

    profile_id = pw.CharField()
    slabs_type = pw.CharField()
    commission_type = pw.CharField()
    min_limit = pw.IntegerField()
    max_limit = pw.IntegerField()
    value = pw.DecimalField(decimal_places=2)


class Institution(MySQLModel):

    INSTITUTION_ID = pw.CharField()
    INSTITUTION_NAME = pw.CharField()
    INSTITUTION_TYPE = pw.CharField()
    TRANSACTION_PROFILE_TYPE = pw.CharField()
    ACCOUNT_NUMBER = pw.CharField()
    ACCOUNT_TYPE = pw.CharField()
    ACCOUNT_BANK = pw.CharField()


class ConfigurationCatalogs(MySQLModel):

    catalog_name = pw.CharField()
    code = pw.CharField()
    description = pw.CharField()
    related = pw.CharField()


class CountryCodes(MySQLModel):

    two_letters = pw.CharField(max_length=2)
    three_letters = pw.CharField(max_length=3)
    numeric_code = pw.CharField(max_length=3)
    spanish_desc = pw.CharField(max_length=40)
    english_desc = pw.CharField(max_length=40)

    class Meta:
        primary_key = pw.CompositeKey(
            'two_letters', 'three_letters', 'numeric_code')


class StateAndCity(MySQLModel):

    state_code = pw.CharField(max_length=2)
    state_description = pw.CharField(max_length=40)
    city_code = pw.CharField(max_length=3)
    city_description = pw.CharField(max_length=40)

    class Meta:
        primary_key = pw.CompositeKey('state_code', 'city_code')


class RetailerAcquirerRegion(MySQLModel):

    retailer_acquirer_country_code_ = pw.CharField(max_length=2)
    retailer_acquirer_state_code_ = pw.CharField(max_length=2)
    retailer_acquirer_city_code_ = pw.CharField(max_length=3)

    class Meta:
        primary_key = pw.CompositeKey('retailer_acquirer_country_code_',
                                      'retailer_acquirer_state_code_', 'retailer_acquirer_city_code_')


class RetailerId(MySQLModel):
    """
    Summary:
        Retailer Details

    Args:
        MySQLModel (_type_): Default MySQL Model
    """
    RetailerId = pw.CharField(max_length=19)
    EntityId = pw.CharField(max_length=8)
    GroupCode = pw.IntegerField()
    MallCode = pw.IntegerField()
    AcquirerRegionCode = pw.CharField(max_length=20)
    CompanyName = pw.CharField(max_length=40)
    Name = pw.CharField(max_length=40)
    CountryCode = pw.CharField(max_length=2)
    StateCode = pw.CharField(max_length=2)
    CityCode = pw.IntegerField()
    CountyCode = pw.IntegerField()
    Address = pw.CharField(max_length=40)
    PostalCode = pw.CharField(max_length=10)
    Phone = pw.CharField(max_length=20)
    CellPhone = pw.CharField(max_length=20)
    FaxPhone = pw.CharField(max_length=20)
    AfterHoursPhone = pw.CharField(max_length=20)
    AfterHoursCellPhone = pw.CharField(max_length=20)
    AfterHoursFaxPhone = pw.CharField(max_length=20)
    ReferralPhone = pw.CharField(max_length=20)
    EmailAddress = pw.CharField(max_length=40)
    AlternateEmailAddress = pw.CharField(max_length=40)
    IdentificationTypeCode = pw.IntegerField()
    IdentificationNumber = pw.CharField(max_length=15)
    MCC = pw.IntegerField()
    MCCForNoPresentTransaction = pw.IntegerField()
    IdForAmex = pw.CharField(max_length=19)
    MCCForAmex = pw.IntegerField()
    MCCForAmexForNoPresentTransaction = pw.IntegerField()
    WorkingHoursCode = pw.IntegerField()
    DepositOnLineCode = pw.IntegerField()
    PaymentVendorsCode = pw.IntegerField()
    AffiliationDate = pw.IntegerField()
    LastUpdateDateNotMonetary = pw.IntegerField()
    LastUpdateDateMonetary = pw.IntegerField()
    StatusCode = pw.IntegerField()
    AssignedAgreeementCode = pw.CharField(max_length=10)
    AccountNumber = pw.CharField(max_length=20)
    MovmentType = pw.CharField(max_length=2)
    BankCode = pw.CharField(max_length=3)
    RubroCode = pw.CharField(max_length=16, null=True)

    class Meta:
        primary_key = pw.CompositeKey('RetailerId', 'EntityId')


class TerminalId(MySQLModel):
    """
    Summary:
        Terminal Details

    Args:
        MySQLModel (_type_): Default MySQL Model
    """
    TerminalId = pw.CharField(max_length=19, primary_key=True)
    SerialNumber = pw.CharField(max_length=19)
    EntityId = pw.CharField(max_length=8)
    OwnerEntityId = pw.CharField(max_length=8)
    TerminalUsage = pw.CharField(max_length=1)
    Factory = pw.CharField(max_length=1)
    Telco = pw.CharField(max_length=1)
    TimeOffset = pw.IntegerField()
    RetailerId = pw.CharField(max_length=19)
    CompanyName = pw.CharField(max_length=40)
    Name = pw.CharField(max_length=40)
    CountryCode = pw.CharField(max_length=2)
    StateCode = pw.CharField(max_length=2)
    CityCode = pw.CharField(max_length=3)
    CountyCode = pw.IntegerField()
    Address = pw.CharField(max_length=20)
    PostalCode = pw.CharField(max_length=10)
    Phone = pw.CharField(max_length=20)
    CellPhone = pw.CharField(max_length=20)
    FaxPhone = pw.CharField(max_length=20)
    AfterHoursPhone = pw.CharField(max_length=20)
    AfterHoursCellPhone = pw.CharField(max_length=20)
    AfterHoursFaxPhone = pw.CharField(max_length=20)
    ReferralPhone = pw.CharField(max_length=20)
    EmailAddress = pw.CharField(max_length=40)
    AlternateEmailAddress = pw.CharField(max_length=40)
    IdentificationTypeCode = pw.IntegerField()
    IdentificationNumber = pw.CharField(max_length=15)
    CutoverBalanceStart = pw.IntegerField()
    CutoverBalanceEnd = pw.IntegerField()
    PostingDateCurrent = pw.IntegerField()
    InstalationDate = pw.IntegerField()
    TimeOutCode = pw.IntegerField()
    LastUpdateDateNotMonetary = pw.IntegerField()
    LastUpdateDateMonetary = pw.IntegerField()
    StatusCode = pw.IntegerField()


class RetailerAccount(MySQLModel):

    EntityId = pw.CharField(max_length=8)
    RetailerId = pw.CharField(max_length=19)
    TerminalId = pw.CharField(max_length=19)
    CardProductId = pw.CharField()
    AccountTypeCode = pw.IntegerField()
    AccountNumber = pw.IntegerField()
    RetefuenteCode = pw.IntegerField()
    Retefuente = pw.DecimalField(max_digits=15, decimal_places=0)
    ReteicaCode = pw.IntegerField()
    Reteica = pw.DecimalField(max_digits=15, decimal_places=0)
    CreeCode = pw.IntegerField()
    Cree = pw.DecimalField(max_digits=15, decimal_places=0)
    ImpoconsumoCode = pw.IntegerField()
    Impoconsumo = pw.DecimalField(max_digits=15, decimal_places=0)
    CreeCode = pw.IntegerField()
    Cree = pw.DecimalField(max_digits=15, decimal_places=0)
    ReteivaCode = pw.IntegerField()
    Reteiva = pw.DecimalField(max_digits=15, decimal_places=0)

    class Meta:
        primary_key = pw.CompositeKey('EntityId', 'RetailerId')


class InstitutionId(MySQLModel):

    institution_id_type_code = pw.CharField(max_length=8)
    institution_id_type_desc = pw.CharField()
    institution_id_code = pw.CharField(max_length=8)
    institution_id_desc = pw.CharField()
    fiid = pw.CharField(max_length=15)
    assigned_agreeement_code = pw.CharField(max_length=10)
    name_officer = pw.CharField(max_length=20)
    tax_id = pw.CharField(max_length=15)
    bank_account_number = pw.CharField(max_length=20)
    movment_type = pw.CharField(max_length=2)
    bank_code = pw.CharField(max_length=3)
    channel_name = pw.CharField(max_length=20)
    channel_type = pw.BooleanField(default=True)

    class Meta:
        primary_key = pw.CompositeKey('institution_id_code', 'channel_name')


class CardBrandId(MySQLModel):

    type_code = pw.CharField(max_length=1)
    type_desc = pw.CharField(max_length=40)
    card_brand_code = pw.CharField(max_length=4)
    card_brand_desc = pw.CharField(max_length=40)
    card_sub_brand_code = pw.CharField(max_length=5)
    card_sub_brand_desc = pw.CharField(max_length=40)

    class Meta:
        primary_key = pw.CompositeKey(
            'type_code', 'card_brand_code', 'card_sub_brand_code')


class TransactionId(MySQLModel):

    token_code = pw.CharField(max_length=2)
    token_desc = pw.CharField(max_length=40)
    transaction_code = pw.CharField(max_length=2)
    transaction_desc = pw.CharField(max_length=40)

    class Meta:
        primary_key = pw.CompositeKey('token_code', 'transaction_code')


class EnterpriseInfo(MySQLModel):

    EntityId = pw.CharField(max_length=8)
    Name = pw.CharField()
    Address = pw.CharField()
    Contact = pw.CharField()
    AltContact = pw.CharField()


class EnableValidations(MySQLModel):

    Val_group = pw.CharField()
    Val_desc = pw.CharField()
    Val_status = pw.IntegerField()


################## * Acquirer Node * ##################

class AcquirerOriginal(MySQLModel):
    """
    Summary:
        Acquirer CSV Data/Trnx Are Dumped Here
        Cut Over Time = 20:59:59
    """
    TimeStamp = pw.DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    MessageType = pw.FixedCharField(max_length=4)
    PrimaryBitMap = pw.FixedCharField(max_length=16)
    SecondaryBitMap = pw.FixedCharField(max_length=16)
    PrimaryAccountNumberPAN = pw.FixedCharField(max_length=19)
    ProcessingCode = pw.FixedCharField(max_length=6)
    TransactionAmount = pw.DecimalField(max_digits=14, decimal_places=0)
    TransactionAmountCardholderBilling = pw.FixedCharField(max_length=12)
    TransmissionDateandTime = pw.FixedCharField(max_length=10)
    ConversionRateCardholderBilling = pw.FixedCharField(max_length=8)
    SystemsTraceAuditNumber = pw.FixedCharField(max_length=6)
    LocalTransactionTime = pw.TimeField()
    LocalTransactionDate = pw.DateField()
    ExpirationDate = pw.FixedCharField(max_length=4)
    SettlementDate = pw.FixedCharField(max_length=4)
    CaptureDate = pw.FixedCharField(max_length=4)
    MerchantTypeCode = pw.FixedCharField(max_length=4)
    AcquirerInstitutionCountryCode = pw.FixedCharField(max_length=3)
    IssuerInstututionCountryCode = pw.FixedCharField(max_length=3)
    ForwardingInstitutionCountryCode = pw.FixedCharField(max_length=3)
    PointofServiceEntryModeCode = pw.FixedCharField(max_length=3)
    CardSequenceNumber = pw.FixedCharField(max_length=3)
    NetworkInternationalIdentifierCode = pw.FixedCharField(max_length=3)
    PointofServiceConditionCode = pw.FixedCharField(max_length=2)
    AcquiringInstitutionIdentification = pw.FixedCharField(max_length=16)
    ForwardingInstitutionIdentification = pw.FixedCharField(max_length=16)
    Track2Data = pw.FixedCharField(max_length=40)
    RetrievalReferenceNumber = pw.FixedCharField(max_length=12)
    AuthorizationIdentificationResponse = pw.FixedCharField(max_length=6)
    ResponseCode = pw.FixedCharField(max_length=2)
    CardAcceptorTerminalIdentification = pw.FixedCharField(max_length=17)
    CardAcceptorIdentification = pw.FixedCharField(max_length=20)
    CardAcceptorNameLocation = pw.FixedCharField(max_length=40)
    Track1Data = pw.FixedCharField(max_length=79)
    RetailerData = pw.FixedCharField(max_length=30)
    TransactionCurrencyCode = pw.FixedCharField(max_length=3)
    CurrencyCodeCardholderBilling = pw.FixedCharField(max_length=3)
    PersonalIdentificationNumberPINData = pw.FixedCharField(max_length=16)
    AdditionalAmount = pw.FixedCharField(max_length=15)
    IntegratedCircuitCardICC = pw.TextField()
    CardholdersIdentificationNumberandName = pw.FixedCharField(max_length=100)
    AdditionalAmounts = pw.TextField()
    TerminalData = pw.FixedCharField(max_length=19)
    CardData = pw.FixedCharField(max_length=22)
    TerminalPostalCode = pw.FixedCharField(max_length=13)
    Token1 = pw.TextField()
    Token2 = pw.TextField()
    Token3 = pw.TextField()
    PrimaryMessageAuthenticationCodeMAC = pw.FixedCharField(max_length=16)
    ChannelType = pw.FixedCharField(max_length=15)
    CardType = pw.FixedCharField(max_length=2)
    NoOfInstallment = pw.FixedCharField(max_length=15, null=True)
    InstallmentType = pw.FixedCharField(max_length=15, null=True)
    IssuerRRN = pw.FixedCharField(max_length=15, null=True)
    TxnLoggingTime = pw.DateTimeField(default=datetime.now())


class AcquirerDuplicates(AcquirerOriginal):
    """
    Summary:
        Acquirer Duplicate Trnxs Are Kept Here
    """
    pass


class AcquirerNotValid(AcquirerOriginal):
    """
    Summary:
        if (ForwardingInstitutionCountryCode & CardAcceptorIdentification) == Blank / Null / Empty:
            Acquirer Not Valid Trnxs Are Dumped Here Here
    """
    Validation = pw.TextField()
    ExtarctFileId = pw.CharField()


class AcquirerExtract(AcquirerOriginal):
    """
    Summary:
        All Filtered Trnxs Are Collected Here For Compensation/Liquidation
    """
    pass


class AcquirerReversalSuccessPurchaceDecline(AcquirerOriginal):
    """
    Summary/Usage:
        - Mantis 728 Specific
        - Reversal Success Trnx Whose Purchase Is Declined At Acqurier Side

    Args:
        AcquirerExtract (Class): Inheritade AcquirerExtract Table Class
    """
    pass


class ISERetailer(AcquirerOriginal):
    """
    Summary:
        All Compensated / Liquidated Trnx Are Put Here For
            1. Daily Merchant Report Generation
            2. History update / insert
    """
    RetCardTypeCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetCardTypePromotion = pw.DecimalField(max_digits=14, decimal_places=0)

    RetBinCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetBinPromotion = pw.DecimalField(max_digits=14, decimal_places=0)

    RetMccCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetMccPromotion = pw.DecimalField(max_digits=14, decimal_places=0)

    RetTxnIdentifierCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetTxnIdentifierPromotion = pw.DecimalField(max_digits=14, decimal_places=0)

    RetRubroCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetRubroPromotion = pw.DecimalField(max_digits=14, decimal_places=0)
    
    RetRegionCommision = pw.DecimalField(max_digits=14, decimal_places=0)
    RetRegionPromotion = pw.DecimalField(max_digits=14, decimal_places=0)

    Retailer = pw.DecimalField(max_digits=14, decimal_places=0)
    Acquirer = pw.DecimalField(max_digits=14, decimal_places=0)
    Issuer = pw.DecimalField(max_digits=14, decimal_places=0)

    TotalCommissions = pw.DecimalField(max_digits=14, decimal_places=0)
    TotalPromotions = pw.DecimalField(max_digits=14, decimal_places=0)

    Retefuente = pw.DecimalField(max_digits=14, decimal_places=0)
    Reteica = pw.DecimalField(max_digits=14, decimal_places=0)
    Cree = pw.DecimalField(max_digits=14, decimal_places=0)
    Reteiva = pw.DecimalField(max_digits=14, decimal_places=0)

    TotalTaxes = pw.DecimalField(max_digits=14, decimal_places=0)
    TotalDiscounts = pw.DecimalField(max_digits=14, decimal_places=0)

    FinalAmount = pw.DecimalField(max_digits=14, decimal_places=0)


class TransactionHistory(ISERetailer):
    """
    Summary:
        All Compensated / Liquidated Trnx Are Put Here For
            1. Monthly Report Generation
            2. Storage Upto 5 Years Max
    """
    class Meta:

        indexes = (
            (('RetrievalReferenceNumber', 'TransmissionDateandTime', 'Track2Data', 'MessageType',
             'ProcessingCode', 'ResponseCode', 'CardAcceptorIdentification'), True),
        )


class TransactionHistory_Copy(TransactionHistory):
    pass


class Update_TH_ISERetailer(ISERetailer):
    """
    Summary:
        All Trnxs Which Will Be Updated In Trnx History Table Are Sotred Here
    """
    pass


class ISERetailerCopy(ISERetailer):
    """
    Summary:
        All Trnxs Which Will Be Newly Inserted In Trnx History Table Are Sotred Here
    """
    pass


########## * CCX30 / CCX24 * ##########

class ValeVista(MySQLModel):

    Ruth = pw.CharField(max_length=10)
    RetName = pw.CharField(max_length=20)
    EmailId = pw.CharField(max_length=30)
    IDP = pw.CharField(primary_key=True, max_length=20)
    FixedValue1 = pw.FixedCharField(default="012", max_length=3)
    FixedValue2 = pw.CharField(max_length=2, default="23")
    FixedValue3 = pw.FixedCharField(default="00000000000000000", max_length=17)
    PaymentAmt = pw.DecimalField(max_digits=14, decimal_places=0)


class Estado_Report(MySQLModel):

    RetId = pw.CharField()
    InsId = pw.CharField()
    StartColumn = pw.CharField(default="Estado")
    Ruth = pw.CharField()
    Dv = pw.CharField()
    RetName = pw.CharField()
    IDP = pw.CharField(max_length=20)
    EmailId = pw.CharField()
    BankCode = pw.CharField()
    AcType = pw.CharField()
    AcNum = pw.CharField()
    FinalAmt = pw.CharField()
    DocType = pw.CharField(default="Estado")
    Observation = pw.CharField(default="Estado")
    Warning = pw.CharField(default="Estado")
    EndColumn = pw.CharField(default="Estado")
    DepositStatus = pw.CharField(max_length=20, default="Pendiente")
    RetailerStatus = pw.CharField(max_length=20)
    PaymentDate = pw.CharField(default='')
    DepositDate = pw.CharField(default=today)
    BrodcastDate = pw.CharField(default=today)
    Region = pw.CharField(max_length=20)


class EstadoIdpUpdate(Estado_Report):
    """
    Summary:
        Updated Records In Estado Table Are Stored Here
    """
    pass


class Chile_Report(MySQLModel):

    RetId = pw.CharField()
    InsId = pw.CharField()
    StartColumn = pw.CharField(max_length=1, default="1")
    Ruth = pw.CharField()
    Dv = pw.CharField()
    RetName = pw.CharField()
    DocType = pw.CharField(max_length=20, default="991")
    DocNum = pw.CharField(max_length=20)
    FinalAmt = pw.CharField()
    Observation = pw.CharField()
    AcType = pw.CharField()
    BankCode = pw.CharField()
    AcNum = pw.CharField()
    Warning = pw.CharField()
    EmailId = pw.CharField()
    EndColumn = pw.CharField(max_length=1, default="1")
    DepositStatus = pw.CharField(max_length=20, default="Pendiente")
    RetailerStatus = pw.CharField(max_length=2)
    PaymentDate = pw.CharField(default='')
    DepositDate = pw.CharField(default=today)
    BrodcastDate = pw.CharField(default=today)
    Region = pw.CharField(max_length=20)


class ChileIdpUpdate(Chile_Report):
    """
    Summary:
        Updated Records In Chile Table Are Stored Here
    """
    pass


class FullDayTransactionRetailerHistory(MySQLModel):

    IDP = pw.CharField(max_length=20)  # DocNum both are same
    RetId = pw.CharField()
    InsId = pw.CharField()
    StartColumn = pw.CharField()
    Ruth = pw.CharField()
    Dv = pw.CharField()
    RetName = pw.CharField()
    DocType = pw.CharField()
    FinalAmt = pw.CharField()
    Observation = pw.CharField(null=True)
    AcType = pw.CharField()
    BankCode = pw.CharField()
    AcNum = pw.CharField()
    Warning = pw.CharField(null=True)
    EmailId = pw.CharField()
    DepositStatus = pw.CharField()
    BrodcastDate = pw.CharField(default=today)
    PaymentDate = pw.CharField(default='')
    DepositDate = pw.CharField()
    RetailerStatus = pw.CharField()
    InsertedDate = pw.CharField(default=today)
    UpdatedDate = pw.CharField(default=today)
    EndColumn = pw.CharField()
    Region = pw.CharField(max_length=20)

    class Meta:
        primary_key = pw.CompositeKey('IDP', 'RetId')


class CurrentDateTransactionHistory(ISERetailer):
    """
    Summary:
        All Current Date Txn of Txn History Copied Here
    """
    IDP = pw.CharField(default="IDPNAN00000000000000", max_length=20)


class FullDayTransactionHistory(CurrentDateTransactionHistory):
    pass


############### * CCX24 Specific * ###############

class FullDayAcquirerDuplicates(AcquirerOriginal):
    """ 
    Summary:
        (CCX24 Specific)
        Full Day Acquirer Duplicate Trnxs Are Kept Here
     """
    pass


class FullDayAcquirerNotValid(AcquirerOriginal):
    """ 
    Summary:
        (CCX24 Specific)
            If (ForwardingInstitutionIdentification & CardAcceptorIdentification) == Blank / Null / Empty:
                Full Day Acquirer Not Valid Trnxs Are Dumped Here
     """
    Validation = pw.TextField()
    ExtarctFileId = pw.CharField()


class FullDayAcquirerOriginal(AcquirerOriginal):
    """ 
    Summary:
        (CCX24 Specific)
            Full Day Acquirer Original Trnxs Are Kept Here
     """
    pass


class FullDayAcquirerExtract(AcquirerOriginal):
    """ 
    Summary:
        (CCX24 Specific)
            Full Day Acquirer Extract Trnxs Are Kept Here
     """
    pass


################## * Adjustment Module * ##################

class FileAdjustments(AcquirerOriginal):
    pass


class AllAdjustments(AcquirerOriginal):
    """
        *  This table is used to :-
                1. Stores All Adjustements
                    - ManualAdjustements
                    - FileAdjustements
                2. Create the AdjustmentReport_YYMMDD.csv in every liquidation run

    """
    pass


class ManualAdjustmentsExtractFile(AcquirerOriginal):
    AdjustmentType = pw.CharField()
    AdjustmentAmountType = pw.CharField()
    NewAmount = pw.FixedCharField(max_length=12)
    Authorized = pw.IntegerField(default=2)
    Comments = pw.CharField()


################## * Issuer Node * ##################

class IssuerOriginal(MySQLModel):
    """
    Summary:
        Issuer CSV Data/Trnx Are Dumped Here
    """
    TimeStamp = pw.DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    MessageType = pw.FixedCharField(max_length=4)
    PrimaryBitMap = pw.FixedCharField(max_length=16)
    SecondaryBitMap = pw.FixedCharField(max_length=16)
    PrimaryAccountNumberPAN = pw.FixedCharField(max_length=19)
    ProcessingCode = pw.FixedCharField(max_length=6)
    TransactionAmount = pw.DecimalField(max_digits=14, decimal_places=0)
    TransactionAmountCardholderBilling = pw.FixedCharField(max_length=12)
    TransmissionDateandTime = pw.FixedCharField(max_length=10)
    ConversionRateCardholderBilling = pw.FixedCharField(max_length=8)
    SystemsTraceAuditNumber = pw.FixedCharField(max_length=6)
    LocalTransactionTime = pw.TimeField()
    LocalTransactionDate = pw.DateField()
    ExpirationDate = pw.FixedCharField(max_length=4)
    SettlementDate = pw.FixedCharField(max_length=4)
    CaptureDate = pw.FixedCharField(max_length=4)
    MerchantTypeCode = pw.FixedCharField(max_length=4)
    AcquirerInstitutionCountryCode = pw.FixedCharField(max_length=3)
    IssuerInstututionCountryCode = pw.FixedCharField(max_length=3)
    ForwardingInstitutionCountryCode = pw.FixedCharField(max_length=3)
    PointofServiceEntryModeCode = pw.FixedCharField(max_length=3)
    CardSequenceNumber = pw.FixedCharField(max_length=3)
    NetworkInternationalIdentifierCode = pw.FixedCharField(max_length=3)
    PointofServiceConditionCode = pw.FixedCharField(max_length=2)
    AcquiringInstitutionIdentification = pw.FixedCharField(max_length=16)
    ForwardingInstitutionIdentification = pw.FixedCharField(max_length=16)
    Track2Data = pw.FixedCharField(max_length=40)
    RetrievalReferenceNumber = pw.FixedCharField(max_length=12)
    AuthorizationIdentificationResponse = pw.FixedCharField(max_length=6)
    ResponseCode = pw.FixedCharField(max_length=2)
    CardAcceptorTerminalIdentification = pw.FixedCharField(max_length=17)
    CardAcceptorIdentification = pw.FixedCharField(max_length=20)
    CardAcceptorNameLocation = pw.FixedCharField(max_length=40)
    Track1Data = pw.FixedCharField(max_length=79)
    RetailerData = pw.FixedCharField(max_length=30)
    TransactionCurrencyCode = pw.FixedCharField(max_length=3)
    CurrencyCodeCardholderBilling = pw.FixedCharField(max_length=3)
    PersonalIdentificationNumberPINData = pw.FixedCharField(max_length=16)
    AdditionalAmount = pw.FixedCharField(max_length=15)
    IntegratedCircuitCardICC = pw.TextField()
    CardholdersIdentificationNumberandName = pw.FixedCharField(max_length=100)
    AdditionalAmounts = pw.TextField()
    TerminalData = pw.FixedCharField(max_length=19)
    CardData = pw.FixedCharField(max_length=22)
    TerminalPostalCode = pw.FixedCharField(max_length=13)
    Token1 = pw.TextField()
    Token2 = pw.TextField()
    Token3 = pw.TextField()
    PrimaryMessageAuthenticationCodeMAC = pw.FixedCharField(max_length=16)
    ChannelType = pw.FixedCharField(max_length=15)
    CardType = pw.FixedCharField(max_length=2)
    NoOfInstallment = pw.FixedCharField(max_length=15, null=True)
    InstallmentType = pw.FixedCharField(max_length=15, null=True)
    IssuerRRN = pw.FixedCharField(max_length=15, null=True)
    TxnLoggingTime = pw.DateTimeField(default=datetime.now())



class IssuerDuplicates(IssuerOriginal):
    """ 
    Summary:
        (CCX24 Specific)
        Issuer Duplicate Trnxs Are Kept Here
     """
    pass


class IssuerNotValid(IssuerOriginal):
    """
    Summary:
        if (ForwardingInstitutionCountryCode & CardAcceptorIdentification) == Blank / Null / Empty:
            Issuer Not Valid Trnxs Are Dumped Here Here
    """
    Validation = pw.TextField()
    ExtarctFileId = pw.CharField()


class IssuerExtract(IssuerOriginal):
    """
    Summary:
        All Filtered Trnxs Are Collected Here 
    """
    pass


class IssuerExtractCopy(IssuerOriginal):
    """
    Summary:
        All Issuer Original Trnxs Are Copied Here 
    """
    pass


class TransactionHistoryIssuer(IssuerOriginal):
    class Meta:
        indexes = (
            (('RetrievalReferenceNumber', 'TransmissionDateandTime', 'Track2Data', 'MessageType',
             'ProcessingCode', 'ResponseCode', 'CardAcceptorIdentification'), True),
        )


################## * CCX28 * ##################

class RetailerCommissionRules(MySQLModel):
    """
    Summary:
       Decide The Commission Rule/Flag Here 
    """
    institution_id              = pw.CharField(max_length=8)
    retailer_id                 = pw.CharField(max_length=19)
    channel                     = pw.CharField(max_length=8, default='DEFAULT')
    commision_type               = pw.CharField(max_length=2)
    commision_sub_type           = pw.CharField(max_length=2)
    card_type                   = pw.CharField(max_length=19)
    transaction_identifier      = pw.CharField(max_length=19)
    mcc                         = pw.CharField(max_length=19)
    bin                         = pw.CharField(max_length=19)
    rubro                       = pw.CharField(max_length=19)
    region                      = pw.CharField(max_length=19)
    priority                    = pw.CharField(constraints=[SQL('DEFAULT 1')])
    status                      = pw.BooleanField(default=True)

    class Meta:
        indexes = (
            # Note the trailing comma!
            (('institution_id', 'retailer_id', 'channel','priority'), True),
        )


class RetailerCommissionValues(MySQLModel):
    """
    Summary:
        Decide The Commission Value For Particular Rule Here
    """

    institution_id                      = pw.CharField(max_length=8)
    retailer_id                         = pw.CharField(max_length=19)
    channel                             = pw.CharField(max_length=10)
    message_type                        = pw.CharField(max_length = 4)
    processing_code                     = pw.CharField(max_length = 2)
    response_code                       = pw.CharField(max_length = 2)
    debit_value                         = pw.CharField(max_length=10, default='0.0')
    credit_value                        = pw.CharField(max_length=10, default='0.0')
    prepaid_value                       = pw.CharField(max_length=10, default='0.0')
    mcc                                 = pw.CharField(max_length = 4)
    mcc_debit_value                     = pw.CharField(max_length=10, default='0.0')
    mcc_credit_value                    = pw.CharField(max_length=10, default='0.0')
    mcc_prepaid_value                   = pw.CharField(max_length=10, default='0.0')
    bin                                 = pw.CharField(max_length = 255)
    bin_value                           = pw.CharField(max_length=10, default='0.0')
    domestic_value                      = pw.CharField(max_length=10, default='0.0')
    international_value                 = pw.CharField(max_length=10, default='0.0')
    rubro                               = pw.CharField(max_length = 16, default='000_000')
    rubro_debit_value                   = pw.CharField(max_length=10, default='0.0')
    rubro_credit_value                  = pw.CharField(max_length=10, default='0.0')
    rubro_prepaid_value                 = pw.CharField(max_length=10, default='0.0')
    region                              = pw.CharField(max_length = 19)
    region_debit_value                  = pw.CharField(max_length=19, default='0.0')
    region_credit_value                 = pw.CharField(max_length=19, default='0.0')
    region_prepaid_value                = pw.CharField(max_length=19, default='0.0')

    class Meta:
        indexes = (
            (('institution_id', 'retailer_id', 'channel', 'message_type', 'processing_code',
             'response_code', 'mcc', 'bin'), True),  # Note the trailing comma!
        )


class CommissionSlabRange(MySQLModel):
    institution_id = pw.CharField(max_length=8)
    retailer_id = pw.CharField(max_length=19)
    commision_subtype = pw.CharField(max_length=2)
    low_range = pw.IntegerField()
    high_range = pw.IntegerField()
    value = pw.DecimalField(decimal_places=2)

    class Meta:
        indexes = (
            (('institution_id', 'retailer_id', 'commision_subtype',
             'low_range', 'high_range'), True),  # Note the trailing comma!
        )


class DiscountAndPromotionRules(MySQLModel):
    """
    Summary:
       Decide The Discounts & Promotion Rule/Flag Here 
    """
    institution_id              = pw.CharField(max_length=8)
    retailer_id                 = pw.CharField(max_length=19)
    channel                     = pw.CharField(max_length=8, default='DEFAULT')
    discount_type               = pw.CharField(max_length=2)
    discount_sub_type           = pw.CharField(max_length=2)
    card_type                   = pw.CharField(max_length=19)
    transaction_identifier      = pw.CharField(max_length=19)
    mcc                         = pw.CharField(max_length=19)
    bin                         = pw.CharField(max_length=19)
    rubro                       = pw.CharField(max_length=19)
    region                      = pw.CharField(max_length=19)
    priority                    = pw.CharField(max_length=19)
    status                      = pw.BooleanField(default=True)

    class Meta:
        indexes = (
            # Note the trailing comma!
            (('institution_id', 'retailer_id', 'channel','priority'), True),
        )


class DiscountAndPromotionValues(MySQLModel):
    """
    Summary:
       Decide The Discounts & Promotion Value For Particular Rule Here 
    """
    institution_id                      = pw.CharField(max_length=8)
    retailer_id                         = pw.CharField(max_length=19)
    channel                             = pw.CharField(max_length=10)
    message_type                        = pw.CharField(max_length = 4)
    processing_code                     = pw.CharField(max_length = 2)
    response_code                       = pw.CharField(max_length = 2)
    debit_value                         = pw.CharField(max_length=10, default='0.0')
    credit_value                        = pw.CharField(max_length=10, default='0.0')
    prepaid_value                       = pw.CharField(max_length=10, default='0.0')
    mcc                                 = pw.CharField(max_length = 4)
    mcc_debit_value                     = pw.CharField(max_length=10, default='0.0')
    mcc_credit_value                    = pw.CharField(max_length=10, default='0.0')
    mcc_prepaid_value                   = pw.CharField(max_length=10, default='0.0')
    bin                                 = pw.CharField(max_length = 10)
    bin_value                           = pw.CharField(max_length=10, default='0.0')
    domestic_value                      = pw.CharField(max_length=10, default='0.0')
    international_value                 = pw.CharField(max_length=10, default='0.0')
    rubro                               = pw.CharField(max_length = 16, default='000_000')
    rubro_debit_value                   = pw.CharField(max_length=10, default='0.0')
    rubro_credit_value                  = pw.CharField(max_length=10, default='0.0')
    rubro_prepaid_value                 = pw.CharField(max_length=10, default='0.0')
    region                              = pw.CharField(max_length = 19)
    region_debit_value                  = pw.CharField(max_length=19, default='0.0')
    region_credit_value                 = pw.CharField(max_length=19, default='0.0')
    region_prepaid_value                = pw.CharField(max_length=19, default='0.0')


    class Meta:
        indexes = (
            (('institution_id', 'retailer_id', 'channel', 'message_type', 'processing_code',
             'response_code', 'mcc', 'bin'), True),  # Note the trailing comma!
        )


class DiscountSlabRange(MySQLModel):
    institution_id      = pw.CharField(max_length=8)
    retailer_id         = pw.CharField(max_length=19)
    commision_subtype   = pw.CharField(max_length = 2)
    low_range           = pw.IntegerField()
    high_range          = pw.IntegerField()
    value               = pw.DecimalField(decimal_places=2)

    class Meta:
        indexes = (
        (('institution_id', 'retailer_id', 'commision_subtype', 'low_range', 'high_range'), True),  # Note the trailing comma!
    )

class Retailercompansation(MySQLModel):
    """
    Summary:
        (CC042 Specific)
    """
    RetailerId = pw.CharField(max_length=19)
    EntityId = pw.CharField(max_length=8)
    Channel = pw.CharField(max_length=8)
    CutOverTime = pw.CharField(max_length=8)
    CutOverDays = pw.CharField(max_length=8)
    PendingDays = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey('RetailerId', 'EntityId','Channel')

class NewISERetailer(ISERetailer):
    """
    Summary:
        (CC042 Specific)
       stored value of TxnLoggingTime ( P031 ) 
    """
class NewISERetailerTranxHistory(ISERetailer):
    """
    Summary:
        (CC042 Specific)
       stored value of TxnLoggingTime ( P031 ) 
    """

if __name__ == '__main__':
    pass
    # print(myDB)
    # myDB.drop_tables([AcquirerOriginal,AcquirerNotValid,AcquirerDuplicates,ISERetailer,AcquirerExtract,IssuerOriginal,IssuerDuplicates,IssuerExtract,IssuerExtractCopy,ManualAdjustmentsExtractFile,AllAdjustments,FullDayAcquirerExtract,FullDayAcquirerOriginal,FullDayAcquirerNotValid,FullDayAcquirerDuplicates,AcquirerReversalSuccessPurchaceDecline,NewISERetailerTranxHistory,NewISERetailer,Retailercompansation,DiscountAndPromotionRules,RetailerCommissionRules])
    # myDB.create_tables([AcquirerOriginal,AcquirerNotValid,AcquirerDuplicates,ISERetailer,AcquirerExtract,IssuerOriginal,IssuerDuplicates,IssuerExtract,IssuerExtractCopy,ManualAdjustmentsExtractFile,AllAdjustments,FullDayAcquirerExtract,FullDayAcquirerOriginal,FullDayAcquirerNotValid,FullDayAcquirerDuplicates,AcquirerReversalSuccessPurchaceDecline,NewISERetailerTranxHistory,NewISERetailer,Retailercompansation,DiscountAndPromotionRules,RetailerCommissionRules])

    # myDB.drop_tables([TransactionHistory,Update_TH_ISERetailer,ISERetailerCopy,TransactionHistoryIssuer])
    # myDB.create_tables([TransactionHistory,Update_TH_ISERetailer,ISERetailerCopy,TransactionHistoryIssuer])

