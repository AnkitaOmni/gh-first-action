from model import *
import pandas as pd
from datetime import datetime
from database import DatabaseConnections
from queries import clean_file_adjustments
from adj_integration import IntegrateAdjustments



db = DatabaseConnections()
engine = db.sqlalchemy_connection()


def currency(amount):
    return "${:,.2f}".format(amount)


class Adjustments():
    def __init__(self, file1):
        self.fname = file1


    def upload_to_db(self):
        fm1 = pd.read_csv(self.fname,  index_col=False,  dtype=str)
        clean_file_adjustments()
        fm1.to_sql(name='fileadjustments', con=engine, if_exists='append', index=False)


    def integrate_to_db(self):
        i = IntegrateAdjustments()
        i.merge_adjustments()
        i.update_manual_adjustments()


    def download_from_db(self):
        path3 = 'CompensationReports/AdjustmentReports/'
        today = datetime.now().strftime("%Y%m%d")

        ipm = pd.read_sql('SELECT * FROM fileadjustments', con=engine)
        ins_id = 'Bech'#ipm['ACQUIRING_INSTITUTION_IDENTIFICATION'][0]
        ipm = ipm[['LocalTransactionDate','AcquiringInstitutionIdentification','CardAcceptorIdentification','TransactionAmount','CardType']]
        #ipm = ipm[['TXN_DATE','CARD_ACCEPTOR_IDENTIFICATION','TRANSACTION_AMOUNT','CARD_TYPE']]
        ipm_credit = ipm.loc[ipm['CardType'] == 'C']
        ipm_debit  = ipm.loc[ipm['CardType'] == 'D']

        manual_credits =  pd.read_sql('SELECT LocalTransactionDate,AcquiringInstitutionIdentification, CardAcceptorIdentification, NewAmount FROM manualadjustmentsextractfile where Authorized = 1 and AdjustmentType like "credit"', con=engine)
        #manual_credits =  pd.read_sql('SELECT LocalTransactionDate, CardAcceptorIdentification, NewAmount FROM manualadjustmentsextractfile where Authorized = 1 and AdjustmentType like "credit"', con=engine)
        manual_debits =  pd.read_sql('SELECT LocalTransactionDate,AcquiringInstitutionIdentification, CardAcceptorIdentification, NewAmount FROM manualadjustmentsextractfile where Authorized = 1 and AdjustmentType like "debit"', con=engine)
        #manual_debits =  pd.read_sql('SELECT LocalTransactionDate, CardAcceptorIdentification, NewAmount FROM manualadjustmentsextractfile where Authorized = 1 and AdjustmentType like "debit"', con=engine)


        manual_credits.rename(columns={"CardAcceptorIdentification": "RETAILER_ID", "NewAmount": "CREDIT"}, inplace=True)
        manual_debits.rename(columns={"CardAcceptorIdentification": "RETAILER_ID", "NewAmount": "DEBIT"}, inplace=True)
        ipm_credit.rename(columns={"TransactionAmount": "CREDIT", "CardAcceptorIdentification":"RETAILER_ID"}, inplace=True)
        ipm_debit.rename(columns={"TransactionAmount": "DEBIT", "CardAcceptorIdentification":"RETAILER_ID"}, inplace=True)

        del ipm_credit['CardType']
        del ipm_debit['CardType']

        adj = manual_credits.append(manual_debits, ignore_index=True)
        adj_cred = adj.append(ipm_credit, ignore_index=True)
        adj_final = adj_cred.append(ipm_debit, ignore_index=True)

        adj_final.fillna(0, inplace=True)
        adj_final['CREDIT'] = adj_final['CREDIT'].astype(int)
        adj_final['DEBIT'] = adj_final['DEBIT'].astype(int)
        adj_final['NET'] = adj_final['CREDIT'] - adj_final['DEBIT']
        adj_report = adj_final.groupby(by=["AcquiringInstitutionIdentification","RETAILER_ID"]).sum().reset_index()
        #adj_report = adj_final.groupby(by=["RETAILER_ID"]).sum().reset_index()
        file_name = "{}AdjusmentsReport{}.csv".format(ins_id, today)
        adj_report.to_csv(path3+file_name, index=False)


class ConciliateWithFiles():
    ''' Base class for conciliation process'''

    def __init__(self, file1, file2, file1_keys, file2_keys):
        self.fm1_name = file1.split('/')[1]
        self.fm2_name = file2.split('/')[1]
        self.fm1 = pd.read_csv(file1)
        self.fm2 = pd.read_csv(file2)
        self.fm1_keys = file1_keys
        self.fm2_keys = file2_keys


    def create_report(self):
        ''' Create the report with provided files'''

        comm = pd.merge(self.fm1, self.fm2, how='inner', left_on=self.fm1_keys, right_on=self.fm2_keys, indicator=True)
        left = pd.merge(self.fm1, self.fm2, how='left', left_on=self.fm1_keys, right_on=self.fm2_keys, indicator=True)
        l_merged = left[left['_merge'] == 'left_only']

        right = pd.merge(self.fm1, self.fm2, how='right', 
            left_on=self.fm1_keys, right_on=self.fm2_keys, indicator=True)
        r_merged = right[right['_merge'] == 'right_only']

        l_merged = l_merged.dropna()
        r_merged = r_merged.dropna()

        amounts = (currency(self.fm1['TRANSACTION_AMOUNT'].sum()),
                   currency(self.fm2['TRANSACTION_AMOUNT'].sum()),
                   currency(comm['TRANSACTION_AMOUNT_x'].sum()),
                   currency(l_merged['TRANSACTION_AMOUNT_x'].sum()),
                   currency(r_merged['TRANSACTION_AMOUNT_x'].sum()))


        summary = pd.DataFrame(

            {
            'Registros presentes en {} (A)'.format(self.fm1_name): [self.fm1.shape[0]], 
            'Registros presentes en {} (B)'.format(self.fm2_name): [self.fm2.shape[0]], 
            'Registros presentes en ambos archivos': [comm.shape[0]], 
            'Registros presentes en A y no en B': [l_merged.shape[0]], 
            'Registros presentes en B y no en A':[r_merged.shape[0]]}
            )

        comm.to_csv('CompensationReports/ConciliationReports/matched.csv')
        summary = summary.to_dict('records')
        comm = comm.to_dict('records')
        l_merged = l_merged.to_dict('records')
        r_merged = r_merged.to_dict('records')

        # parse(summary, comm, l_merged, r_merged, amounts)


class Conciliation():
    ''' Base class for conciliation process'''

    def __init__(self, file_keys, output_loc):
        # self.fm1_name = file1.split('/')[3]
        # self.fm2_name = file2.split('/')[3]
        # self.acquirer_df = pd.read_csv(file1)
        # self.issuer_df = pd.read_csv(file2)

        self.acquirer_df = pd.read_sql('SELECT * FROM acquirerextract', con=engine) #dtype={'TransactionAmount':int64},
        self.issuer_df = pd.read_sql('SELECT * FROM issuerextract', con=engine)
        self.file_keys = file_keys

        self.output_loc = output_loc


    def create_report(self):
        ''' Create the report with provided files'''

        # self.acquirer_df = self.acquirer_df.astype({"TransactionAmount": int})
        # self.issuer_df = self.issuer_df.astype({"TransactionAmount": int})

        # common = pd.merge(self.acquirer_df, self.issuer_df, how='inner',
        #                   left_on=self.file_keys, right_on=self.file_keys, indicator=True)
                          
        left = pd.merge(self.acquirer_df[['RetrievalReferenceNumber','TransmissionDateandTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification']], self.issuer_df[['RetrievalReferenceNumber','TransmissionDateandTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification']], how='left', on=self.file_keys, indicator=True)
        l_merged = left[left['_merge'] == 'left_only']

        # print(f'size of acquirer - original {left.shape[0]} and left {l_merged.shape[0]}')

        right = pd.merge(self.acquirer_df[['RetrievalReferenceNumber','TransmissionDateandTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification']], self.issuer_df[['RetrievalReferenceNumber','TransmissionDateandTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification']], how='right', on=self.file_keys, indicator=True)
        r_merged = right[right['_merge'] == 'right_only']

        # print(f'size of issuer - original {right.shape[0]} and right {r_merged.shape[0]}')
        l_merged = l_merged.dropna()
        r_merged = r_merged.dropna()



        # df['zipcode'] = df.zipcode.astype('category')


        # self.acquirer_df = self.acquirer_df.astype({"TransactionAmount": int})
        # intialise total_data of lists.
        # total_data = {'No': ['Records present in {} (A)', 'Records present in {} (B)', 'Records present in both files', 'Records present in A and not B', 'Records present in B and not A'],
        #         'Transaction Count': [self.acquirer_df.shape[0], self.issuer_df.shape[0], common.shape[0], l_merged.shape[0], r_merged.shape[0]],
        #         'Amount': [currency(self.acquirer_df['TransactionAmount'].sum()),
        #                    currency(self.issuer_df['TransactionAmount'].sum()),
        #                    currency(common['TransactionAmount'].sum()),
        #                    currency(l_merged['TransactionAmount'].sum()),
        #                    currency(r_merged['TransactionAmount'].sum())]}

        # self.acquirer_df.loc[(df['ResponseCode'] == '00') & (df['column_name'] <= B)]
        aa = self.acquirer_df.loc[self.acquirer_df['ResponseCode'] == '00'].shape[0]
        # print(f"approved count of acquirer {aa}")

        bb = self.acquirer_df['TransactionAmount'].loc[self.acquirer_df['ResponseCode'] == '00'].sum()
        # print(f"approved amount of acquirer {bb}")

        cc = self.issuer_df.loc[self.issuer_df['ResponseCode'] == '00'].shape[0]
        # print(f"approved count of issuer {cc}")

        dd = self.issuer_df['TransactionAmount'].loc[self.issuer_df['ResponseCode'] == '00'].sum()
        # print(f"approved amount of issuer {dd}")


        ee = r_merged.loc[r_merged['ResponseCode'] == '00'].shape[0]
        # print(f"approved missing count of acquirer {ee}")

        ff = r_merged['TransactionAmount'].loc[r_merged['ResponseCode'] == '00'].sum()
        # print(f"approved missing amount of acquirer {ff}")


        gg = l_merged.loc[l_merged['ResponseCode'] == '00'].shape[0]
        # print(f"approved missing count of issuer {gg}")

        hh = l_merged['TransactionAmount'].loc[l_merged['ResponseCode'] == '00'].sum()
        # print(f"approved missing amount of issuer {hh}")




        mm = self.acquirer_df.loc[self.acquirer_df['ResponseCode'] != '00'].shape[0]
        # print(f"approved count of acquirer {mm}")

        nn = self.acquirer_df['TransactionAmount'].loc[self.acquirer_df['ResponseCode'] != '00'].sum()
        # print(f"approved amount of acquirer {nn}")

        oo = self.issuer_df.loc[self.issuer_df['ResponseCode'] != '00'].shape[0]
        # print(f"approved count of issuer {oo}")

        pp = self.issuer_df['TransactionAmount'].loc[self.issuer_df['ResponseCode'] != '00'].sum()
        # print(f"approved amount of issuer {pp}")


        qq = r_merged.loc[r_merged['ResponseCode'] != '00'].shape[0]
        # print(f"approved missing count of acquirer {qq}")

        rr = r_merged['TransactionAmount'].loc[r_merged['ResponseCode'] != '00'].sum()
        # print(f"approved missing amount of acquirer {rr}")


        ss = l_merged.loc[l_merged['ResponseCode'] != '00'].shape[0]
        # print(f"approved missing count of issuer {ss}")

        tt = l_merged['TransactionAmount'].loc[l_merged['ResponseCode'] != '00'].sum()
        # print(f"approved missing amount of issuer {tt}")

        # total_data = [{'#': 'Acquirer Side', 'Total Count': self.acquirer_df.shape[0], 'Total Amount': self.acquirer_df['TransactionAmount'].sum(), 'Aprroved Count': self.acquirer_df.loc[self.acquirer_df['ResponseCode'] == '00'].shape[0], 'Aprroved Amount': self.acquirer_df['TransactionAmount'].loc[self.acquirer_df['ResponseCode'] == '00'].sum()},
        #         {'#': 'Issuer Side', 'Total Count': self.issuer_df.shape[0], 'Total Amount': self.issuer_df['TransactionAmount'].sum(), 'Aprroved Count': self.issuer_df.loc[self.issuer_df['ResponseCode'] == '00'].shape[0], 'Aprroved Amount': self.issuer_df['TransactionAmount'].loc[self.issuer_df['ResponseCode'] == '00'].sum()},
        #         # {'#': 'Present at Both Side', 'Transaction Count': common.shape[0], 'Amount': currency(common['TransactionAmount'].sum())},
        #         {'#': 'Missing Count at Issuer Side', 'Total Count': l_merged.shape[0], 'Total Amount': l_merged['TransactionAmount'].sum(), 'Aprroved Count': l_merged.loc[l_merged['ResponseCode'] == '00'].shape[0], 'Aprroved Amount': l_merged['TransactionAmount'].loc[l_merged['ResponseCode'] == '00'].sum()},
        #         {'#': 'Missing Count at Acquirer Side', 'Total Count': r_merged.shape[0], 'Total Amount': r_merged['TransactionAmount'].sum(), 'Aprroved Count': r_merged.loc[r_merged['ResponseCode'] == '00'].shape[0], 'Aprroved Amount': r_merged['TransactionAmount'].loc[r_merged['ResponseCode'] == '00'].sum()}]


        total_data = {
            '#': ['Acquirer Side', 'Issuer Side'],
            'Total Count': [self.acquirer_df.shape[0], self.issuer_df.shape[0]],
            'Total Amount': [currency(self.acquirer_df['TransactionAmount'].sum()), currency(self.issuer_df['TransactionAmount'].sum())],
            'Missing Count': [r_merged.shape[0], l_merged.shape[0]],
            'Missing Amount': [currency(r_merged['TransactionAmount'].sum()), currency(l_merged['TransactionAmount'].sum())]
        }

        approved_data = {
            '#': ['Acquirer Side', 'Issuer Side'],
            'Total Count': [f'{aa}', f'{cc}'],
            'Total Amount': [currency(bb), currency(dd)],
            'Missing Count': [f'{ee}', f'{gg}'],
            'Missing Amount': [currency(ff), currency(hh)]
        }

        declined_data = {
            '#': ['Acquirer Side', 'Issuer Side'],
            'Total Count': [f'{mm}', f'{oo}'],
            'Total Amount': [currency(nn), currency(pp)],
            'Missing Count': [f'{qq}', f'{ss}'],
            'Missing Amount': [currency(rr), currency(tt)]
        }
        # amounts = (currency(self.acquirer_df['TransactionAmount'].sum()),
        #            currency(self.issuer_df['TransactionAmount'].sum()),
        #            currency(common['TransactionAmount'].sum()),
        #            currency(l_merged['TransactionAmount'].sum()),
        #            currency(r_merged['TransactionAmount'].sum()))

        # total_df = pd.DataFrame({'Records present in {} (A)'.format(self.fm1_name): [self.acquirer_df.shape[0]],
        #                         'Records present in {} (B)'.format(self.fm2_name): [self.issuer_df.shape[0]],
        #                         'Records present in both files': [common.shape[0]],
        #                         'Records present in A and not B': [l_merged.shape[0]],
        #                         'Records present in B and no A': [r_merged.shape[0]]})

        total_df = pd.DataFrame(total_data, columns=[  '#', 
                                                'Total Count', 
                                                'Total Amount',
                                                'Missing Count', 
                                                'Missing Amount'])

        approved_df = pd.DataFrame(approved_data, columns=[  '#', 
                                                'Total Count', 
                                                'Total Amount',
                                                'Missing Count', 
                                                'Missing Amount'])

        declined_df = pd.DataFrame(declined_data, columns=[  '#', 
                                                'Total Count', 
                                                'Total Amount',
                                                'Missing Count', 
                                                'Missing Amount'])


        # summary_file = self.output_loc + f"/Summary_{datetime.now().strftime(r'%Y%m%d')}.csv"
        # total_df.to_csv(summary_file, index=False)

        # Create a Pandas Excel writer object, using XlsxWriter as the engine.
        file_name = self.output_loc + f"/Conciliation_Summary_{datetime.now().strftime(r'%Y%m%d')}.xlsx"
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        total_df.to_excel(writer, sheet_name='Total', index=False)
        approved_df.to_excel(writer, sheet_name='Approved', index=False)
        declined_df.to_excel(writer, sheet_name='Declined', index=False)

        writer.close()

        # common_file = self.output_loc + 'common.csv'
        # common.to_csv(common_file, index=False)

        left_present_in_A_file = self.output_loc + f"/TotalMissingAtIssuer_{datetime.now().strftime(r'%Y%m%d')}.csv"
        l_merged.to_csv(left_present_in_A_file, index=False)

        right_present_in_B_file = self.output_loc + f"/TotalMissingAtAcquirer_{datetime.now().strftime(r'%Y%m%d')}.csv"
        r_merged.to_csv(right_present_in_B_file, index=False)

        return total_df, approved_df, declined_df

class ReversalsDeclinedAgainstApproved():
    ''' Class for finding Originals Of Reversals At Acquirer Side'''
    ''' Declined Reversals at Brands are presented as Credit voucher/Refund/Reversals if Original is Approved'''

    def __init__(self, file_keys, output_loc):

        self.reversal_decline = pd.read_sql('SELECT *  \
                                        FROM issuerextract \
                                        WHERE MessageType = "0420" \
                                        AND ResponseCode != "00"; ', con=engine) 
        # self.reversal_approved = pd.read_sql('SELECT *  \
        #                                 FROM issuerextract \
        #                                 WHERE MessageType = "0420" \
        #                                 AND ResponseCode = "00"; ', con=engine)

        self.purchase_approved = pd.read_sql('SELECT *  \
                                        FROM issuerextract \
                                        WHERE MessageType = "0210" \
                                        AND ResponseCode = "00"; ', con=engine)

        self.file_keys = file_keys

        self.output_loc = output_loc

    def create_report(self):
        ''' Create the report with provided files'''
        
                          
        left = pd.merge(self.reversal_decline[['RetrievalReferenceNumber','LocalTransactionDate','LocalTransactionTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification','SystemsTraceAuditNumber']], self.purchase_approved[['RetrievalReferenceNumber','LocalTransactionDate','LocalTransactionTime','Track2Data','TransactionAmount','MessageType','ProcessingCode','ResponseCode','CardAcceptorIdentification','SystemsTraceAuditNumber']], how='inner',suffixes=("_reversal_decline", "_purchase_approved"), on=self.file_keys, indicator=True)
        l_merged = left[left['_merge'] == 'both']
        l_merged = l_merged.dropna()
        left_present_in_A_file = self.output_loc + f"/ReversalsDeclined_{datetime.now().strftime(r'%Y%m%d')}.csv"
        l_merged.to_csv(left_present_in_A_file, index=False)



if __name__ == '__main__':
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # * ReversalsDeclinedAgainstApproved # # # # # # # # # 
    output_ep_file_loc = '.'
    file_keys = ['RetrievalReferenceNumber', 'LocalTransactionDate', 'LocalTransactionTime', 
                'Track2Data','ProcessingCode', 'TransactionAmount']
    c = ReversalsDeclinedAgainstApproved(file_keys, output_ep_file_loc)
    summary_frame = c.create_report()

