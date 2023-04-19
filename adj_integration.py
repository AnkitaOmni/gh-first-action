import time
import pandas as pd
from database import DatabaseConnections
from queries import clean_manual_adjustments


# * Authorized:  1: authorized, 0: decliend, 2: pending, 3: processed
# * AdjustmentType: 1: MA, 2:FA
# * CardType: C or D (FA)
# * AdjustmentType: credit or debit (MA)


db = DatabaseConnections()
engine = db.sqlalchemy_connection()


class IntegrateAdjustments():
    """ 
    To Merege & Update Adjustments :-
    1. File Adjustments
    2. Manual Adjustmetns
    3. All Adjustmetns

    """

    def __init__(self):

        self.df_fa = pd.read_sql_table('fileadjustments', con=engine)
        self.df_ma = pd.read_sql_table('manualadjustmentsextractfile', con=engine)
        self.final = None

    def merge_adjustments(self):

        manual = self.df_ma
        ipm = self.df_fa

        manual = manual.loc[manual['Authorized'] == 1]

        manual['NetworkInternationalIdentifierCode'] = 1  # adjusmenttype [Manual]
        ipm['NetworkInternationalIdentifierCode'] = 2  # adjusmenttype [File]
        manual['CardType'] = manual['AdjustmentType'].apply(lambda x: 'C' if x == 'credit' else 'D')
        manual['TransactionAmount'] = manual['NewAmount']

        del manual['Comments']
        del manual['NewAmount']
        del manual['Authorized']
        del manual['AdjustmentType']
        del manual['AdjustmentAmountType']

        final = manual.append(ipm, ignore_index=True, sort=False)
        final['TimeStamp'] = int(time.time())
        del final['id']

        final['TransactionAmount'] = final['TransactionAmount'].astype(int)
        # * Dishant :- Below line was uncommented for Adjsutment Testing [07_May_2021]
        # * if card type is debit then put negative amount for transaction
        final.loc[final['CardType'] == 'D', 'TransactionAmount'] = abs(final['TransactionAmount']) * -1

        self.final = final
        # * Dishant [17Jun2021] :- Insert Data Into "AllAdjustments" includes all the Manual & File Adjustments
        self.final.to_sql(name='alladjustments', con=engine, if_exists='append', index=False)


    def update_manual_adjustments(self):
        manual = pd.read_sql_table('manualadjustmentsextractfile', con=engine)
        manual['Authorized'] = manual['Authorized'].apply(lambda x: 3 if x == 1 else x)
        manual['TimeStamp'] = int(time.time())
        manual['id'] = manual.index + manual.size
        clean_manual_adjustments()
        manual.to_sql(name='manualadjustmentsextractfile',con=engine, if_exists='append', index=False)

    def liquidated_all_adjustments(self):
        all_adj = pd.read_sql_table('alladjustments', con=engine)
        del all_adj['id']
        all_adj['TimeStamp'] = int(time.time())
        all_adj.to_sql(name='acquireroriginal', con=engine, if_exists='append', index=False)
        # * RRN List To Return
        adj_rrn_list = [str(rrn) for rrn in all_adj['RetrievalReferenceNumber']]
        return adj_rrn_list


if __name__ == '__main__':
    # i = IntegrateAdjustments()
    # i.merge_adjustments()
    # i.update_manual_adjustments()
    # i.liquidated_all_adjustments()
    pass
