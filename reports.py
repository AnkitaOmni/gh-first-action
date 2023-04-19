from model import *
import pandas as pd
from peewee import fn
from datetime import datetime


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
        except table_name.DoesNotExist:
            print('Error In Generating Report Of {}'.format(report_name))
        except Exception as e:
            print('Error In Generating Report Of {} - {}'.format(report_name, str(e)))


    def transactions_summary_report(self):
        try:
            query = ISERetailer.select(
                ISERetailer.AcquiringInstitutionIdentification.alias('ACQ_INST_ID'),
                ISERetailer.CardAcceptorIdentification.alias('RETAILER_ID'),
                fn.COUNT(ISERetailer.CardAcceptorIdentification).alias('TOTAL_TXN_CNT'),
                ISERetailer.MessageType.alias('MESSAGE_TYPE'),
                ISERetailer.ProcessingCode.alias('PROCESSING_CODE'),
                ISERetailer.ChannelType.alias('CHANNEL_TYPE'),
                fn.SUM(ISERetailer.TransactionAmount).alias('TOTAL_AMOUNT'),
                fn.SUM(ISERetailer.TotalCommissions).alias('TOTAL_COMMISSION'),
                fn.SUM(ISERetailer.TotalTaxes).alias('TOTAL_TAX'),
                fn.SUM(ISERetailer.TotalDiscounts).alias('TOTAL_DISCOUNT'),
                fn.SUM(ISERetailer.FinalAmount).alias('FINAL_AMOUNT')).where(
                    ISERetailer.ResponseCode == '00').group_by(
                    ISERetailer.AcquiringInstitutionIdentification,
                    ISERetailer.CardAcceptorIdentification,
                    ISERetailer.MessageType,
                    ISERetailer.ProcessingCode,
                    ISERetailer.ChannelType
            ).dicts()
           
            data_frame = pd.DataFrame(query, columns=['ACQ_INST_ID', 'RETAILER_ID', 'TOTAL_TXN_CNT', 'MESSAGE_TYPE', 'PROCESSING_CODE', 'CHANNEL_TYPE',
                                                      'TOTAL_AMOUNT', 'TOTAL_COMMISSION', 'TOTAL_TAX', 'TOTAL_DISCOUNT', 'FINAL_AMOUNT'])
            
            for x, y in data_frame.groupby('ACQ_INST_ID'):
                for k, v in y.groupby('CHANNEL_TYPE'):
                    file_name = "{}_{}_RetailerSummary_{}.csv".format(x, k, self.today)
                    v.to_csv(self.path + file_name, index=False)
            print("Transactions Summary Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

        except ISERetailer.DoesNotExist:
            print('Error In Generating Report Of Transactions Summary')

        except Exception as e:
            print('Error In Generating Report Of Transactions Summary - {}'.format(str(e)))


    def all_transactions_report(self):
        try:
            query = ISERetailer.select(ISERetailer.AcquiringInstitutionIdentification,
                                       ISERetailer.CardAcceptorIdentification,
                                       ISERetailer.CardAcceptorTerminalIdentification,
                                       ISERetailer.MerchantTypeCode,
                                       ISERetailer.MessageType,
                                       ISERetailer.ResponseCode,
                                       ISERetailer.ProcessingCode,
                                       ISERetailer.LocalTransactionTime,
                                       ISERetailer.LocalTransactionDate,
                                       ISERetailer.SettlementDate,
                                       ISERetailer.Track2Data,
                                       ISERetailer.SystemsTraceAuditNumber,
                                       ISERetailer.RetrievalReferenceNumber,
                                       ISERetailer.CardAcceptorNameLocation,
                                       ISERetailer.ChannelType,
                                       ISERetailer.CardType,
                                       ISERetailer.TransactionAmount,
                                       ISERetailer.RetCardTypeCommision,
                                       ISERetailer.RetMccCommision,
                                       ISERetailer.RetBinCommision,
                                       ISERetailer.RetTxnIdentifierCommision,
                                       ISERetailer.Retailer,
                                       ISERetailer.Acquirer,
                                       ISERetailer.Issuer,
                                       ISERetailer.TotalCommissions,
                                       ISERetailer.Retefuente,
                                       ISERetailer.Reteica,
                                       ISERetailer.Cree,
                                       ISERetailer.Reteiva,
                                       ISERetailer.TotalTaxes,
                                       ISERetailer.TotalDiscounts,
                                       ISERetailer.FinalAmount).where(ISERetailer.ResponseCode == '00').dicts()

            data_frame = pd.DataFrame(query, columns=['AcquiringInstitutionIdentification', 'CardAcceptorIdentification', 'CardAcceptorTerminalIdentification',
                                                      'MerchantTypeCode', 'MessageType', 'ResponseCode', 'ProcessingCode', 'LocalTransactionTime',
                                                      'LocalTransactionDate', 'SettlementDate', 'Track2Data', 'SystemsTraceAuditNumber', 'RetrievalReferenceNumber',
                                                      'CardAcceptorNameLocation', 'ChannelType', 'CardType', 'TransactionAmount', 'RetCardTypeCommision',
                                                      'RetMccCommision', 'RetBinCommision', 'RetTxnIdentifierCommision', 'Retailer', 'Acquirer', 'Issuer',
                                                      'TotalCommissions', 'Retefuente', 'Reteica', 'Cree', 'Reteiva', 'TotalTaxes', 'TotalDiscounts', 'FinalAmount'])

            for x, y in data_frame.groupby('AcquiringInstitutionIdentification'):
                for k, v in y.groupby('ChannelType'):
                    file_name = "{}_{}_Retailer_{}.csv".format(x, k, self.today)
                    v.to_csv(self.path + file_name, index=False)
            print("All Transactions Report With Liquidation Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

        except ISERetailer.DoesNotExist:
            print('Error In Generating Report Of All Transactions With Liquidation')

        except Exception as e:
            print('Error In Generating Report Of All Transactions With Liquidation - {}'.format(str(e)))


    def all_retailer_report(self):

        try:
            query = RetailerId.select(RetailerId.RetailerId,
                                      RetailerId.EntityId,
                                      RetailerId.AcquirerRegionCode,
                                      RetailerId.Name,
                                      RetailerId.CountryCode,
                                      RetailerId.StateCode,
                                      RetailerId.CityCode,
                                      RetailerId.CountyCode,
                                      RetailerId.Address,
                                      RetailerId.PostalCode,
                                      RetailerId.Phone,
                                      RetailerId.EmailAddress,
                                      RetailerId.IdentificationTypeCode,
                                      RetailerId.IdentificationNumber,
                                      RetailerId.MCC,
                                      RetailerId.StatusCode).dicts()

            data_frame = pd.DataFrame(query, columns=["RetailerId", "EntityId", "AcquirerRegionCode", "Name", "CountryCode",
                                                      "StateCode", "CityCode", "CountyCode", "Address", "PostalCode", "Phone",
                                                      "EmailAddress", "IdentificationTypeCode", "IdentificationNumber", "MCC", "StatusCode"])

            file_name = "AllRetailerStatus_{}.csv".format(self.today)
            data_frame.to_csv(self.path + file_name, index=False)

            print("All Retailers Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except ISERetailer.DoesNotExist:
            print('Error In Generating Report Of All Retailers')
        except Exception as e:
            print('Error In Generating Report Of All Retailers - {}'.format(str(e)))


    def blocked_retailer_report(self):

        try:
            query = RetailerId.select(RetailerId.RetailerId, RetailerId.EntityId, RetailerId.AcquirerRegionCode,
                                      RetailerId.Name, RetailerId.CountryCode, RetailerId.StateCode, RetailerId.CityCode,
                                      RetailerId.CountyCode, RetailerId.Address, RetailerId.PostalCode, RetailerId.Phone,
                                      RetailerId.EmailAddress, RetailerId.IdentificationTypeCode,
                                      RetailerId.IdentificationNumber, RetailerId.MCC,
                                      RetailerId.StatusCode).where(RetailerId.StatusCode == 2).dicts()

            data_frame = pd.DataFrame(query, columns=["RetailerId", "EntityId", "AcquirerRegionCode", "Name", "CountryCode",
                                                      "StateCode", "CityCode", "CountyCode", "Address", "PostalCode", "Phone",
                                                      "EmailAddress", "IdentificationTypeCode", "IdentificationNumber", "MCC", "StatusCode"])

            file_name = "PartialBlockRetailerStatus_{}.csv".format(self.today)
            data_frame.to_csv(self.path + file_name, index=False)

            print("Blocked Retailers Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except ISERetailer.DoesNotExist:
            print('Error In Generating Report Of Blocked Retailers')
        except Exception as e:
            print('Error In Generating Report Of Blocked Retailers - {}'.format(str(e)))




if __name__ == '__main__':
    pass
