from sys import argv
from glob import glob
from model import myDB
from shutil import move
from config import Config
from os import system, path
from secrets import token_hex
from datetime import datetime
from bs4 import BeautifulSoup
from peewee import fn, chunked
from pandas import read_sql_table
from os import system, chdir, path
from file_transfer import file_transfer
from database import DatabaseConnections
from model import FullDayAcquirerExtract, Chile_Report, Estado_Report
from pandas import read_sql_table, read_sql, read_sql_query, DataFrame
from base_liquidation import fullDayAcquirerExtractLoad, create_directories, fullDayLiquidation
from model import EstadoIdpUpdate, ChileIdpUpdate, ValeVista, RetailerId, CurrentDateTransactionHistory, FullDayTransactionRetailerHistory, FullDayTransactionHistory


# * Fetch DB Connection
db_instance = DatabaseConnections()
db_con = db_instance.peewee_connection()
today = datetime.now().strftime(r"%d-%m-%Y")
sqlEngine = db_instance.sqlalchemy_connection()
destLoc = fr"./AcquirerExtractFullDay/ProcessedExtracts/{datetime.now().strftime(r'%b_%Y')}/"
inputReportLoc = r"./AcquirerExtractFullDay/InputExtracts/*"
reportLocation = create_directories(fr"./CompensationReports/DepositRetailerReports/", fr"{datetime.now().strftime(r'%b_%Y')}")
config = Config().get_config_json()
dbName = config['DB_NAME']
system(f"mkdir -p {destLoc}")
system(f"mkdir -p {reportLocation}BK")


def get_acnum_chile(bankCode: str, acType: str) -> str :
    """
    Summary:
        Change AccType Based On Combination Of [bankCode + acType]

    Args:
        bankCode (str): BankCode From RetailerId Table
        acType (str): ACType From RetailerId Table

    Returns:
        str: AccountType based on combo
    """
    if bankCode == "001" and acType == "3": return "01"
    elif bankCode == "504" and acType == "3": return "07"
    elif bankCode == "028" and acType == "3": return "07"
    elif bankCode == "055" and acType == "3": return "07"
    elif bankCode == "027" and acType == "3": return "07"
    elif bankCode == "016" and acType == "3": return "07"
    elif bankCode == "507" and acType == "3": return "07"
    elif bankCode == "051" and acType == "3": return "07"
    elif bankCode == "009" and acType == "3": return "07"
    elif bankCode == "039" and acType == "3": return "07"
    elif bankCode == "053" and acType == "3": return "07"
    elif bankCode == "037" and acType == "3": return "07"
    elif bankCode == "049" and acType == "3": return "07"
    elif bankCode == "672" and acType == "3": return "07"
    elif bankCode == "031" and acType == "3": return "07"
    elif bankCode == "014" and acType == "3": return "07"
    elif bankCode == "001" and acType == "22": return "01"
    elif bankCode == "001" and acType == "4": return "06"
    elif bankCode == "504" and acType == "22": return "07"
    elif bankCode == "504" and acType == "4": return "08"
    elif bankCode == "028" and acType == "22": return "07"
    elif bankCode == "028" and acType == "4": return "08"
    elif bankCode == "055" and acType == "22": return "07"
    elif bankCode == "055" and acType == "4": return "08"
    elif bankCode == "027" and acType == "22": return "07"
    elif bankCode == "027" and acType == "4": return "08"
    elif bankCode == "016" and acType == "22": return "07"
    elif bankCode == "016" and acType == "4": return "08"
    elif bankCode == "507" and acType == "22": return "07"
    elif bankCode == "507" and acType == "4": return "08"
    elif bankCode == "051" and acType == "22": return "07"
    elif bankCode == "051" and acType == "4": return "08"
    elif bankCode == "009" and acType == "22": return "07"
    elif bankCode == "009" and acType == "4": return "08"
    elif bankCode == "039" and acType == "22": return "07"
    elif bankCode == "039" and acType == "4": return "08"
    elif bankCode == "053" and acType == "22": return "07"
    elif bankCode == "053" and acType == "4": return "08"
    elif bankCode == "037" and acType == "22": return "07"
    elif bankCode == "037" and acType == "4": return "08"
    elif bankCode == "049" and acType == "22": return "07"
    elif bankCode == "049" and acType == "4": return "08"
    elif bankCode == "672" and acType == "22": return "07"
    elif bankCode == "672" and acType == "4": return "08"
    elif bankCode == "031" and acType == "22": return "07"
    elif bankCode == "031" and acType == "4": return "08"
    elif bankCode == "014" and acType == "22": return "07"
    elif bankCode == "014" and acType == "4": return "08"


def updateRetailerDataForIdpUpdateTables() -> None:
    # TODO : check bankcode of update records if it is 012 then move record to estado idp with proper latest data (query on chile idp)
    # TODO : check bankcode of update records if it is != 012 then move record to chile idp with proper latest data (query on estado idp)
    # TODO : update AccountType for both table seperately after the above tasks 
    chileIdpUpdte = ChileIdpUpdate.select().dicts().iterator()
    for eachRecord in [k for k in chileIdpUpdte]:
        retQuery = (RetailerId
                    .select(RetailerId.IdentificationNumber.alias('Ruth'),
                            RetailerId.IdentificationNumber.alias('Dv'),
                            RetailerId.EntityId.alias('InsId'),
                            RetailerId.EmailAddress.alias('EmailId'),
                            RetailerId.BankCode.alias('BankCode'),
                            RetailerId.MovmentType.alias('AcType'),
                            RetailerId.AccountNumber.alias('AcNum'),
                            RetailerId.Name.alias('RetName'))
                    .where((RetailerId.RetailerId == eachRecord["RetId"]) &
                            (RetailerId.EntityId == eachRecord["InsId"])
                            ).dicts().iterator())
        retData = [k for k in retQuery][0]

        if '-' in retData['Ruth']:
            retData['Dv'] = retData['Dv'].split("-")[1]
        else:
            retData['Dv'] = ''

        if (retData['AcType'] != "") and (retData['AcType'] != " "):
            if get_acnum_chile(retData['BankCode'], str(int(retData['AcType']))) != None:
                retData['AcType'] = get_acnum_chile(retData['BankCode'], str(int(retData['AcType'])))
                # print("Testing = ", updatedRetData['BankCode'], str(int(updatedRetData['AcType'])))
            retData['AcType'] = retData['AcType'].rjust(2, "0")

        # print(retData)
        ChileIdpUpdate.update(
            Ruth=retData['Ruth'], Dv=retData['Dv'], EmailId=retData['EmailId'],
            AcNum=retData['AcNum'], AcType=retData['AcType'], BankCode=retData['BankCode']).where(
                (ChileIdpUpdate.InsId == eachRecord['InsId']) & (ChileIdpUpdate.RetId == eachRecord['RetId'])
        ).execute()
        del retData, eachRecord 
    del chileIdpUpdte

    estadoIdpUpdte = EstadoIdpUpdate.select().dicts().iterator()
    for eachRecord in [k for k in estadoIdpUpdte]:
        retQuery = (RetailerId
                    .select(RetailerId.IdentificationNumber.alias('Ruth'),
                            RetailerId.IdentificationNumber.alias('Dv'),
                            RetailerId.EntityId.alias('InsId'),
                            RetailerId.EmailAddress.alias('EmailId'),
                            RetailerId.BankCode.alias('BankCode'),
                            RetailerId.MovmentType.alias('AcType'),
                            RetailerId.AccountNumber.alias('AcNum'),
                            RetailerId.Name.alias('RetName'))
                    .where((RetailerId.RetailerId == eachRecord["RetId"]) &
                            (RetailerId.EntityId == eachRecord["InsId"])
                            ).dicts().iterator())
        retData = [k for k in retQuery][0]
    
        if retData['AcType'] == "3": retData['AcType'] = '01'
        elif retData['AcType'] == "4": retData['AcType'] = '02'
        elif retData['AcType'] == "22": retData['AcType'] = '22'

        try:
            if "-" in retData['Ruth']:
                retData['Dv'] = retData['Dv'].split("-")[1]
            else:
                retData['Dv'] = ""
        except Exception as err:
            print(f"Error At [db_cursor] Ruth/Dv split : {err}")

        # print(retData)
        EstadoIdpUpdate.update(
            Ruth=retData['Ruth'], Dv=retData['Dv'], EmailId=retData['EmailId'],
            AcNum=retData['AcNum'], AcType=retData['AcType'], BankCode=retData['BankCode']).where(
                (EstadoIdpUpdate.InsId == eachRecord['InsId']) & (EstadoIdpUpdate.RetId == eachRecord['RetId'])
        ).execute()

        del retData, eachRecord
    del estadoIdpUpdte


def copyToFullDayTransactionRetailerHistory() -> None:
    """
    Summary: 
        Copy data from Chile_Report & Estado_Report To FullDayTransactionRetailerHistory
        Before inserting we need to combine the spit trnxs of 5000000 to single trnx
    """

    getSumFinalAmtEstado = read_sql_query("""SELECT DISTINCT (RetID), SUM(FinalAmt) AS FinalAmt FROM estado_report GROUP BY RetID;""", con=sqlEngine)
    estadoReportUnique = read_sql_table('estado_report', con=sqlEngine).drop_duplicates('IDP')
    try: del estadoReportUnique['id']
    except Exception as err: print(f"No Id Col In estadoReport = {err}")
    del estadoReportUnique['FinalAmt']  # delete old column
    estadoReportUnique['FinalAmt'] = list(getSumFinalAmtEstado['FinalAmt'])
    estadoReportUnique['InsertedDate'] = [today for k in range(estadoReportUnique.shape[0])]
    estadoReportUnique['UpdatedDate'] = [today for k in range(estadoReportUnique.shape[0])] 
    # print(f"getSumFinalAmtEstado :-\n {getSumFinalAmtEstado}")
    # print(f"estadoReportUnique :-\n {estadoReportUnique.columns}")
    # print(f"estadoReportUnique :-\n {estadoReportUnique}")
    # print(f"estadoReportUnique :-\n {estadoReportUnique[['RetId', 'FinalAmt']]}")
    # print(f"estadoReportUnique :-\n {estadoReportUnique[['UpdatedDate', 'InsertedDate']]}")
    # print(f"estadoReportUnique :-\n {estadoReportUnique[['BrodcastDate', 'DepositDate']]}")
    # try: estadoReportUnique.to_sql(name='fulldaytransactionretailerhistory', con=sqlEngine, if_exists='append', index=False)
    # except Exception as err1: print(f"err1 = {err1.args}")
    for eru in estadoReportUnique.to_dict(orient='records'):
        # print(eru['BrodcastDate'], eru['DepositDate'])
        try: FullDayTransactionRetailerHistory.insert(**eru).execute()
        except Exception as err1:
            # TODO : Update All Retailer Data [ruth, dv, retname, actype, bankcode, actno, emailid] (FullDayTransactionRetailerHistory & FullDayTransactionHistory)
            FullDayTransactionRetailerHistory.update(FinalAmt=eru['FinalAmt']).execute()
            print(f"Update Query estadoReportUnique = {err1.args}")

    getSumFinalAmtChile = read_sql_query("""SELECT DISTINCT (RetID), SUM(FinalAmt) AS FinalAmt FROM chile_report GROUP BY RetID;""", con=sqlEngine)
    chileReportUnique = read_sql_table('chile_report', con=sqlEngine).drop_duplicates('DocNum')
    chileReportUnique.rename(columns={'DocNum': 'IDP'}, inplace=True)
    # print(f"chileReportUnique :-\n {chileReportUnique.columns}")
    try: del chileReportUnique['id']
    except Exception as err: print(f"No Id Col In estadoReport = {err}")
    del chileReportUnique['FinalAmt']  # delete old column
    chileReportUnique['FinalAmt'] = list(getSumFinalAmtChile['FinalAmt'])
    chileReportUnique['InsertedDate'] = [today for k in range(chileReportUnique.shape[0])]
    chileReportUnique['UpdatedDate'] = [today for k in range(chileReportUnique.shape[0])]
    # print(f"getSumFinalAmtChile :-\n {getSumFinalAmtChile}")
    # print(f"chileReportUnique :-\n {chileReportUnique.columns}")
    # print(f"chileReportUnique :-\n {chileReportUnique}")
    # print(f"chileReportUnique :-\n {chileReportUnique[['RetId', 'FinalAmt']]}")
    # print(f"chileReportUnique :-\n {chileReportUnique[['UpdatedDate', 'InsertedDate']]}")
    # print(f"chileReportUnique :-\n {chileReportUnique[['BrodcastDate', 'DepositDate']]}")
    # try: chileReportUnique.to_sql(name='fulldaytransactionretailerhistory', con=sqlEngine, if_exists='append', index=False)
    # except Exception as err2: print(f"err1 = {err2.args}")
    for cru in chileReportUnique.to_dict(orient='records'):
        # print(cru['BrodcastDate'], cru['DepositDate'])
        try: FullDayTransactionRetailerHistory.insert(**cru).execute()
        except Exception as err2:
            # TODO : Update All Retailer Data [ruth, dv, retname, actype, bankcode, actno, emailid] (FullDayTransactionRetailerHistory & FullDayTransactionHistory)
            FullDayTransactionRetailerHistory.update(FinalAmt=cru['FinalAmt']).execute()
            print(f"Update Query chileReportUnique = {err2.args}")


def split_max_amount(maxAmt: int, tableName: str) -> None:
    """
    Summary:
        Split Trnxs > 5000000 Into Slabs :-
        Example :- 
            IDP001abc merchant1 codigo banco ... 5000000 -> linea1
            IDP001abc merchant1 codigo banco ... 900000 -> linea2

            Input payment failed 

            Retry next day

            total net amount = 5900000 (old transactions) + 100000 (current deposit day) = 6000000 

            IDP002abc merchant1 codigo banco ... 5000000 -> linea1
            IDP002abc merchant1 codigo banco ... 1000000 -> linea2     

    Args:
        maxAmt (int): max amount allowed in single line
        tableName (str): name of table
    """
    if maxAmt == 0 or maxAmt < 0 :
        return None

    noOfRows = read_sql_query(f""" SELECT FinalAmt DIV {maxAmt} AS NoOfRows FROM {tableName} WHERE FinalAmt >= {maxAmt} order by FinalAmt; """,
                              con=sqlEngine)
    if not noOfRows.empty:
        # print(f"noOfRows = {noOfRows}\n")
        # data = read_sql_query(f""" SELECT DocNum, RetId, InsId, FinalAmt FROM {tableName} WHERE FinalAmt >= {maxAmt} order by FinalAmt; """,
        data = read_sql_query(f""" SELECT * FROM {tableName} WHERE FinalAmt >= {maxAmt} order by FinalAmt; """, con=sqlEngine)
        if not data.empty:
            # print(f"## data = \n{data}\n")
            tempDf = DataFrame(columns=data.columns)
            for k in range(data.shape[0]):
                finalAmt= float(data.iloc[[k]]['FinalAmt'].astype(float))
                if finalAmt > maxAmt:
                    # print("-"*150)
                    # print(f"Current RetId & Amount = {data.iloc[[k]]['RetId'].to_string().replace(' ', '')[1:]} | {data.iloc[[k]]['FinalAmt'].to_string().replace(' ', '')[1:]}")
                    nor = int(noOfRows['NoOfRows'].to_list()[k])
                    # print(f"rows after split = {noOfRows['NoOfRows'].to_list()} | {nor}")
                    splitDf = tempDf.append([data.iloc[[k]]]*nor, ignore_index=True)
                    splitDf['FinalAmt'] = splitDf['FinalAmt'].astype(float).astype(int).apply(lambda x: maxAmt)
                    splitCombineAmt = float(splitDf['FinalAmt'].astype(float).astype(int).sum())
                    if finalAmt != splitCombineAmt: 
                        finalDf = splitDf.append([data.iloc[[k]]]*1, ignore_index=True) 
                        finalDf.at[nor, 'FinalAmt'] = finalAmt - splitCombineAmt
                        try: del finalDf['id']
                        except Exception as err: print(f"No Id Col In finalDf['id'] = {err}")
                        # print(finalDf)
                        finalDfCombineAmt = float(finalDf['FinalAmt'].astype(float).astype(int).sum())
                        # print(f"Diff in count = {finalDf.iloc[-1]['FinalAmt']}")
                        # print(f"FinalAmt = {finalDfCombineAmt} | {finalAmt}\n")
                        if tableName == "chile_report":
                            # # print(f"{finalDf.iloc[0]}")
                            Chile_Report.delete().where(Chile_Report.DocNum == finalDf.iloc[0]['DocNum']).execute()
                            finalDf.to_sql('chile_report', con=sqlEngine, if_exists='append', index=False)
                            # print(f"finalDf :- Delete / Insert :- {tableName}")
                        elif tableName == "estado_report":
                            # print(f"{finalDf.iloc[0]}")
                            Estado_Report.delete().where(Estado_Report.IDP == finalDf.iloc[0]['IDP']).execute()
                            finalDf.to_sql('estado_report', con=sqlEngine, if_exists='append', index=False)
                            # print(f"finalDf :- Delete / Insert :- {tableName}")
                    else:
                        try: del splitDf['id']
                        except Exception as err: print(f"No Id Col In splitDf['id'] = {err}")
                        # print(f"FinalAmt = {splitCombineAmt} | {finalAmt}\n")
                        if tableName == "chile_report":
                            # # print(f"{splitDf.iloc[0]}")
                            Chile_Report.delete().where(Chile_Report.DocNum == finalDf.iloc[0]['DocNum']).execute()
                            splitDf.to_sql('chile_report', con=sqlEngine, if_exists='append', index=False)
                            # print(f"splitDf :- Delete / Insert :- {tableName}")
                        elif tableName == "estado_report":
                            # print(f"{splitDf.iloc[0]}")
                            Estado_Report.delete().where(Estado_Report.IDP == splitDf.iloc[0]['IDP']).execute()
                            splitDf.to_sql('estado_report', con=sqlEngine, if_exists='append', index=False)
                            # print(f"splitDf :- Delete / Insert :- {tableName}")



def combine_duplicate_chile() -> None:
    """ 
    Summary : Combine Duplicate RetId's Amount & Make Single Entry In Reports 
    # TODO : Analysis For Same IDP Num is peding
    """

    data = read_sql("""
    SELECT
            RetId,
            Ruth,
            sum(FinalAmt) AS TotalFinalAmt,
            SUBSTRING_INDEX(GROUP_CONCAT(SUBSTRING_INDEX(DocNum, "NAN", 1) ORDER BY DocNum DESC), ",", 1) AS LatestIDP
    FROM chile_report
    WHERE Ruth IN (
            SELECT Ruth
            FROM chile_report
            GROUP BY Ruth
            HAVING count(Ruth) > 1)
    GROUP BY Ruth;
    """, con=sqlEngine)
    if not data.empty :
        # print(f"data = \n{data}\n")
        for eachRecord in data.to_dict(orient='records'):
            # print(f"eachRecord = {eachRecord}") # * Each Result From Query
            retData = (RetailerId
                .select(RetailerId.IdentificationNumber.alias('Ruth'), 
                        RetailerId.IdentificationNumber.alias('Dv'),
                        RetailerId.EntityId.alias('InsId'),
                        RetailerId.EmailAddress.alias('EmailId'), 
                        RetailerId.BankCode.alias('BankCode'),
                        RetailerId.MovmentType.alias('AcType'), 
                        RetailerId.AccountNumber.alias('AcNum'),
                        RetailerId.Name.alias('RetName'))
                    .where(RetailerId.RetailerId == f'{eachRecord["RetId"]}').dicts())
            updatedRetData = [k for k in retData][0]
            getBigIdpER = (Chile_Report.select().where(
                (Chile_Report.RetId == f'{eachRecord["RetId"]}') &
                (Chile_Report.Ruth == f'{eachRecord["Ruth"]}') &
                (Chile_Report.DocNum.startswith(f'{eachRecord["LatestIDP"]}'))
            ).dicts())
            if '-' in updatedRetData['Ruth']: 
                updatedRetData['Ruth'] = updatedRetData['Ruth'].split("-")[0]
                updatedRetData['Dv'] = updatedRetData['Dv'].split("-")[1]
            else:
                updatedRetData['Dv'] = ''
            # print(f"NewRetData = {updatedRetData}") # * New Retailer Data
            gotOldRowToUpdate = [k for k in getBigIdpER][0]
            # print(f"Old = {gotOldRowToUpdate}") # * Old Row Data
            gotOldRowToUpdate['InsId'] = updatedRetData['InsId']
            gotOldRowToUpdate['Ruth'], gotOldRowToUpdate['RetName'] = updatedRetData['Ruth'], updatedRetData['RetName']
            gotOldRowToUpdate['EmailId'], gotOldRowToUpdate['BankCode'] = updatedRetData['EmailId'], updatedRetData['BankCode']
            if (updatedRetData['AcType'] != "") and (updatedRetData['AcType'] != " "):
                if get_acnum_chile(updatedRetData['BankCode'], str(int(updatedRetData['AcType']))) != None:
                    updatedRetData['AcType'] = get_acnum_chile(updatedRetData['BankCode'], str(int(updatedRetData['AcType'])))
                    # print("Testing = ", updatedRetData['BankCode'], str(int(updatedRetData['AcType'])))
                gotOldRowToUpdate['AcType'] = updatedRetData['AcType'].rjust(2, "0")
            gotOldRowToUpdate['AcNum'], gotOldRowToUpdate['FinalAmt'] = updatedRetData['AcNum'], eachRecord['TotalFinalAmt']
            # print(f"New = {gotOldRowToUpdate}") # * New Row Data
            Chile_Report.delete().where(Chile_Report.RetId == f'{eachRecord["RetId"]}').execute()
            Chile_Report.insert(**gotOldRowToUpdate).execute()
            # break # * kept for debug


def combine_duplicate_estado() -> None:
    """ 
    Summary : Combine Duplicate RetId's Amount & Make Single Entry In Reports 
    # TODO : Analysis For Same IDP Num is peding
    """

    data = read_sql("""
    SELECT
            RetId,
            Ruth,
            sum(FinalAmt) AS TotalFinalAmt,
            SUBSTRING_INDEX(GROUP_CONCAT(SUBSTRING_INDEX(IDP, "NAN", 1) ORDER BY IDP DESC), ",", 1) AS LatestIDP
    FROM estado_report
    WHERE Ruth IN (
            SELECT Ruth
            FROM estado_report
            GROUP BY Ruth
            HAVING count(Ruth) > 1)
    GROUP BY Ruth;
    """, con=sqlEngine)
    if not data.empty :
        # print(f"data = {data}\n")
        for eachRecord in data.to_dict(orient='records'):
            # print(f"eachRecord = {eachRecord}") # * Each Result From Query
            retData = (RetailerId
                    .select(RetailerId.IdentificationNumber.alias('Ruth'),
                            RetailerId.EmailAddress.alias('EmailId'),
                            RetailerId.BankCode.alias('BankCode'),
                            RetailerId.MovmentType.alias('AcType'),
                            RetailerId.AccountNumber.alias('AcNum'),
                            RetailerId.Name.alias('RetName'),
                            RetailerId.EntityId.alias('InsId'))
                    .where(RetailerId.RetailerId == f'{eachRecord["RetId"]}').dicts())
            updatedRetData = [k for k in retData][0]
            getBigIdpER = (Estado_Report.select().where(
                (Estado_Report.RetId == f'{eachRecord["RetId"]}') &
                (Estado_Report.Ruth == f'{eachRecord["Ruth"]}') &
                (Estado_Report.IDP.startswith(f'{eachRecord["LatestIDP"]}'))
            ).dicts())
            # print(f"NewRetData = {updatedRetData}") # * New Retailer Data
            gotOldRowToUpdate = [k for k in getBigIdpER][0]
            hexVal = gotOldRowToUpdate['IDP'].split('NAN')[1]
            # IdpCnt = str(int(gotOldRowToUpdate['IDP'].split('NAN')[0].split('IDP')[1]) + 1).rjust(3, '0') # ! might not req
            # updateIdp = f"IDP{IdpCnt}NAN{hexVal}"  # ! might not req
            # print(f"Old = {gotOldRowToUpdate}") # * Old Row Data
            # gotOldRowToUpdate['InsId'] = updateIdp # ! might not req
            gotOldRowToUpdate['InsId'] = updatedRetData['InsId']
            gotOldRowToUpdate['Ruth'], gotOldRowToUpdate['RetName'] = updatedRetData['Ruth'], updatedRetData['RetName']
            gotOldRowToUpdate['EmailId'], gotOldRowToUpdate['BankCode'] = updatedRetData['EmailId'], updatedRetData['BankCode']
            if updatedRetData['AcType'] == "3": gotOldRowToUpdate['AcType'] = '01'
            elif updatedRetData['AcType'] == "4": gotOldRowToUpdate['AcType'] = '02'
            gotOldRowToUpdate['AcNum'], gotOldRowToUpdate['FinalAmt'] = updatedRetData['AcNum'], eachRecord['TotalFinalAmt']
            # print(f"New = {gotOldRowToUpdate}") # * New Row Data
            Estado_Report.delete().where(Estado_Report.RetId == f'{eachRecord["RetId"]}').execute()
            Estado_Report.insert(**gotOldRowToUpdate).execute()
            # break # * kept for debug


def db_cursor(retIdConcatDistinct, reportName) -> list:
    """
    Summary/Usage:
        - Fetch Data Of Each Retailer From RetailerId Table
        - Fetch Final Amount -> [ Total Amount = (Financial + Refund Reversal) - (Reversal + Refund) ] 

    Args:
        retIdConcatDistinct (_type_): Iterator For Loop
        reportName (_type_): Fetch Data From RetailerId Table

    Returns:
        list, list:
            - chileList - Array Of All Txns (BancoChile) With Each Element/Transaction In Dictionary Form
            - estadoList - Array Of All Txns (BancoEstado) With Each Element/Transaction In Dictionary Form 
    """

    estadoList, chileList = [], []

    # try:
    # * Peewee ORM Based Cursor
    for eachRow in retIdConcatDistinct:
        # print(f"eachRow = {eachRow}") # * kept for debug
        retIdDataBE, retIdDataBC, finalAmt = '', '', 0.0
        RetId = eachRow.get('verifiedRetIdData').split('#^#')[0]
        InstId = eachRow.get('verifiedRetIdData').split('#^#')[1]
        del eachRow

        purchaseAmt = (
            CurrentDateTransactionHistory
            .select(fn.SUM(CurrentDateTransactionHistory.FinalAmount).alias('purchaseAmt'))
            .where((CurrentDateTransactionHistory.MessageType == "0210") & (CurrentDateTransactionHistory.ProcessingCode == "000000") &
                   (CurrentDateTransactionHistory.ResponseCode == "00") & (CurrentDateTransactionHistory.CardAcceptorIdentification == RetId) &
                   (CurrentDateTransactionHistory.AcquiringInstitutionIdentification == InstId))
        ).dicts().iterator()
        purAmt = next(purchaseAmt).get('purchaseAmt', 'NAN')
        purAmt = 0 if purAmt == None else purAmt
        del purchaseAmt

        refRevAmt = (
            CurrentDateTransactionHistory
            .select(fn.SUM(CurrentDateTransactionHistory.FinalAmount).alias('refRevAmt'))
            .where((CurrentDateTransactionHistory.MessageType == "0420") & (CurrentDateTransactionHistory.ProcessingCode == "200000") &
                   (CurrentDateTransactionHistory.ResponseCode == "00") & (CurrentDateTransactionHistory.CardAcceptorIdentification == RetId) &
                   (CurrentDateTransactionHistory.AcquiringInstitutionIdentification == InstId))
        ).dicts().iterator()
        refrevAmt = next(refRevAmt).get('refRevAmt', 'NAN')
        refrevAmt = 0 if refrevAmt == None else refrevAmt
        del refRevAmt

        reversalAmt = (
            CurrentDateTransactionHistory
            .select(fn.SUM(CurrentDateTransactionHistory.FinalAmount).alias('reversalAmt'))
            .where((CurrentDateTransactionHistory.MessageType == "0420") & (CurrentDateTransactionHistory.ProcessingCode == "000000") &
                   (CurrentDateTransactionHistory.ResponseCode == "00") & (CurrentDateTransactionHistory.CardAcceptorIdentification == RetId) &
                   (CurrentDateTransactionHistory.AcquiringInstitutionIdentification == InstId))
        ).dicts().iterator()
        revAmt = next(reversalAmt).get('reversalAmt', 'NAN')
        revAmt = 0 if revAmt == None else revAmt
        del reversalAmt

        refundAmt = (
            CurrentDateTransactionHistory
            .select(fn.SUM(CurrentDateTransactionHistory.FinalAmount).alias('refundAmt'))
            .where((CurrentDateTransactionHistory.MessageType == "0210") & (CurrentDateTransactionHistory.ProcessingCode == "200000") &
                   (CurrentDateTransactionHistory.ResponseCode == "00") & (CurrentDateTransactionHistory.CardAcceptorIdentification == RetId) &
                   (CurrentDateTransactionHistory.AcquiringInstitutionIdentification == InstId))
        ).dicts().iterator()
        refAmt = next(refundAmt).get('refundAmt', 'NAN')
        refAmt = 0 if refAmt == None else refAmt
        del refundAmt

        finalAmt = round((float(purAmt)+float(refrevAmt)) - (float(revAmt)+float(refAmt)))

        if reportName == "BancoEstado":
            # print("BancoEstado") # * kept for debug
            retIdDataBE = (
                RetailerId
                .select(RetailerId.IdentificationNumber.alias('Ruth'), RetailerId.IdentificationNumber.alias('Dv'),
                        RetailerId.EmailAddress.alias('EmailId'), RetailerId.BankCode.alias('BankCode'), 
                        RetailerId.MovmentType.alias('AcType'),RetailerId.AccountNumber.alias('AcNum'), 
                        RetailerId.Name.alias('RetName'), RetailerId.StatusCode.alias('RetailerStatus'), 
                        RetailerId.AcquirerRegionCode.alias('Region'))
                .where((RetailerId.RetailerId == RetId) & (RetailerId.EntityId == InstId))
            ).dicts().iterator()
            
            # * Table Structure / Sequence
            # RetId, InsId, Ruth, RetName, EmailId, BankCode, AcType, AcNum, FinalAmt, DepositDate, BrodcastDate
            q1 = (EstadoIdpUpdate
                  .select(EstadoIdpUpdate.RetId, EstadoIdpUpdate.InsId, EstadoIdpUpdate.IDP)
                  .where(EstadoIdpUpdate.RetId == RetId, EstadoIdpUpdate.InsId == InstId).dicts().iterator())
            estadoIdpUpdateData = [k for k in q1]
            # print(estadoIdpUpdateData)
            if len(estadoIdpUpdateData) != 0:
                retidData = {'RetId': RetId, 'InsId': InstId, 'IDP': f"{estadoIdpUpdateData[0]['IDP']}", **next(retIdDataBE), 'FinalAmt': finalAmt}
                # print(f"retidData Old = {retidData['Ruth']} | {retidData['FinalAmt']}")
            else:
                retidData = {'RetId': RetId, 'InsId': InstId, 'IDP': f'IDP001NAN{token_hex(6)[:11]}', **next(retIdDataBE), 'FinalAmt': finalAmt}
                # print(f"retidData New = {retidData['Ruth']} | {retidData['FinalAmt']}")

            if retidData['AcType'] == "3": retidData['AcType'] = '01'
            elif retidData['AcType'] == "4": retidData['AcType'] = '02'
            elif retidData['AcType'] == "22": retidData['AcType'] = '22'

            try:
                if "-" in retidData['Ruth']:
                    retidData['Dv'] = retidData['Dv'].split("-")[1]
                else:
                    retidData['Dv'] = ""
            except Exception as err:
                print(f"Error At [db_cursor] Ruth/Dv split : {err}")

            if int(retidData['FinalAmt']) > 0: estadoList.append(retidData)

            # print(f"RetId = {RetId} || InstId = {InstId} || purAmt = {purAmt}", end="")
            # print(f" || refrevAmt = {refrevAmt} || revAmt = {revAmt} || refAmt = {refAmt}  || finalAmt = {finalAmt}\n", end="")
            # print(f"{retidData}\n")
            del retIdDataBE, retidData
            del RetId, InstId, purAmt, refrevAmt, revAmt, refAmt, finalAmt

        elif reportName == "BancoChile":
            # print("BancoChile")
            retIdDataBC = (
                RetailerId
                .select(RetailerId.IdentificationNumber.alias('Ruth'), RetailerId.IdentificationNumber.alias('Dv'),
                        RetailerId.EmailAddress.alias('EmailId'), RetailerId.BankCode.alias('BankCode'),
                        RetailerId.MovmentType.alias('AcType'), RetailerId.AccountNumber.alias('AcNum'),
                        RetailerId.Name.alias('RetName'), RetailerId.StatusCode.alias('RetailerStatus'), 
                        RetailerId.AcquirerRegionCode.alias('Region'))
                .where((RetailerId.RetailerId == RetId) & (RetailerId.EntityId == InstId))
            ).dicts().iterator()

            # * Table Structure / Sequence
            # StartColumn, Ruth, Dv, RetName, DocType, DocNum, BrodcastDate, FinalAmt, Observation, AcType, BankCode, AcNum, Warning, EmailId, EndColumn
            # * Commented By Dishant [20 Dec 2022] : Update the old idp of chile 
            q1 = (ChileIdpUpdate
                  .select(ChileIdpUpdate.RetId, ChileIdpUpdate.InsId, ChileIdpUpdate.DocNum)
                  .where(ChileIdpUpdate.RetId == RetId, ChileIdpUpdate.InsId == InstId).dicts().iterator())
            chileIdpUpdateData = [k for k in q1]
            # print(chileIdpUpdateData)

            if len(chileIdpUpdateData) != 0:
                retidData = {'RetId': RetId, 'InsId': InstId, 'DocNum': f"{chileIdpUpdateData[0]['DocNum']}", **next(retIdDataBC), 'FinalAmt': finalAmt}
                # print(f"retidData Old = {retidData['Ruth']} | {retidData['FinalAmt']}")
            else:
                retidData = {'RetId': RetId, 'InsId': InstId, 'DocNum': f'IDP001NAN{token_hex(6)[:11]}', **next(retIdDataBC), 'FinalAmt': finalAmt}
                # print(f"retidData New = {retidData['Ruth']} | {retidData['FinalAmt']}")

            if get_acnum_chile(retidData['BankCode'], retidData['AcType']) != None: 
                retidData['AcType'] = get_acnum_chile(retidData['BankCode'], str(int(retidData['AcType'])))

            if (retidData['AcType'] != "") and (retidData['AcType'] != " "): 
                retidData['AcType'] = retidData['AcType'].rjust(2, "0")

            try: 
                if "-" in retidData['Ruth']:
                    retidData['Dv'] = retidData['Dv'].split("-")[1]
                else:
                    retidData['Dv'] = ""
            except Exception as err:
                print(f"Error At [db_cursor] Ruth/Dv split : {err}")

            if int(retidData['FinalAmt']) > 0: chileList.append(retidData)

            # print(f"RetId = {RetId} || InstId = {InstId} || purAmt = {purAmt}", end="")
            # print(f" || refrevAmt = {refrevAmt} || revAmt = {revAmt} || refAmt = {refAmt}  || finalAmt = {finalAmt}\n", end="")
            # print(f"{retidData}\n")
            del retIdDataBC, retidData
            del RetId, InstId, purAmt, refrevAmt, revAmt, refAmt, finalAmt

        # * Kept For Stand Alone Testing
        # print(f"RetId = {RetId} || InstId = {InstId} || purAmt = {purAmt}", end="")
        # print(f" || refrevAmt = {refrevAmt} || revAmt = {revAmt} || refAmt = {refAmt}  || finalAmt = {finalAmt}\n", end="")

    # except Exception as err1:
    #     print(f"Cursor Run Failed err1 : {err1}")
    #     print(f"Cursor Run Failed err1.args : {err1.args}")
    #     del err1

    return estadoList, chileList


def push_data_estado() -> None:
    """
    Summary:
        Fetch Data Of Estado Retailers To Estado_Report Table From Function [db_cursor()]
        Insert The Data In Batches [1000 Rows At A Time]
    """
    Estado_Report.truncate_table()
    query = """
    SELECT
        CONCAT(RetailerId, '#^#', EntityId) AS verifiedRetIdData
    FROM
        retailerid
    WHERE
        BankCode = '012'
        AND CONCAT(RetailerId, '#^#', EntityId) IN (
            SELECT
                DISTINCT (
                    CONCAT(
                        CardAcceptorIdentification,
                        '#^#',
                        AcquiringInstitutionIdentification
                    )
                ) AS 'CAI#^#AII'
            FROM
                fulldayacquirerextract
            WHERE
                ResponseCode = "00"
        );    
    """
    retIdForEstado = read_sql_query(f"{query}", con=sqlEngine).to_dict(orient='records')

    ## * Estado Atomic
    # print(f"Estodo Atomic = {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    with db_con.atomic():
        getEstadoList = db_cursor(retIdConcatDistinct=retIdForEstado, reportName="BancoEstado")[0]
        for batch in chunked(getEstadoList, 500):
            # print(f"estadoBatch = {batch[0]}")
            Estado_Report.insert_many(batch).execute()



def bancoEstadoHtmlProcessing() -> None:
    """
    Summary:
        Read HTML, Update IDP Values & Insert Into estado_report From estadoidpupdate 
    """

    estadoKeys = ['Ruth', 'IDP', 'FromSource', 'AcNum', 'Bank', 'OwnCode', 'PaymentAmt', 'NoOfDocuments', 'PaymentStatus', 'Reason']
    idpList = []

    for eachFile in glob(inputReportLoc):
        if "_rendicion_bancoestado_smartpos" in eachFile:
            print(f"Each HTML File = {eachFile}")
            htmlData, trCount = open(f"{eachFile}", "r").read(), 0
            soup = BeautifulSoup(htmlData, "html.parser")
            
            for eachRowValues in soup.find_all('tr'):
                trCount += 1

                if trCount == 5:  # * exaclty @5th row we fetch our data
                    fileDate = eachRowValues.find_all('td')[-1].text.strip()
                    finalPaymentDate = fileDate.split('/')[0]+'-'+fileDate.split('/')[1]+'-'+fileDate.split('/')[2]
                    # print(f"fileDate = {fileDate}\n")
                    # print(f"PaymentDate = {finalPaymentDate}\n")

                elif trCount > 7:  # * after 7th rows we fetch our data
                    estadoHtmlDict = {key: value.text.strip() for key, value in zip(estadoKeys, eachRowValues.find_all('td'))}

                    if "Rechazado" in estadoHtmlDict['PaymentStatus']:

                        # * [ Update IDP ]
                        hexVal = estadoHtmlDict['IDP'].split('NAN')[1]
                        updateIdpCnt = f"IDP{str(int(estadoHtmlDict['IDP'].split('NAN')[0].split('IDP')[1]) + 1).rjust(3, '0')}NAN{hexVal}"
                        oldIdp = estadoHtmlDict['IDP']
                        print(f"\nOld = {oldIdp}")
                        estadoHtmlDict['IDP'] = updateIdpCnt
                        idpList.append(updateIdpCnt)
                        estadoHtmlDict['DepositStatus'] = "Rechazado"
                        print(f"Rechazado = {estadoHtmlDict}")

                        # * [ Get Latest Retailer Data ]
                        getRetInsId = [k for k in Estado_Report.select(Estado_Report.RetId, Estado_Report.InsId).where(Estado_Report.IDP == oldIdp).dicts()][0]
                        print(f"YooMan Estado 1 = {getRetInsId}")
                        queryRetId = (
                            RetailerId
                            .select(RetailerId.IdentificationNumber.alias('Ruth'), RetailerId.IdentificationNumber.alias('Dv'),
                                    RetailerId.EmailAddress.alias('EmailId'), RetailerId.BankCode.alias('BankCode'), 
                                    RetailerId.MovmentType.alias('AcType'),RetailerId.AccountNumber.alias('AcNum'), 
                                    RetailerId.Name.alias('RetName'), RetailerId.StatusCode.alias('RetailerStatus'), 
                                    RetailerId.AcquirerRegionCode.alias('Region'), RetailerId.RetailerId.alias('RetId'),
                                    RetailerId.EntityId.alias('InsId'))
                            .where(RetailerId.RetailerId == getRetInsId['RetId'], RetailerId.EntityId == getRetInsId['InsId'])
                        ).dicts().iterator()
                        updatedData = [k for k in queryRetId][0]
                        print(f"YooMan Estado 2 = {updatedData}")
                        try:
                            if str(int(updatedData['AcType'])) == "3": updatedData['AcType'] = '01'
                            elif str(int(updatedData['AcType'])) == "4": updatedData['AcType'] = '02'
                        except Exception as err: pass

                        try:
                            updatedData['Dv'] = updatedData['Dv'].split('-')[1]
                        except Exception as err: pass
                        

                        new_func(estadoHtmlDict)
                        del estadoHtmlDict['FromSource'], estadoHtmlDict['PaymentStatus']
                        del estadoHtmlDict['OwnCode'], estadoHtmlDict['Reason'], estadoHtmlDict['AcNum']
                        del estadoHtmlDict['PaymentAmt'], estadoHtmlDict['NoOfDocuments'], estadoHtmlDict['Bank']
                        estadoHtmlDict.update(updatedData)
                        print(f"updatedData = {estadoHtmlDict}")

                        # * [ Check For ValeVista Trnxs ]
                        if int(estadoHtmlDict['IDP'].split('NAN')[0].replace('IDP', '')) == 111:
                            print(f"# ValeVista -> Estado = {estadoHtmlDict['IDP']}")
                            estadoHtmlDict['PaymentAmt'] = estadoHtmlDict['FinalAmt']
                            del estadoHtmlDict['BankCode'], estadoHtmlDict['AcType'], estadoHtmlDict['AcNum']
                            del estadoHtmlDict['FinalAmt'], estadoHtmlDict['RetailerStatus'], estadoHtmlDict['InsId']
                            del estadoHtmlDict['Dv'], estadoHtmlDict['Region'], estadoHtmlDict['RetId'], estadoHtmlDict['DepositStatus']
                            ValeVista.insert(**estadoHtmlDict).execute()
                            try:
                                FullDayTransactionHistory.update(IDP = estadoHtmlDict['IDP']).where(FullDayTransactionHistory.IDP == oldIdp.strip()).execute()
                            except Exception as vvEstErr:
                                print(f"Error: vvEstErr = {vvEstErr}")
                        
                        else:
                            try:
                                EstadoIdpUpdate.insert(**estadoHtmlDict).execute()
                                FullDayTransactionRetailerHistory.update(**estadoHtmlDict).where(FullDayTransactionRetailerHistory.IDP == oldIdp.strip()).execute()
                                FullDayTransactionHistory.update(IDP = estadoHtmlDict['IDP']).where(FullDayTransactionHistory.IDP == oldIdp.strip()).execute()                
                            except Exception as EIdpUpdate:
                                print(f"Error: EIdpUpdate = {EIdpUpdate}")

                    elif "Pagado" in estadoHtmlDict['PaymentStatus']:
                        print(f"\nPagado = {estadoHtmlDict}")
                        idpList.append(estadoHtmlDict['IDP'])
                        try:
                            (FullDayTransactionRetailerHistory
                            .update(DepositStatus='Pagado', PaymentDate=finalPaymentDate)
                            .where(FullDayTransactionRetailerHistory.IDP == estadoHtmlDict['IDP'].strip())).execute()
                        except Exception as err1:
                            print(f"Error = {err1}")

            try:
                move(eachFile, destLoc)
            except Exception as estadoMvError:
                print(f"{eachFile} | {destLoc}")
                print(f"Error: estadoMvError = {estadoMvError}")

    return idpList


def bancoEstadoReports() -> None:

    try:
        reportNameBE = "bancoestado"
        estadoData = read_sql_table(table_name="estado_report", con=sqlEngine, columns=['Ruth', 'RetName', 'IDP', 'EmailId', 'BankCode', 'AcType', 'AcNum', 'FinalAmt'])
        newFile = open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameBE}.txt", "w+", encoding="UTF-8")
        newFile.close()
        for eachRow in estadoData.iterrows():
            # print(f"{eachRow}\n")
            # print(f"Ruth = {eachRow[1].get('Ruth', 'NoDataFound')+'\t'}")
            # print(f"RetName (IDP) = {eachRow[1].get('IDP', 'NoDataFound')+'\t'}")
            # print(f"EmailId = {eachRow[1].get('EmailId', 'NoDataFound')+'\t'}")
            # print(f"BankCode = {eachRow[1].get('BankCode', 'NoDataFound')+'\t'}")
            # print(f"AcType = {eachRow[1].get('AcType', 'NoDataFound')+'\t'}")
            # print(f"AcNum = {eachRow[1].get('AcNum', 'NoDataFound')+'\t'}")
            # print(f"FinalAmt = {str(round(float(eachRow[1].get('FinalAmt', 'NoDataFound'))))}")
            with open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameBE}.txt", "a+", encoding="UTF-8") as estadoReport:
                estadoReport.write(
                    eachRow[1].get('Ruth', 'NoDataFound').replace('-', '')+'\t'
                    +eachRow[1].get('IDP', 'NoDataFound')+'\t'
                    +eachRow[1].get('EmailId', 'NoDataFound')+'\t'
                    +eachRow[1].get('BankCode', 'NoDataFound')+'\t'
                    +eachRow[1].get('AcType', 'NoDataFound').rjust(2,'0')+'\t'
                    +eachRow[1].get('AcNum', 'NoDataFound')+'\t'
                    +str(round(float(eachRow[1].get('FinalAmt', 'NoDataFound'))))
                    +'\r\n')
               

    except Exception as err1:
        print(f"Error In Generating Report Of BancoEstado - {err1}")


def new_func(estadoHtmlDict):
    estadoHtmlDict['FinalAmt'] = estadoHtmlDict['PaymentAmt']

def push_data_chile() -> None:
    """
    * Function Task :-
    1. Read TXT, Update IDP Values & Insert Into chile_report From chileidpupdate 
    2. Generate Retailer Based Banco Chile Reports
    """
    Chile_Report.truncate_table()
    query = """
    SELECT
        CONCAT(RetailerId, '#^#', EntityId) AS verifiedRetIdData
    FROM
        retailerid
    WHERE
        BankCode != '012'
        AND CONCAT(RetailerId, '#^#', EntityId) IN (
            SELECT
                DISTINCT (
                    CONCAT(
                        CardAcceptorIdentification,
                        '#^#',
                        AcquiringInstitutionIdentification
                    )
                ) AS 'CAI#^#AII'
            FROM
                fulldayacquirerextract
            WHERE
                ResponseCode = "00"
        );    
    """
    retIdForChile = read_sql_query(f"{query}", con=sqlEngine).to_dict(orient='records')

    ## * Chile Atomic
    # print(f"Chile Atomic = {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    with db_con.atomic():
        getChileList = db_cursor(retIdConcatDistinct=retIdForChile, reportName="BancoChile")[1]
        for batch in chunked(getChileList, 1000):
            # print(f"chileBatch = {batch[0]}")
            Chile_Report.insert_many(batch).execute()


def bancoChileExtractUpload() -> None:

    # * [ Upload Extract Data To Chile_Report ]
    push_data_chile()

    # * [ Add IDP values to each transactions ]
    for retIdp in [k for k in Chile_Report.select(Chile_Report.DocNum, Chile_Report.RetId).dicts().iterator()]:
        # print(f"retIdp = {retIdp}")
        (CurrentDateTransactionHistory
         .update(IDP=retIdp['DocNum'])
         .where(CurrentDateTransactionHistory.CardAcceptorIdentification == retIdp['RetId'])
         .execute())

    # * [ Merge Data From ChileIdpUpdate To Chile_Report ]
    (Chile_Report.insert_from(
        ChileIdpUpdate.select(
            ChileIdpUpdate.RetId, ChileIdpUpdate.InsId, ChileIdpUpdate.StartColumn, ChileIdpUpdate.Ruth, ChileIdpUpdate.Dv, ChileIdpUpdate.RetName, ChileIdpUpdate.DocType, ChileIdpUpdate.DocNum,
            ChileIdpUpdate.EmailId, ChileIdpUpdate.BankCode, ChileIdpUpdate.AcType, ChileIdpUpdate.AcNum, ChileIdpUpdate.FinalAmt, ChileIdpUpdate.Observation,
            ChileIdpUpdate.Warning, ChileIdpUpdate.EndColumn, ChileIdpUpdate.DepositStatus, ChileIdpUpdate.RetailerStatus, ChileIdpUpdate.PaymentDate,
            ChileIdpUpdate.DepositDate, ChileIdpUpdate.BrodcastDate, ChileIdpUpdate.Region),
        fields=[Chile_Report.RetId, Chile_Report.InsId, Chile_Report.StartColumn, Chile_Report.Ruth, Chile_Report.Dv, Chile_Report.RetName, Chile_Report.DocType, Chile_Report.DocNum,
                Chile_Report.EmailId, Chile_Report.BankCode, Chile_Report.AcType, Chile_Report.AcNum, Chile_Report.FinalAmt, Chile_Report.Observation,
                Chile_Report.Warning, Chile_Report.EndColumn, Chile_Report.DepositStatus, Chile_Report.RetailerStatus, Chile_Report.PaymentDate,
                Chile_Report.DepositDate, Chile_Report.BrodcastDate, Chile_Report.Region])
        .execute())

    # * [ delete duplicate retid + combine totalamt of duplicate retid + update ret data = insert this combined new record ] 
    combine_duplicate_chile()

    # * [ split amount > 5000000 into sub trnxs ]
    split_max_amount(5000000, "chile_report")


def bancoEstadoExtractUpload() -> None:

    # * [ Upload Extract Data To Estado_Report ]
    push_data_estado()

    # * [ Add IDP values to each transactions ]
    for retIdp in [k for k in Estado_Report.select(Estado_Report.IDP, Estado_Report.RetId).dicts().iterator()]:
        # print(f"retIdp = {retIdp}")
        (CurrentDateTransactionHistory
         .update(IDP=retIdp['IDP'])
         .where(CurrentDateTransactionHistory.CardAcceptorIdentification == retIdp['RetId'])
         .execute())

    # * [ Merge Data From EstadoIdpUpdate To Estado_Report ]
    (Estado_Report.insert_from(
        EstadoIdpUpdate.select(
            EstadoIdpUpdate.RetId, EstadoIdpUpdate.InsId, EstadoIdpUpdate.StartColumn, EstadoIdpUpdate.Ruth, EstadoIdpUpdate.Dv, EstadoIdpUpdate.RetName, EstadoIdpUpdate.IDP, EstadoIdpUpdate.EmailId, EstadoIdpUpdate.BankCode,
            EstadoIdpUpdate.AcType, EstadoIdpUpdate.AcNum, EstadoIdpUpdate.FinalAmt, EstadoIdpUpdate.Observation, EstadoIdpUpdate.Warning, EstadoIdpUpdate.EndColumn, EstadoIdpUpdate.DepositStatus, EstadoIdpUpdate.RetailerStatus, EstadoIdpUpdate.PaymentDate, EstadoIdpUpdate.DepositDate, EstadoIdpUpdate.BrodcastDate, EstadoIdpUpdate.Region),

        fields=[Estado_Report.RetId, Estado_Report.InsId, Estado_Report.StartColumn, Estado_Report.Ruth, Estado_Report.Dv, Estado_Report.RetName, Estado_Report.IDP, Estado_Report.EmailId, Estado_Report.BankCode,
                Estado_Report.AcType, Estado_Report.AcNum, Estado_Report.FinalAmt, Estado_Report.Observation, Estado_Report.Warning, Estado_Report.EndColumn, Estado_Report.DepositStatus, Estado_Report.RetailerStatus,
                Estado_Report.PaymentDate, Estado_Report.DepositDate, Estado_Report.BrodcastDate, Estado_Report.Region])
        .execute())

    # * [ delete duplicate retid + combine totalamt of duplicate retid + update ret data = insert this combined new record ] 
    combine_duplicate_estado()

    # * [ split amount > 5000000 into sub trnxs ]
    split_max_amount(0, "estado_report")


def bancoChileTxtProcessing() -> None:
    """
    Summary:
        Generate Retailer Based Banco Estado Reports
        Do Not Delete Comments, They Could Be Useful For Debugging 
    """

    idpList = []

    for eachFile in glob(inputReportLoc):
        if "_rendicion_bancochile_smartpos" in eachFile:
            print(f"Each TXT File = {eachFile}")
            count = True
            with open(f"{eachFile}", encoding="UTF-8", mode="r") as bancoChileFile:
                for eachLine in bancoChileFile.readlines():
                    paymentDate = datetime.strptime(eachLine[23:31], r'%Y%m%d')
                    finalPaymentDate = datetime.strftime(paymentDate, r'%d-%m-%Y')
                    print(f'\npaymentDate = {paymentDate}')
                    print(f'finalPaymentDate = {finalPaymentDate}\n')
                    
                    # * [ Skip Header Line ]
                    if count:
                        count = False
                        continue
                    else:

                        # * [ Fetch Rejected Trnxs ]
                        if eachLine[128:130] == "22" or eachLine[128:130] == "28":
                            # print(f"Not Consider - {eachLine[0:11]} || {len(eachLine[0:11])}")
                            """ print(f"Compraqui RUTH - {eachLine[11:20]} || {len(eachLine[11:20])}") """
                            """ print(f"Ret RUTH - {eachLine[56:65]} || {len(eachLine[56:65])}") """
                            # print(f"ConventionCode - {eachLine[20:23]} || {len(eachLine[20:23])}")
                            # print(f"PaymentDate - {eachLine[23:31]} || {len(eachLine[23:31])}")
                            # print(f"PayrollFileName - {eachLine[32:45]} || {len(eachLine[32:45])}")
                            # print(f"RUTH DF - {eachLine[56:66]} || {len(eachLine[57:66])}")
                            # print(f"Not Consider - {eachLine[66:68]} || {len(eachLine[66:68])}")
                            """ print(f"IDP - {eachLine[68:88]} || {len(eachLine[69:88])}") """
                            """ print(f"TransferStatusCode - {eachLine[128:130]} || {len(eachLine[128:130])}") """
                            """ print(f"Amt Paid - {eachLine[130:144]} || {len(eachLine[130:144])}") """
                            # print(f"DoubleZero - {eachLine[144:146]} || {len(eachLine[144:146])}")
                            # print(f"PaymentDate - {eachLine[146:154]} || {len(eachLine[146:154])}")
                            # print(f"DepositBank - {eachLine[171:174]} || {len(eachLine[171:174])}")
                            # print(f"AccNo - {eachLine[174:196]} || {len(eachLine[174:196])}")
                            """ print(f"Email = NAN") """
                            """ print(f"Fixed Val = {'012'}") """
                            """ print(f"Fixed Val = {'23'}") """
                            """ print(f"Fixed Val = {'00000000000000000'}") """
                            chileRejDict = {colName:value for colName,value in zip(['Ruth', 'PaymentAmt', 'IDP'],[eachLine[11:20], str(int(eachLine[130:144])), eachLine[68:88]])}
                            # print(f"Chile Rechazado = {chileRejDict}")

                            # * [ Update IDP ]
                            hexVal = chileRejDict['IDP'].split('NAN')[1]
                            IdpCnt = str(int(chileRejDict['IDP'].split('NAN')[0].split('IDP')[1]) + 1).rjust(3, '0')
                            oldIdp = chileRejDict['IDP']
                            updateIdp = f"IDP{IdpCnt}NAN{hexVal}"
                            chileRejDict['DocType'] = "991"
                            print(f"\nOld = {oldIdp} | New = {updateIdp}")
                            chileRejDict['DepositStatus'] = "Rechazado"
                            chileRejDict['IDP'] = updateIdp
                            idpList.append(updateIdp)

                            # * [ Get Latest Retailer Data ]
                            getRetInsId = [k for k in Chile_Report.select(Chile_Report.RetId, Chile_Report.InsId).where(Chile_Report.DocNum == oldIdp).dicts()][0]
                            queryRetId = (
                                RetailerId
                                .select(RetailerId.IdentificationNumber.alias('Ruth'), RetailerId.IdentificationNumber.alias('Dv'),
                                        RetailerId.EmailAddress.alias('EmailId'), RetailerId.BankCode.alias('BankCode'), 
                                        RetailerId.MovmentType.alias('AcType'),RetailerId.AccountNumber.alias('AcNum'), 
                                        RetailerId.Name.alias('RetName'), RetailerId.StatusCode.alias('RetailerStatus'), 
                                        RetailerId.AcquirerRegionCode.alias('Region'), RetailerId.RetailerId.alias('RetId'),
                                        RetailerId.EntityId.alias('InsId'))
                                .where(RetailerId.RetailerId == getRetInsId['RetId'], RetailerId.EntityId == getRetInsId['InsId'])
                            ).dicts().iterator()
                            updatedData = [k for k in queryRetId][0]
                            print(f"YooMan Chile = {updatedData}")
                            if '-' in updatedData['Ruth']: updatedData['Dv'] = updatedData['Dv'].split('-')[1]
                            else: updatedData['Dv'] = ''

                            if get_acnum_chile(updatedData['BankCode'], updatedData['AcType']) != None:
                                updatedData['AcType'] = get_acnum_chile(updatedData['BankCode'], str(int(updatedData['AcType'])))
                            if (updatedData['AcType'] != "") or (updatedData['AcType'] != " "):
                                updatedData['AcType'] = updatedData['AcType'].rjust(2, "0")
                            try: updatedData['Dv'] = updatedData['Dv'].split('-')[1]
                            except Exception as err: pass
                            chileRejDict.update(updatedData)
                            chileRejDict['FinalAmt'] = chileRejDict['PaymentAmt']
                            del chileRejDict['PaymentAmt']
                            print(f"Chile Rechazado = {chileRejDict}")

                            if int(chileRejDict['IDP'].split('NAN')[0].replace('IDP', '')) == 111:
                                print(f"# ValeVista -> Chile = {chileRejDict['IDP']}")
                                try:
                                    FullDayTransactionHistory.update(IDP = updateIdp).where(FullDayTransactionHistory.IDP == oldIdp.strip()).execute()
                                    chileRejDict['PaymentAmt'] = chileRejDict['FinalAmt']
                                    del chileRejDict['RetId'], chileRejDict['InsId'], chileRejDict['FinalAmt']
                                    del chileRejDict['Dv'], chileRejDict['BankCode'], chileRejDict['AcType']
                                    del chileRejDict['AcNum'], chileRejDict['RetailerStatus'], chileRejDict['Region']
                                    ValeVista.insert(**chileRejDict).execute()
                                except Exception as vvEstErr:
                                    print(f"Error: vvEstErr = {vvEstErr}")
                            
                            else:
                                try:
                                    chileRejDict['DocNum'] = chileRejDict['IDP']
                                    del chileRejDict['IDP']
                                    ChileIdpUpdate.insert(**chileRejDict).execute()
                                    chileRejDict['IDP'] = chileRejDict['DocNum']
                                    del chileRejDict['DocNum']
                                    FullDayTransactionHistory.update(IDP = updateIdp).where(FullDayTransactionHistory.IDP == oldIdp.strip()).execute()
                                    FullDayTransactionRetailerHistory.update(**chileRejDict).where(FullDayTransactionRetailerHistory.IDP == oldIdp.strip()).execute()
                                except Exception as CIdpUpdate:
                                    print(f"Error: CIdpUpdate = {CIdpUpdate}")

                        # * [ Fetch Success Trnxs ]
                        else:
                            chileSuccDict = {colName:value for colName,value in zip(['Ruth', 'PaymentAmt', 'IDP'],[eachLine[11:20], str(int(eachLine[130:144])), eachLine[68:88]])}
                            print(f"\nChile Pagado = {chileSuccDict}")
                            idpList.append(chileSuccDict['IDP'])
                            try:
                                (FullDayTransactionRetailerHistory
                                .update(DepositStatus='Pagado', PaymentDate=finalPaymentDate)
                                .where(FullDayTransactionRetailerHistory.IDP == chileSuccDict['IDP'].strip())).execute()
                            except Exception as err1:
                                print(f"Error = {err1}")

            try:
                move(eachFile, destLoc)
            except Exception as chileMvError:
                print(f"{eachFile} | {destLoc}")
                print(f"Error: chileMvError = {chileMvError}")

    return idpList


def bancoChileReports() -> None:
    """
    * Function Task :-
    1. Generate Retailer Based Banco Chile Reports
    2. Do Not Delete Comments, They Could Be Useful For Debugging 
    """

    try:
        reportNameBC = "bancochile"
        chileData = read_sql_table(table_name="chile_report", con=sqlEngine, columns=['StartColumn', 'Ruth', 'Dv', 'RetName', 'DocType', 'DocNum', 'BrodcastDate', 'FinalAmt', 'Observation', 'AcType', 'BankCode', 'AcNum', 'EmailId', 'Warning', 'EndColumn'])
        newFile = open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameBC}.txt", "w+", encoding="UTF-8")
        newFile.close()
        for eachRow in chileData.iterrows():
            # print(f"{eachRow}\n")
            with open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameBC}.txt", "a+", encoding="UTF-8") as chileReport:
                chileReport.write(
                    eachRow[1].get('StartColumn', 'NoDataFound')+';'+eachRow[1].get('Ruth', 'NoDataFound').split('-')[0]+';'
                    +eachRow[1].get('Dv', 'NoDataFound')+';'+eachRow[1].get('DocNum', 'NoDataFound')+';'
                    +eachRow[1].get('DocType', '991')+';'+eachRow[1].get('DocNum', 'NoDataFound').replace("IDP", "")+';'
                    +eachRow[1].get('BrodcastDate', 'NoDataFound').replace('-', '')+';'
                    +str(round(float(eachRow[1].get('FinalAmt', 'NoDataFound'))))+';'
                    +eachRow[1].get('Observation', 'NoDataFound')+';'
                    +eachRow[1].get('AcType', 'NoDataFound').rjust(2,'0')+';'
                    +eachRow[1].get('BankCode', 'NoDataFound')+';'
                    +eachRow[1].get('AcNum', 'NoDataFound')+';'
                    +eachRow[1].get('Warning', 'NoDataFound')+';'
                    +eachRow[1].get('EmailId', 'NoDataFound')+';'
                    +eachRow[1].get('EndColumn', 'NoDataFound')
                    +'\r\n')
             

    except Exception as err1:
        print(f"Error In Generating Report Of BancoChille - {err1}")



def CC30ReportGeneration(date: str = datetime.now().strftime(r"%Y%m%d"), idpList: list = None, r1r2: bool = False) -> None:
    """
    Summary:
        1. Make Payment/Deposit Details Report
        2. Make Transactions Details Report

    Args:
        date (str, optional): Give the date when file is received. Today.
        idpList (list, optional): IDP list to fetch data. Defaults to None.
        r1r2 (bool. optional): Prepare report after CCX24/CCX30 run.Defaluts to False.
    """
    finalDf1, finalDf2 = False, False
    
    for idp in idpList:
        # print(f"{idp} | {date}")
        if r1r2:
            r1 = f'{reportLocation}{date}_GPSMARTPOS_DepositDetailsR1.csv'
            r2 = f'{reportLocation}{date}_GPSMARTPOS_TransactionsDetailsR2.csv'
        else:
            r1 = f'{reportLocation}{date}_GPSMARTPOS_DepositDetails.csv'
            r2 = f'{reportLocation}{date}_GPSMARTPOS_TransactionsDetails.csv'

        retID = [k for k in FullDayTransactionRetailerHistory.select(FullDayTransactionRetailerHistory.RetId, FullDayTransactionRetailerHistory.InsId).where(FullDayTransactionRetailerHistory.IDP==idp).dicts().iterator()][0]

        connection = sqlEngine.raw_connection()
        cursor = connection.cursor()
        storeProc = cursor.callproc('GetFinalAmtFromIdp', (idp, 0, 0, 0))
        # print(f"AmtBc = {storeProc[1]} | AmtCom = {storeProc[3]} | AmtAc = {storeProc[2]}")
        cursor.close()
        connection.commit()
        connection.close()

        # * paymentDetailsReport / depositDetailsReport
        queryPDR = f"""
        SELECT

            table1.IDP AS "IDP", -- * "IDP00058" | String max 20 | IDP
            RetID AS "ID", -- * "1491505" | String max 17 | Retailer ID
            Ruth AS "RUT", -- * "54773897" | String max 9 | TAX-ID before - and checkdigit
            RetName AS "Nombre del comercio", -- * "Kiosko Santa Bernardita" | String max 50 | Retailer Name
            BrodcastDate AS "Fecha de disponibilidad original", -- * "25-02-2022" | String max 10 | It is the first committed date for the payment
            BrodcastDate AS "Fecha a depositar", -- * "25-02-2022" | String max 10 | Date to deposit
            CntIdp AS "Cantidad de Ventas", -- * "1200" | String max 5 yes | total number of transactions for this IDP
            FLOOR(TrnxAmtBeforeCommissions) AS "Monto Bruto", -- * "58900" | String max 13 | Final Amount before Commission 
            FLOOR(TotalComm) AS "Comision total", -- * "1809" | String max 13 | Sum of commissions
            FLOOR(TrnxAmtAfterCommissions) AS "Monto Neto a Pagar", -- * "57088" | String max 13 | Final Amount after commission
            BankNameOnBankCode(BankCode) AS "Banco", -- * "Banco del Estado de Chile" | String max 60 | Bank Name
            AcType AS "Tipo de cuenta", -- * "07" | String max 16 | Account type
            AcNum AS "N de cuenta", -- * "5477389" | String max 12 | account number
            DepositStatus AS "Estado del deposito", -- * "Pagado" | String max 10 | Deposit Status
            PaymentDate AS "Fecha del deposito", -- * "25-02-2022" | String max 10 | Local payment date reported by the bank (same Detail payment date)
            '' AS "Respuesta Transferencia", -- * "" | String max 25 | Observation only if necessary
            EmailId AS "Email abono" -- * "XXXXXXX@XXXXXXX.XXX" | String max 25 | Email of payment account

        FROM
            (
                SELECT
                    IDP,
                    COUNT(IDP) AS CntIdp,
                    {storeProc[1]} AS TrnxAmtBeforeCommissions,
                    {storeProc[3]} AS TotalComm,
                    {storeProc[2]} AS TrnxAmtAfterCommissions
                FROM fulldaytransactionhistory
                WHERE IDP = "{idp}"
            ) AS table1

            INNER JOIN 
            
            (
                SELECT
                    IDP,
                    RetID,
                    Ruth,
                    RetName,
                    BrodcastDate,
                    PaymentDate,
                    BankCode,
                    AcType,
                    AcNum,
                    DepositStatus,
                    EmailId
                FROM fulldaytransactionretailerhistory
                WHERE IDP = "{idp}"
            ) AS table2 
            
            ON table1.IDP = table2.IDP;
        """
        queryDf1 = read_sql_query(f"{queryPDR}", con=sqlEngine)
        if not queryDf1.empty:
            if finalDf1:
                queryDf1.to_csv(r1, sep=';', index=False, encoding='UTF-8', mode='a', header=False)
                # print(f'queryDf1 = {r1}')
            else:
                system(f'rm {r1}')
                finalDf1 = True
                queryDf1.to_csv(r1, sep=';', index=False, encoding='UTF-8', mode ='w')
            # print(queryDf1)


        # * transactionDetailsReport
        queryTDR = f"""
        SELECT
            FTH.IDP AS IDP,
            FTRH.Ruth AS RUT,
            -- FTH.MessageType AS MT,
            -- FTH.ResponseCode AS RC,
            -- FTH.ProcessingCode AS PC,
            TransactionType(FTH.MessageType, FTH.ProcessingCode) AS Tipo,
            CONCAT(DATE_FORMAT(FTH.LocalTransactionDate,'%d-%m-%Y'),' ',FTH.LocalTransactionTime) AS Fecha, 
            FTRH.RetId AS 'Codigo de comercio',
            FTRH.RetName AS Comercio,
            CASE
                WHEN RetTable.StatusCode = 1 THEN 'Enabled'
                WHEN RetTable.StatusCode = 2 THEN 'Disabled'
                WHEN RetTable.StatusCode = 4 THEN 'Temporary Block'
                ELSE 'Blocked'
            END AS Activo,
            '' AS Sucursal,
            FTRH.Region AS Region,
            FTH.RetrievalReferenceNumber AS TransactionID,
            FLOOR(FTH.TransactionAmount) AS 'Monto bruto',
            '' AS 'Monto bruto sin reversas',
            FLOOR(FTH.TotalCommissions) AS Arancel,
            FLOOR(FTH.Retefuente) AS 'IVA Arancel',
            REPLACE(FTH.TotalCommissions*100/TransactionAmount,'.', ',') AS 'Porcentaje Arancel',
            FLOOR(FTH.FinalAmount) AS 'Monto neto',
            '' AS 'Monto neto sin reversas',
            FTRH.BrodcastDate AS 'Fecha de disponibilidad original',
            FTRH.PaymentDate AS 'Fecha de pago',
            FTRH.DepositStatus AS 'Estado deposito',
            FTRH.IDP AS 'ID Deposito',
            CASE
                WHEN FTH.ProcessingCode = 200000 THEN LocalTransactionDate
                ELSE ''
            END AS 'Fecha de anulacion',
            '' AS 'Usuario de la aplicacion',
            CASE
                WHEN FTH.ResponseCode = '00' THEN 'ACCEPTED'
                ELSE 'REJECTED'
            END AS Estado,
            '' AS 'E-mail del cliente',
            '' AS 'Nombre del cliente',
            '' AS RUN,
            BrandName(FTH.ForwardingInstitutionIdentification) AS 'Marca de tarjeta',
            RIGHT(FTH.Track2Data, 4) AS 'Numero tarjeta',
            CASE
                WHEN FTH.CardType = 'D' THEN 'Debito'
                WHEN FTH.CardType = 'C' THEN 'Credito'
                ELSE ''
            END AS 'Tipo tarjeta',
            CASE
                WHEN FTH.NoOfInstallment = NULL THEN ''
                ELSE FTH.NoOfInstallment
            END AS 'Cantidad de cuotas',
            FTRH.BankCode AS 'Cod banco emisor',
            BankNameOnBankCode(FTRH.BankCode) AS 'Nombre banco emisor',
            FTH.AuthorizationIdentificationResponse AS 'N Autorizacion',
            ResponseCodeDescription(FTH.ResponseCode) AS 'Mensaje de respuesta',
            FTH.CardAcceptorTerminalIdentification AS Lector,
            FTH.PointofServiceEntryModeCode AS 'Tipo de Venta',
            '-33.42248,-70.62169' AS Geolocalizacion

        FROM
            fulldaytransactionhistory AS FTH, 
            (SELECT * FROM retailerid WHERE RetailerId = '{retID["RetId"]}' AND EntityId = '{retID["InsId"]}' LIMIT 1) AS RetTable, 
            (SELECT * FROM fulldaytransactionretailerhistory) AS FTRH
        WHERE
            FTH.IDP = "{idp}" AND
            FTRH.IDP = "{idp}";
        """
        queryDf2 = read_sql_query(f"{queryTDR}", con=sqlEngine)
        if not queryDf2.empty:
            if finalDf2:
                queryDf2.to_csv(r2, sep=';', index=False, encoding='UTF-8', mode='a', header=False)
                # print(f'queryDf2 = {r2}')
            else:
                system(f'rm {r2}')
                finalDf2 = True
                queryDf2.to_csv(r2, sep=';', index=False, encoding='UTF-8', mode ='w')
            # print(queryDf2)


def vale_vista() -> None:    
    """ Make Vale Vista Reports """
    reportNameVV = "valevista"
    newFile = open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameVV}.txt", "w+", encoding="UTF-8")
    newFile.close()
    valevistaData = read_sql_table(table_name="valevista", con=sqlEngine)    
    for eachRowVV in valevistaData.iterrows():
        # print(f"eachRow = {eachRowVV}\n")
        with open(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_{reportNameVV}.txt", "a+", encoding="UTF-8") as estadoReport:
            estadoReport.write(
                eachRowVV[1].get('Ruth', 'NoDataFound')+"\t"
                + eachRowVV[1].get('RetName', 'NoDataFound')+"\t"
                + eachRowVV[1].get('EmailId', 'NoDataFound')+"\t"
                + "012"+"\t" + "23"+"\t" + "00000000000000000"+"\t"
                + str(round(eachRowVV[1].get('PaymentAmt', 'NoDataFound')))
                +'\r\n')
    ValeVista.truncate_table()



def copyToFullDayTransactionhistory():
    try:
        cdthData = read_sql_query("""SELECT * FROM currentdatetransactionhistory;""", con=sqlEngine)
        for k1 in cdthData.to_dict(orient='records'):
            del k1['id'], k1['TimeStamp']
            FullDayTransactionHistory.insert(**k1).execute()
    except Exception as err3:
        print(f"Error in inserting from CurrentDate to TransactionHistory = {err3}")


if '__main__' == __name__:

    # print(f"reportLocation = {reportLocation}")
    # print(f"currentLocation ={path.dirname(path.realpath(__file__))}")
    # system(f"rm {reportLocation}*.txt") # * Only Use On Dev Env
    # print(f"START = {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    
    if argv[1] == 'CCX30':
        print('#'*45)
        print(f'\tRunning Process = {argv[1]}')
        print('#'*45, '\n\n')
        """
        # * CC030 [HTM & TXT Received - Update IDP(Rejected)/status/paymentDate]
        # * Take old rejected IDP in memory for Rejected Trnx to pull data for reports
        # * Update Stauts / PaymentDate / IDP (Rejected) in detail trnxs
        """
        EstadoIdpUpdate.truncate_table()
        ChileIdpUpdate.truncate_table()
        idpList1 = bancoEstadoHtmlProcessing()
        idpList2 = bancoChileTxtProcessing()
        print(f'\nUnique IDP = {set(idpList1+idpList2)}\n')
        # TODO CCX30 reports file rename as per brodcastedate / filedate
        CC30ReportGeneration(idpList=set(idpList1+idpList2))
        # * Commented By Dishant [13Oct2022] :- Kept For Re-Run During Error
        # LogIdp = {}
        # CC30ReportGeneration(idpList=set(LogIdp))
        system(f"mv {reportLocation}*R1.csv* {reportLocation}BK/ > /dev/null 2>&1; mv {reportLocation}*R2.csv* {reportLocation}BK/ > /dev/null 2>&1")


    elif argv[1] == 'CCX24':
        print('#'*45)
        print(f'\tRunning Process = {argv[1]}')
        print('#'*45, '\n\n')
        """
        # * CC024 [Extract Will Be Received Next Day]
        # * Append fresh IDP value to detail trnxs as well
        """

        if fullDayAcquirerExtractLoad(pick_date="all"):
            updateRetailerDataForIdpUpdateTables()
            db_con.execute_sql("CALL CCX24_UpdateMoveDataIdpTable;")
            fullDayLiquidation()
            bancoChileExtractUpload()
            bancoEstadoExtractUpload()
            bancoChileReports()
            bancoEstadoReports()
            vale_vista()
            copyToFullDayTransactionRetailerHistory()
            copyToFullDayTransactionhistory()
            # * CCX24 Update Retailer Data For [ fulldaytransactionretailerhistory ] Rechazado IDP
            system(f"mysql -u compsan -pcompsan* {dbName} < ./SqlFiles/CCX24_updateRetData.sql")
            idpList = read_sql_query(f"SELECT IDP FROM estado_report UNION SELECT DocNum AS IDP FROM chile_report;", con=sqlEngine).to_dict(orient='records')
            CC30ReportGeneration(idpList=set([k['IDP'] for k in idpList]), r1r2=True)
            print(f"CCX24 Report Generation Success At {today}")
            # TODO EstadoIdpUpdate.truncate_table()
            # TODO ChileIdpUpdate.truncate_table()
        else:
            print(f"CCX24 Report Generation Failed At {today}")

    elif argv[1] == 'ZIPFTP':
        zip_backup_loc = f"/comp_repo/{datetime.now().strftime(r'%b_%Y')}/{datetime.now().strftime(r'%d-%b-%y')}/"
        zip_Columbiabk_loc = f"/home/compsan_bk/comp_repo/{datetime.now().strftime(r'%b_%Y')}/{datetime.now().strftime(r'%d-%b-%y')}/"
        for singleReportFile in glob(f"{reportLocation}*{datetime.now().strftime(r'%Y%m%d')}**.txt*"):
            if "_DetailedTrnxReport.txt" in singleReportFile:
                continue
            # print(f"singleReportFile = {singleReportFile} ")
            zip_directory_loc = singleReportFile.replace(f"{singleReportFile.split('/')[-1]}", "")
            origin_file_name = singleReportFile.split("/")[-1]
            dest_file_name = singleReportFile.split("/")[-1]
            # print("Origin = ", zip_directory_loc, " | " ,origin_file_name)
            # print("Destination = ", zip_backup_loc, " | " ,dest_file_name)
            # file_transfer(zip_directory_loc, origin_file_name, zip_backup_loc, dest_file_name, host="192.168.3.83", username="comp_prod_ftp", password="comp_prod_ftp$2021", port=22)
            # file_transfer(zip_directory_loc, origin_file_name, zip_Columbiabk_loc, dest_file_name, host="192.168.6.10", username="compsan_bk", password="compsanbk#15Feb2023", port=45450)


        chdir(f"{reportLocation}")
        system(f"zip {datetime.now().strftime(r'%Y%m%d')}_DepositRetailerReports.zip *{datetime.now().strftime(r'%Y%m%d')}**.txt* -x *_DetailedTrnxReport.txt*")
        chdir(f"{path.split(path.abspath(__file__))[0].split('CompensationReports')[0]}")
        system(f"ls -lthr {reportLocation}*{datetime.now().strftime(r'%Y%m%d')}* | tail -6")
        system(f"tree /home/comp_prod_ftp/comp_repo/{datetime.now().strftime(r'%b_%Y')}/{datetime.now().strftime(r'%d-%b-%y')}/")


    elif argv[1] == 'trnxDetailReport':
        # querytdr = f"SELECT * FROM fulldaytransactionhistory WHERE TimeStamp LIKE '{datetime.now().strftime(r'%Y-%m-%d')}%';"
        querytdr = f"select * from fulldaytransactionhistory WHERE IDP IN (select IDP from estado_report UNION select DocNum AS IDP from chile_report);"
        data = read_sql_query(f'{querytdr}', con=sqlEngine)
        data.drop(['id'], inplace=True, axis=1)
        data.to_csv(f"{reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_DetailedTrnxReport.txt", index=False, encoding='UTF-8')
        print(f"trnxDetailReport Loc = {reportLocation}{datetime.now().strftime(r'%Y%m%d')}_GPSMARTPOS_DetailedTrnxReport.txt")
        # print(data)
