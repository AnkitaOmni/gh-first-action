from model import *
import pandas as pd
from peewee import fn
from datetime import datetime


class IssuerStats:
    ''' Base class for IssuerStats'''

    def __init__(self, path):

        self.today = datetime.now().strftime("%y%m%d")  # today's date format YYMMDD
        self.path = path  # './CompensationReports/RetailerReports/'
        self.issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}


    def daily_responsecodes_count_against_messagetypes(self, report_name):
        query = IssuerExtract.select(
            IssuerExtract.ForwardingInstitutionIdentification.alias('NAME'),
            IssuerExtract.MessageType.alias('MSG_TYP'),
            IssuerExtract.ResponseCode.alias('RESP_CODE'),
            fn.COUNT(IssuerExtract.ResponseCode).alias('COUNT'),
        ).group_by(IssuerExtract.ForwardingInstitutionIdentification,
                   IssuerExtract.MessageType,
                   IssuerExtract.ResponseCode).dicts()

        data_frame = pd.DataFrame(query)
        # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
        file_name = "{}_{}.xlsx".format(report_name, self.today)
        writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

        for x in data_frame.index:
            data_frame.loc[x, "NAME"] = self.issuer_is.get(
                data_frame.loc[x, "NAME"], 'UnKnown')

        if not data_frame.empty:
            for k, v in data_frame.groupby('NAME'):
                v.to_excel(writer, sheet_name=k, columns=['MSG_TYP','RESP_CODE','COUNT'], index=False)
        writer.close()


    def monthly_responsecodes_count_against_messagetypes(self, report_name, first_date, last_date):
        first_date = datetime.strptime(first_date, "%Y-%m-%d")
        last_date = datetime.strptime(last_date, "%Y-%m-%d")

        query = TransactionHistoryIssuer.select(
            TransactionHistoryIssuer.ForwardingInstitutionIdentification.alias('NAME'),
            TransactionHistoryIssuer.MessageType.alias('MSG_TYP'),
            TransactionHistoryIssuer.ResponseCode.alias('RESP_CODE'),
            fn.COUNT(TransactionHistoryIssuer.ResponseCode).alias('COUNT'),
        ).where(TransactionHistoryIssuer.LocalTransactionDate.between(first_date, last_date)).group_by(TransactionHistoryIssuer.ForwardingInstitutionIdentification,
                                                                                                 TransactionHistoryIssuer.MessageType,
                                                                                                 TransactionHistoryIssuer.ResponseCode).dicts()
        data_frame = pd.DataFrame(query)
        # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
        file_name = "{}_{}.xlsx".format(report_name, self.today)
        writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

        for x in data_frame.index:
            data_frame.loc[x, "NAME"] = self.issuer_is.get(
                data_frame.loc[x, "NAME"], 'UnKnown')

        if not data_frame.empty:
            for k, v in data_frame.groupby('NAME'):
                v.to_excel(writer, sheet_name=k, columns=['MSG_TYP','RESP_CODE','COUNT'], index=False)

        writer.close()
        return data_frame


    def monthly_pointofservice_entrymode_count(self, report_name, first_date, last_date):
            first_date = datetime.strptime(first_date, "%Y-%m-%d")
            last_date = datetime.strptime(last_date, "%Y-%m-%d")

            query = TransactionHistoryIssuer.select(
                TransactionHistoryIssuer.ForwardingInstitutionIdentification.alias('NAME'),
                TransactionHistoryIssuer.PointofServiceEntryModeCode.alias('POS_ENTRYMODE_CODE'),
                fn.COUNT(TransactionHistoryIssuer.PointofServiceEntryModeCode).alias('COUNT'),
            ).where(TransactionHistoryIssuer.LocalTransactionDate.between(first_date, last_date)).group_by(TransactionHistoryIssuer.AcquiringInstitutionIdentification,
                                                                                                    TransactionHistoryIssuer.PointofServiceEntryModeCode).dicts()

            data_frame = pd.DataFrame(query)
            # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
            file_name = "{}_{}.xlsx".format(report_name, self.today)
            writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

            for x in data_frame.index:
                data_frame.loc[x, "NAME"] = self.issuer_is.get(
                    data_frame.loc[x, "NAME"], 'UnKnown')

            if not data_frame.empty:
                for k, v in data_frame.groupby('NAME'):
                    v.to_excel(writer, sheet_name=k, columns=['POS_ENTRYMODE_CODE','COUNT'], index=False)

            writer.close()
            return data_frame


if __name__ == "__main__":
    a = IssuerStats("./CompensationReports/MonthlyReports/Aug_2022/Issuer/")  # "./CompensationReports/RetailerReports/"
    print(a.monthly_responsecodes_count_against_messagetypes("Monthly_Issuer_ResponseCodes", "2022-07-01", "2022-07-31"))
    print(a.monthly_pointofservice_entrymode_count("Monthly_Issuer_PointofServiceEntryModeCode", "2022-07-01", "2022-07-31"))
