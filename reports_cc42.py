import os
from model import *
import pandas as pd
from peewee import fn
from datetime import datetime
from database import DatabaseConnections

db = DatabaseConnections()
engine = db.sqlalchemy_connection()

year, month, day = str(datetime.today().date()).split('-')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class Reports:

    def __init__(self, institution, retailer, path):
        self.institution = institution
        self.retailer = retailer
        self.today = datetime.now().strftime("%y%m%d")  # today's date format YYMMDD
        self.path = path  # './CompensationReports/RetailerReports/'

    def csvReport(self, table_name, report_name):
        try:
            cols = table_name._meta.sorted_field_names
            data = table_name.select().dicts()
            data_frame = pd.DataFrame(data, columns=cols)
            file_name = "{}_{}.csv".format(report_name, self.today)
            data_frame.to_csv(self.path + file_name, index=False)
            print("{} Generated at {} ".format(report_name ,datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except table_name.DoesNotExist:print('Error In Generating Report Of {}'.format(report_name))
        except Exception as e:print('Error In Generating Report Of {} - {}'.format(report_name, str(e)))



    def all_transactions_report(self):
        query = '''SELECT distinct(newiseretailer.CardAcceptorIdentification) FROM newiseretailer INNER JOIN retailercompansation
                ON retailercompansation.RetailerId = newiseretailer.CardAcceptorIdentification And retailercompansation.Channel = newiseretailer.ChannelType and retailercompansation.EntityId = newiseretailer.AcquiringInstitutionIdentification where (newiseretailer.ResponseCode = '00') and (retailercompansation.PendingDays = '0');'''
        cursor = myDB.execute_sql(query)

        data=[k for k in cursor]
        result = [k for k in data]
        retailer_list = [item for sublist in result for item in sublist]
        try:
            query = NewISERetailer.select(
                                        NewISERetailer.AcquiringInstitutionIdentification,NewISERetailer.CardAcceptorIdentification,
                                        NewISERetailer.CardAcceptorTerminalIdentification,NewISERetailer.MerchantTypeCode,NewISERetailer.MessageType,
                                        NewISERetailer.ResponseCode,NewISERetailer.ProcessingCode,NewISERetailer.LocalTransactionTime,
                                        NewISERetailer.LocalTransactionDate,NewISERetailer.SettlementDate,NewISERetailer.Track2Data,
                                        NewISERetailer.SystemsTraceAuditNumber,NewISERetailer.RetrievalReferenceNumber,NewISERetailer.CardAcceptorNameLocation,
                                        NewISERetailer.ChannelType,NewISERetailer.CardType,NewISERetailer.TransactionAmount,NewISERetailer.RetCardTypeCommision,
                                        NewISERetailer.RetMccCommision,NewISERetailer.RetBinCommision,NewISERetailer.RetTxnIdentifierCommision,
                                        NewISERetailer.Retailer,NewISERetailer.Acquirer,NewISERetailer.Issuer,NewISERetailer.TotalCommissions,
                                        NewISERetailer.Retefuente,NewISERetailer.Reteica,NewISERetailer.Cree,NewISERetailer.Reteiva,NewISERetailer.TotalTaxes,
                                        NewISERetailer.TotalDiscounts,NewISERetailer.FinalAmount
                                       ).where((NewISERetailer.ResponseCode == '00') & NewISERetailer.CardAcceptorIdentification.in_(tuple(retailer_list))).dicts()

            data_frame = pd.DataFrame(query, columns=['AcquiringInstitutionIdentification', 'CardAcceptorIdentification', 'CardAcceptorTerminalIdentification',
                                                      'MerchantTypeCode', 'MessageType', 'ResponseCode', 'ProcessingCode', 'LocalTransactionTime',
                                                      'LocalTransactionDate', 'SettlementDate', 'Track2Data', 'SystemsTraceAuditNumber', 'RetrievalReferenceNumber',
                                                      'CardAcceptorNameLocation', 'ChannelType', 'CardType', 'TransactionAmount', 'RetCardTypeCommision',
                                                      'RetMccCommision', 'RetBinCommision', 'RetTxnIdentifierCommision', 'Retailer', 'Acquirer', 'Issuer',
                                                      'TotalCommissions', 'Retefuente', 'Reteica', 'Cree', 'Reteiva', 'TotalTaxes', 'TotalDiscounts', 'FinalAmount'])

            for x, y in data_frame.groupby('AcquiringInstitutionIdentification'):
                for k, v in y.groupby('ChannelType'):
                    file_name = "{}_{}_TGR_Retailer_{}.csv".format(x, k, self.today)
                    v.to_csv(self.path + file_name, index=False)

            print("All Transactions Report With Liquidation Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except NewISERetailer.DoesNotExist:print('Error In Generating Report Of All Transactions With Liquidation')

        except Exception as e:print('Error In Generating Report Of All Transactions With Liquidation - {}'.format(str(e)))


    def Compsation_table_backup(self):

        FNAME = f'Daily_Bk_{"retailercompansation"}_{year}{month}{day}.csv'
        REPORTS_PATH = f'CompensationReports/RetailerCompansationBackup/'

        dataFrame = pd.read_sql_table("retailercompansation",  con=engine).astype('str')
        dataFrame.to_csv(REPORTS_PATH+FNAME)

if __name__ == '__main__':
    pass