import glob
import numpy as np
import pandas as pd
from shutil import move
from model import RetailerId
from datetime import datetime
from database import DatabaseConnections

file_path = r"./ApiLoaders/Retailer/InputFiles/*.txt"
# file_path = r"./*.txt"
engine = DatabaseConnections().sqlalchemy_connection()
# destination_path = r"./ApiLoaders/Retailer/ProcessedFiles/*.txt"
destination_path = r"./ApiLoaders/Retailer/RefreshLoad/"
renamedCols = {
    'RETAILER_ID': 'RetailerId', 'INSTITUTION_ID': 'EntityId', 'RETAILER_REGION': 'AcquirerRegionCode',
    'RETAILER_LEGAL_NAME': 'CompanyName', 'RETAILER_NAME': 'Name', 'COUNTRY': 'CountryCode',
    'STATE_CODE': 'StateCode', 'CITY_CODE': 'CityCode', 'POSTAL_CODE': 'PostalCode',
    'CONTACT': 'Phone', 'LEGAL_REPRESENTATIVE_EMAIL_ID': 'EmailAddress',
    'IDENTIFICATION_DOC_TYPE': 'IdentificationTypeCode', 'TAX_ID': 'IdentificationNumber',
    'RUBRO_CODE': 'MCC', 'ACCOUNT_ID': 'AccountNumber', 'ACCOUNT_TYPE': 'MovmentType',
    'SETTLEMENT_BANK_CODE': 'BankCode', 'STATUS':'StatusCode',
    'ACCOUNT_TYPE':'MovmentType'
}
reFormatedCol = [
    'RetailerId', 'EntityId', 'GroupCode', 'MallCode', 'AcquirerRegionCode', 'CompanyName', 'Name',
    'CountryCode', 'StateCode', 'CityCode', 'CountyCode', 'Address', 'PostalCode', 'Phone', 'CellPhone', 'FaxPhone',
    'AfterHoursPhone', 'AfterHoursCellPhone', 'AfterHoursFaxPhone',
    'ReferralPhone', 'EmailAddress', 'AlternateEmailAddress', 'IdentificationTypeCode',
    'IdentificationNumber', 'MCC', 'MCCForNoPresentTransaction', 'IdForAmex',
    'MCCForAmex', 'MCCForAmexForNoPresentTransaction', 'WorkingHoursCode',
    'DepositOnLineCode', 'PaymentVendorsCode', 'AffiliationDate',
    'LastUpdateDateNotMonetary', 'LastUpdateDateMonetary', 'StatusCode', 'AssignedAgreeementCode', 'AccountNumber',
    'MovmentType', 'BankCode'
]
getInsertQuery = """
-- * Get Uncommon Trnx For {INSERT}
SELECT
    # COUNT(*)
    *
FROM
    retailerfileload
WHERE
    CONCAT(RetailerId, '#^#', EntityId) NOT IN (
        SELECT
            CONCAT(RetailerId, '#^#', EntityId)
        FROM
            retailerid
    );"""
getUpdateQuery = """
-- * Get Common Trnx {UPDATE}
SELECT
    # COUNT(*)
    *
FROM
    retailerfileload
WHERE
    CONCAT(RetailerId, '#^#', EntityId) IN (
        SELECT
            CONCAT(RetailerId, '#^#', EntityId)
        FROM
            retailerid
    );
"""


engine.execute("CREATE TABLE retailerfileload LIKE retailerid;")
for singleFile in glob.glob(file_path):
    # singleFileDf = pd.read_csv(f'{singleFile}', delimiter='|', dtype='str', error_bad_lines=False, encoding='unicode_escape',on_bad_lines='skip')
    singleFileDf = pd.read_csv(f'{singleFile}', delimiter='|', dtype='str', encoding='unicode_escape',on_bad_lines='skip')
    singleFileDf.rename(columns=renamedCols, inplace=True)
    singleFileDf.drop(singleFileDf.columns[0], axis=1, inplace=True)
    singleFileDf['MovmentType'] = singleFileDf['MovmentType'].replace(np.nan, "")
    singleFileDf['MCC'] = singleFileDf['MCC'].replace(np.nan, 0)
    singleFileDf['CompanyName'] = singleFileDf['CompanyName'].replace(np.nan, "")
    singleFileDf['IdentificationTypeCode'] = singleFileDf['IdentificationTypeCode'].replace(np.nan, 0)
    singleFileDf['StatusCode'] = singleFileDf['StatusCode'].apply(lambda status: 1 if status =="ACTIVE" else (2 if status =="INACTIVE" else(3 if status == "TEMPORARILY BLOCKED" else  4)))
    singleFileDf["CountryCode"] = singleFileDf["CountryCode"].str[:2]
    singleFileDf['GroupCode'], singleFileDf['MallCode'], singleFileDf['CountyCode'] = 0, 0, 0
    singleFileDf['FaxPhone'], singleFileDf['CellPhone'], singleFileDf['AlternateEmailAddress']= "", "", ""
    singleFileDf['AfterHoursPhone'], singleFileDf['AfterHoursCellPhone'], singleFileDf['AfterHoursFaxPhone'] ="","",""
    singleFileDf['ReferralPhone'], singleFileDf['MCCForNoPresentTransaction'] = "", 0
    singleFileDf['IdForAmex'], singleFileDf['MCCForAmex'], singleFileDf['MCCForAmexForNoPresentTransaction'] = "", 0, 0
    singleFileDf['WorkingHoursCode'], singleFileDf['DepositOnLineCode'], singleFileDf['PaymentVendorsCode'] = 0, 0, 0
    singleFileDf['AffiliationDate'], singleFileDf['LastUpdateDateNotMonetary'], singleFileDf['LastUpdateDateMonetary'] = 0, 0, 0
    singleFileDf['AssignedAgreeementCode'], singleFileDf['Address'] = "", ""
    singleFileUpdatedDf = singleFileDf[reFormatedCol]
    del singleFile, singleFileDf
    engine.execute('TRUNCATE TABLE retailerfileload;')
    # print(singleFileUpdatedDf['CountryCode'])
    singleFileUpdatedDf.to_sql('retailerfileload', con=engine, if_exists='append', index=False,)
    # print(f'singleFileUpdatedDf = {singleFileUpdatedDf.shape}')
    # * Bulk Insert Start
    insertCount = pd.read_sql(f'{getInsertQuery}', con=engine)
    if not insertCount.empty:
        insertCount.to_sql('retailerid', con=engine, if_exists='append', index=False, chunksize=1000, method='multi')
        # print(insertCount.head())
        # print(insertCount.shape)
    # * Each Row Update
    updateCount = pd.read_sql(f'{getUpdateQuery}', con=engine)
    if not updateCount.empty:
        # print(updateCount.head())
        # print(updateCount.shape)
        for eachRow in updateCount.to_dict(orient='records'):
            # print(f'eachRow = {eachRow}')
            RetailerId.update(**eachRow).where(RetailerId.RetailerId == eachRow['RetailerId'],RetailerId.EntityId == eachRow['EntityId']).execute()
        del eachRow
    if not insertCount.empty:
        print(f'Insert Count = {insertCount.shape[0]} || Update Count= {updateCount.shape[0]} || Total = {len(RetailerId)}')
    else:
        print(f'Insert Count = {insertCount.shape[0]} || Update Count= {updateCount.shape[0]} || Total = {len(RetailerId)}')

    for singleFile in glob.glob(file_path):
        print(singleFile)
    try:
        move(singleFile, destination_path)
    except Exception as estadoMvError:
        print(f"Error: estadoMvError = {estadoMvError}")

    del updateCount, insertCount
    print()
    # break
engine.execute('DROP TABLE retailerfileload;')
del engine

