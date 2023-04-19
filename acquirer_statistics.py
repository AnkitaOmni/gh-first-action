import pandas as pd
from peewee import fn
from datetime import datetime
from model import AcquirerExtract, TransactionHistory


class AcquirerStats:
    ''' Base class for AcquirerStats '''

    def __init__(self, path):

        self.today = datetime.now().strftime("%y%m%d")  # today's date format YYMMDD
        self.path = path  # './CompensationReports/RetailerReports/'
        self.acquirer_is = {'0012': 'Geo Pagos', '0014': 'Alvi', '2003': 'Digital Acquirer'}

    def daily_responsecodes_count_against_messagetypes(self, report_name):
        query = AcquirerExtract.select(
            AcquirerExtract.AcquiringInstitutionIdentification.alias('NAME'),
            AcquirerExtract.MessageType.alias('MSG_TYP'),
            AcquirerExtract.ResponseCode.alias('RESP_CODE'),
            fn.COUNT(AcquirerExtract.ResponseCode).alias('COUNT'),
        ).group_by(AcquirerExtract.AcquiringInstitutionIdentification,
                   AcquirerExtract.MessageType,
                   AcquirerExtract.ResponseCode).dicts()

        data_frame = pd.DataFrame(query)
        # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
        file_name = "{}_{}.xlsx".format(report_name, self.today)
        writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

        for x in data_frame.index:
            data_frame.loc[x, "NAME"] = self.acquirer_is.get(
                data_frame.loc[x, "NAME"], 'UnKnown')

        if not data_frame.empty:
            for k, v in data_frame.groupby('NAME'):
                v.to_excel(writer, sheet_name=k, columns=['MSG_TYP','RESP_CODE','COUNT'], index=False)
        writer.close()


    def monthly_responsecodes_count_against_messagetypes(self, report_name, first_date, last_date):
        first_date = datetime.strptime(first_date, "%Y-%m-%d")
        last_date = datetime.strptime(last_date, "%Y-%m-%d")

        query = TransactionHistory.select(
            TransactionHistory.AcquiringInstitutionIdentification.alias('NAME'),
            TransactionHistory.MessageType.alias('MSG_TYP'),
            TransactionHistory.ResponseCode.alias('RESP_CODE'),
            fn.COUNT(TransactionHistory.ResponseCode).alias('COUNT'),
        ).where(TransactionHistory.LocalTransactionDate.between(first_date, last_date)).group_by(TransactionHistory.AcquiringInstitutionIdentification,
                                                                                                 TransactionHistory.MessageType,
                                                                                                 TransactionHistory.ResponseCode).dicts()

        data_frame = pd.DataFrame(query)
        # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
        file_name = "{}_{}.xlsx".format(report_name, self.today)
        writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

        for x in data_frame.index:
            data_frame.loc[x, "NAME"] = self.acquirer_is.get(
                data_frame.loc[x, "NAME"], 'UnKnown')

        if not data_frame.empty:
            for k, v in data_frame.groupby('NAME'):
                v.to_excel(writer, sheet_name=k, columns=['MSG_TYP','RESP_CODE','COUNT'], index=False)

        writer.close()
        return data_frame


    def monthly_pointofservice_entrymode_count(self, report_name, first_date, last_date):
            first_date = datetime.strptime(first_date, "%Y-%m-%d")
            last_date = datetime.strptime(last_date, "%Y-%m-%d")

            query = TransactionHistory.select(
                TransactionHistory.AcquiringInstitutionIdentification.alias('NAME'),
                TransactionHistory.PointofServiceEntryModeCode.alias('POS_ENTRYMODE_CODE'),
                fn.COUNT(TransactionHistory.PointofServiceEntryModeCode).alias('COUNT'),
            ).where(TransactionHistory.LocalTransactionDate.between(first_date, last_date)).group_by(TransactionHistory.AcquiringInstitutionIdentification,
                                                                                                    TransactionHistory.PointofServiceEntryModeCode).dicts()
            data_frame = pd.DataFrame(query)
            # * Create a Pandas Excel writer object, using XlsxWriter as the engine.
            file_name = "{}_{}.xlsx".format(report_name, self.today)
            writer = pd.ExcelWriter(self.path + file_name, engine='xlsxwriter')

            for x in data_frame.index:
                data_frame.loc[x, "NAME"] = self.acquirer_is.get(
                    data_frame.loc[x, "NAME"], 'UnKnown')

            if not data_frame.empty:
                for k, v in data_frame.groupby('NAME'):
                    v.to_excel(writer, sheet_name=k, columns=['POS_ENTRYMODE_CODE','COUNT'], index=False)

            writer.close()
            return data_frame


if __name__ == "__main__":
    a = AcquirerStats("./CompensationReports/MonthlyReports/Aug_2022/Acquirer/")  # "./CompensationReports/RetailerReports/"
    print(a.monthly_responsecodes_count_against_messagetypes("Monthly_Acquirer_ResponseCodes", "2022-07-01", "2022-07-31"))
    print(a.monthly_pointofservice_entrymode_count("Monthly_Acquirer_PointofServiceEntryModeCode", "2022-07-01", "2022-07-31"))
