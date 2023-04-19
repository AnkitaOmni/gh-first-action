import queries
import pandas as pd
from glob import glob
from datetime import datetime
from database import DatabaseConnections


db = DatabaseConnections()
engine = db.sqlalchemy_connection()


year, month, day = str(datetime.today().date()).split('-')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
              

# * comment by matesh [21 dec 2022] : usign pandas to read files
def extract_input_file(fileName, originalTable):
    dataFrame = pd.read_csv(fileName,  index_col=False, engine='python', encoding='latin-1', dtype=str)

    if 'TxnLoggingTime(P031)' in dataFrame.columns.to_list():
        dataFrame.rename(columns = {'TxnLoggingTime(P031)':'TxnLoggingTime'}, inplace = True)

    # * Added By Dishant [09 Nov 2022] :- Skip the new added columns in extract and set defalult values to empty columns
    # dataFrame['Track1Data'].fillna('0', inplace=True)
    # dataFrame['Track1Data'].replace(to_replace=r'\s*', value='0', inplace=True, regex=True)

    if 'Credit_Voucher' in fileName:
        columnNaList = dataFrame.loc[:, dataFrame.isnull().all()].columns.tolist()
        if 'NetworkInternationalIdentifierCode' in columnNaList:
            columnNaList.remove('NetworkInternationalIdentifierCode')
        dataFrame[columnNaList] = dataFrame[columnNaList].fillna(0)
        dataFrame.fillna('',inplace=True)

    dataFrame.to_sql(name=originalTable, con=engine, if_exists='append', index=False)
    # print(f"File Upload Done = {fileName}") # * Kept For Testing



def remove_duplicate(originalTable, duplicate_table):

    FNAME = f'DuplicatesReport_{originalTable}_{year}{month}{day}.csv'
    REPORTS_PATH = f'CompensationReports/ConciliationReports/{months[int(month)-1]}_{year}/'


    primary_key = ['RetrievalReferenceNumber', 'TransmissionDateandTime', 'Track2Data',
                   'MessageType', 'ProcessingCode', 'ResponseCode', 'CardAcceptorIdentification']
    # add additional key member to duplicates @gdar

    dataFrame = pd.read_sql_table(originalTable,  con=engine).astype('str')
    dataFrame = dataFrame.sort_values(['LocalTransactionDate', 'LocalTransactionTime'], ascending=[True, True])
    # print(len(dataFrame))

    unique = dataFrame.drop_duplicates(subset=primary_key, keep='last').copy()
    # print(len(unique))
    if not unique.empty:
        # set TimeStamp column with current time # unique['TimeStamp'] = datetime.now()
        unique[unique.columns[1]] = datetime.now()
        unique.loc[(unique['MessageType'] == '0110'), 'MessageType'] = '0210'
        unique.loc[(unique['MessageType'] == '0400'), 'MessageType'] = '0420'

    for i in unique.index:
        if len(unique.at[i, "LocalTransactionDate"]) <= 4:
            dateTimeStr = datetime.now().strftime("%Y") + unique.at[i, "LocalTransactionDate"]
            dataFrame.at[i, "LocalTransactionDate"] = datetime.strptime(dateTimeStr, '%Y%m%d').date()
        else:
            # print("not changed")
            pass

    duplicate = dataFrame.loc[dataFrame.duplicated(subset=primary_key)].copy()
    
    # print(len(duplicate))
    if not duplicate.empty:
        # set TimeStamp column with current time # duplicate['TimeStamp'] = datetime.now()
        duplicate[duplicate.columns[1]] = datetime.now()
        duplicate.loc[(duplicate['MessageType'] == '0110'), 'MessageType'] = '0210'
        duplicate.loc[(duplicate['MessageType'] == '0400'), 'MessageType'] = '0420'

    for i in unique.index:
        if len(unique.at[i, "LocalTransactionDate"]) <= 4:
            dateTimeStr = datetime.now().strftime("%Y") + unique.at[i, "LocalTransactionDate"]
            unique.at[i, "LocalTransactionDate"] = datetime.strptime(dateTimeStr, '%Y%m%d').date()
        else:
            # print("not changed")
            pass

    duplicate.to_sql(name=duplicate_table, con=engine, if_exists='append', index=False)
    #export duplicates to a csv file @gdar
    
    if not duplicate.empty:
        duplicate.drop(columns = duplicate.columns[0], axis = 1, inplace= True)
        duplicate.to_csv(REPORTS_PATH+FNAME,index=False)
    engine.execute(f"truncate table {originalTable};")
    unique.to_sql(name=originalTable, con=engine, if_exists='append', index=False)


if __name__ == '__main__':

    pass
    # print(glob(r"./AcquirerExtract/InputExtracts/*"))
    # print(glob(r"./AcquirerExtractFullDay/InputExtracts/*"))
    # queries.clean_acquirer_extract_tables()
    # queries.clean_issuer_extract_tables()
    # queries.fullday_clean_acquirer_extract_tables()
    # for i in glob(r"./AcquirerExtract/InputExtracts/*"):
    #     extract_input_file(i, 'acquireroriginal')
    #     break
    # remove_duplicate('acquirerextract', 'acquirerduplicates')
