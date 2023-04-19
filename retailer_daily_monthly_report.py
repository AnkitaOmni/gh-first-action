import csv
import calendar
from model import *
from sys import argv
from datetime import datetime
from pandas import read_sql_query
from database import DatabaseConnections


db = DatabaseConnections()
engine = db.sqlalchemy_connection()


class RetailerReports:

    def __init__(self, path):
        self.today = datetime.now().strftime("%y%m%d")  # today's date format YYMMDD
        self.path = path  # './CompensationReports/RetailerReports/'

        self.all_cols = ['TRACE_ID', 'ACQ_RRN', 'TOKEN', 'MESSAGE_TYPE', 'MSG_DESC', 'TRANSACTION_SOURCE', 'TRANSACTION_TYPE', 'TRAN_SUBTYPE', 'TRAN_DESC', 'TRANSACTION_AMOUNT', 'TRANSACTION_TIME', 'ENTRY_MODE', 'AUTH_MODE', 'TERMINAL_ID', 'RETAILER_ID', 'LOCATION', 'RESPONSE_CODE', 'RESP_DESC',
                         'ACQUIRER_ID', 'ISSUER_ID', 'RESPONSE_TIME', 'RET_CARDTYPE_COMMISION', 'RET_MCC_COMMISION', 'RET_BIN_COMMISION', 'RET_TXNIDENTIFIER_COMMISION', 'RETAILER', 'ACQUIRER', 'ISSUER', 'TOTAL_COMMISSIONS', 'RETEFUENTE', 'RETEICA', 'CREE', 'RETEIVA', 'TOTAL_TAXES', 'TOTAL_DISCOUNTS', 'FINAL_AMOUNT', 'RULE_DESC']

        self.specific_cols = ['TRACE_ID', 'ACQ_RRN', 'TOKEN', 'MESSAGE_TYPE', 'MSG_DESC', 'TRANSACTION_SOURCE', 'TRANSACTION_TYPE', 'TRAN_SUBTYPE', 'TRAN_DESC', 'TRANSACTION_AMOUNT', 'TRANSACTION_TIME',
                              'ENTRY_MODE', 'AUTH_MODE', 'TERMINAL_ID', 'RETAILER_ID', 'LOCATION', 'RESPONSE_CODE', 'RESP_DESC', 'ACQUIRER_ID', 'ISSUER_ID', 'RESPONSE_TIME', 'TOTAL_COMMISSIONS', 'TOTAL_TAXES', 'FINAL_AMOUNT', 'RULE_DESC']

        self.message_type_desc = {
            "0210": "Response for Financial Request Message",
            "0420": "Reversal Request Message",
            "0430": "Reversal Request Message"
        }

        self.transaction_type_desc = {
            "200000": {
                "sub_type": "Refund",
                "desc": "Refund or Cancel"
            },
            "300000": {
                "sub_type": "Installment Inquiry",
                "desc": "Installment Inquiry"
            },
            "000000": {
                "sub_type": "Payment",
                "desc": "Purchase"
            }
        }

        self.response_code_desc = {
            "11": "APPROVED - VIP",
            "12": "INVALID TXN",
            "13": "INVALID AMT",
            "14": "INVALID CARD NUM.",
            "15": "INACTIVE OR TERMINAL NOT FOUND",
            "31": "NO SHARING",
            "33": "EXPIRED CARD",
            "36": "RESTRICTED CARD",
            "38": "ALLOWABLE PIN TRIES EXCEEDED",
            "41": "LOST CARD",
            "43": "STOLEN CARD",
            "51": "NO SUFFICIENT FUND",
            "54": "EXPIRED CARD",
            "55": "INCORRECT PIN",
            "56": "CAF NOT FOUND",
            "57": "TXN NOT PERMITTED",
            "61": "EXCEED WDRL AMT.",
            "62": "RESTRICTED CARD",
            "65": "EXCEED WDRL FREQ.",
            "68": "RESPONSE RECEIVED TOO LATE",
            "75": "PIN RETRIES EXCEEDED",
            "76": "APPROVED - PRI ENTRY CLUB",
            "77": "APPROVED - PENDING IDENTIFICATION",
            "78": "APPROVED - BLIND",
            "79": "APPROVED - ADMIN TXN.",
            "80": "APPROVED - NAT. NEG. HIT",
            "81": "APPROVED - COMMERCIAL",
            "82": "NO SECURITY BOX",
            "83": "PRIVATE- NO A/C",
            "84": "NO PBF",
            "85": "PBF UPDATE ERROR",
            "86": "INVALID AUTH TYPE",
            "87": "BAD TRACK2",
            "89": "TXN ROUTING ISSUE",
            "94": "DUPLICATE TXN",
            "00": "SUCCESS",
            "01": "REFER CARD ISSUER",
            "02": "REFER CARD ISSUER SPE. COND.",
            "03": "INVALID MERCHANT",
            "04": "CAPTURE",
            "05": "UNAUTHORISED USAGE",
            "06": "UNABLE TO PROCESS TXN",
            "08": "APPROVED - HONOR WITH IDENTIFICATION",
            "N2": "PRE AUTH FULL",
            "N3": "PRIVATE MAX ONLINE REFUND",
            "N4": "PRIVATE MAX OFFLINE REFUND",
            "N5": "PRIVATE MAX CR PER REFUND",
            "N6": "MAX REFUND CR REACHED",
            "N7": "CUSTOM NEG REASON",
            "N8": "OVERFLOOR LIMIT",
            "N9": "MAX NUM REFUND CR",
            "O0": "REF FILE FULL",
            "O1": "NEG FILE PROBLEM",
            "O2": "ADVANCE LESS THAN MIN",
            "O3": "DELINQUENT",
            "O4": "OVER LIMIT TABLE",
            "O5": "PRIVATE PIN REQUIRED",
            "O6": "MOD 10 CHECK",
            "O7": "FORCE POST",
            "O8": "BAD PBF",
            "O9": "NEG FILE PROBLEM",
            "P0": "CAF FILE PROBLEM",
            "P1": "DAILY LIMIT EXCEEDS",
            "P2": "CAPF NOT FOUND",
            "P5": "DELINQUENT",
            "Q0": "INVALID TRAN DATE",
            "Q1": "INVALID EXPIRATION DATE",
            "Q2": "INVALID TRANCODE",
            "Q3": "ADVANCE LESS THAN MIN",
            "Q4": "NUM OF TIMES EXCEEDS",
            "Q5": "DELINQUENT",
            "Q6": "OVER LIMIT TABLE",
            "Q7": "ADVANCE LESS AMT",
            "Q8": "ADMIN CARD NEEDED",
            "Q9": "ENTER LESSER AMT",
            "R0": "APPROVED ADMIN REQ IN WINDOW",
            "R1": "APPROVED ADMIN REQ OUT WINDOW",
            "R2": "APPROVED ADMIN REQ ANYTIME",
            "R3": "CHARGEBACK CUSTOMER FILE UPDATED",
            "R4": "CHARGEBACK CUST.FILE UPDATED ACQR. NOT FOUND",
            "R5": "CHARGEBACK INCORRECT PREFIX NUMBER",
            "R6": "CHARGEBACK INCORRECT RSP CODE OR CPF CON",
            "R7": "ADMIN TXN NOT SUPPORTED",
            "S4": "PTLF IS FULL",
            "S5": "APPROVED, CUSTOMER FILES NOT UPDATED",
            "S6": "APPROVED, FILES NOT UPDATED ACQ. NOT FOUND",
            "S7": "ACCEPTED, INCORRECT DESTINATION",
            "S8": "ADMIN FILE ERROR",
            "S9": "SECURITY DEVICE ERROR",
            "T1": "INVALID AMT",
            "T2": "FORMAT ERROR",
            "T3": "NO CARD RECRD",
            "T4": "INVALID AMT",
            "T5": "CAF STATUS INACTIVE",
            "T6": "BAD UAF",
            "T7": "RESERVED FOR PRIVATE USE",
            "T8": "ERROR, A/C PROBLEM",
            "W8": "CONSULTATION FOR PROD W/OUT INTEREST",
            "W9": "INVALID MENU"
        }


    def commonReport(self, report_name):
        try:
            data = ISERetailer.select().order_by(
                ISERetailer.LocalTransactionDate.desc()).dicts()
            records = []

            for rec in data:
                dicts = {}

                dicts['TRACE_ID'] = rec['SystemsTraceAuditNumber']
                dicts['ACQ_RRN'] = rec['RetrievalReferenceNumber']
                dicts['TOKEN'] = rec['Track2Data'][3:]
                dicts['MESSAGE_TYPE'] = rec['MessageType']
                # self.message_type_desc[ rec['MessageType'] ]
                dicts['MSG_DESC'] = self.message_type_desc.get(
                    rec['MessageType'], '')
                dicts['TRANSACTION_SOURCE'] = "POS"
                dicts['TRANSACTION_TYPE'] = rec['ProcessingCode']
                dicts['TRAN_SUBTYPE'] = self.transaction_type_desc.get(rec['ProcessingCode'], '').get(
                    'sub_type')  # self.transaction_type_desc[ rec['ProcessingCode'] ]
                dicts['TRAN_DESC'] = self.transaction_type_desc.get(
                    rec['ProcessingCode'], '').get('desc')
                dicts['TRANSACTION_AMOUNT'] = rec['TransactionAmount']
                dicts['TRANSACTION_TIME'] = "{} {}".format(
                    rec['LocalTransactionDate'], rec['LocalTransactionTime'])
                dicts['ENTRY_MODE'] = rec['PointofServiceEntryModeCode']
                dicts['AUTH_MODE'] = rec['PersonalIdentificationNumberPINData']
                dicts['TERMINAL_ID'] = rec['CardAcceptorTerminalIdentification']
                dicts['RETAILER_ID'] = rec['CardAcceptorIdentification']
                dicts['LOCATION'] = rec['CardAcceptorNameLocation']
                dicts['RESPONSE_CODE'] = rec['ResponseCode']
                dicts['RESP_DESC'] = self.response_code_desc.get(
                    rec['ResponseCode'], '')
                dicts['ACQUIRER_ID'] = rec['AcquiringInstitutionIdentification']
                dicts['ISSUER_ID'] = rec['ChannelType']
                dicts['RESPONSE_TIME'] = rec['Token2']
                dicts['RET_CARDTYPE_COMMISION'] = rec['RetCardTypeCommision']
                dicts['RET_MCC_COMMISION'] = rec['RetMccCommision']
                dicts['RET_BIN_COMMISION'] = rec['RetBinCommision']
                dicts['RET_TXNIDENTIFIER_COMMISION'] = rec['RetTxnIdentifierCommision']
                dicts['RET_RUBRO_COMMISION'] = rec['RetRubroCommision']
                dicts['RETAILER'] = rec['Retailer']
                dicts['ACQUIRER'] = rec['Acquirer']
                dicts['ISSUER'] = rec['Issuer']
                dicts['TOTAL_COMMISSIONS'] = rec['TotalCommissions']
                dicts['RETEFUENTE'] = rec['Retefuente']
                dicts['RETEICA'] = rec['Reteica']
                dicts['CREE'] = rec['Cree']
                dicts['RETEIVA'] = rec['Reteiva']
                dicts['TOTAL_TAXES'] = rec['TotalTaxes']
                dicts['TOTAL_DISCOUNTS'] = rec['TotalDiscounts']
                dicts['FINAL_AMOUNT'] = rec['FinalAmount']
                dicts['RULE_DESC'] = rec['Token1'].split('#^#')[0]

                records.append(dicts)

            # ise_loader("ISE.html", "{}{}.csv".format(report_name,self.today), records, self.cols)
            self.create_report("{}/{}{}.csv".format(
                self.path, report_name, self.today), self.all_cols, sorted(records, key=lambda i: i['TRANSACTION_TIME']))
        except ISERetailer.DoesNotExist as e:
            print('ISERetailer.DoesNotExist - {} Error : {}'.format(report_name, e))
        except Exception as e:
            print('{} Error : {}'.format(report_name, e))


    def dailyAcquirerReport(self, report_name):
        try:
            channels = ISERetailer.select(
                ISERetailer.AcquiringInstitutionIdentification).distinct().iterator()

            for channel in channels:
                # print("channel name",channel.ChannelType)
                data = ISERetailer.select().order_by(ISERetailer.LocalTransactionDate.desc()).where(
                    ISERetailer.AcquiringInstitutionIdentification == channel.AcquiringInstitutionIdentification).dicts().iterator()
                records = []

                for rec in data:
                    dicts = {}

                    dicts['TRACE_ID'] = rec['SystemsTraceAuditNumber']
                    dicts['ACQ_RRN'] = rec['RetrievalReferenceNumber']
                    dicts['TOKEN'] = rec['Track2Data'][3:]
                    dicts['MESSAGE_TYPE'] = rec['MessageType']
                    # self.message_type_desc[ rec['MessageType'] ]
                    dicts['MSG_DESC'] = self.message_type_desc.get(
                        rec['MessageType'], '')
                    dicts['TRANSACTION_SOURCE'] = "POS"
                    dicts['TRANSACTION_TYPE'] = rec['ProcessingCode']
                    dicts['TRAN_SUBTYPE'] = self.transaction_type_desc.get(rec['ProcessingCode'], '').get(
                        'sub_type')  # self.transaction_type_desc[ rec['ProcessingCode'] ]
                    dicts['TRAN_DESC'] = self.transaction_type_desc.get(
                        rec['ProcessingCode'], '').get('desc')
                    dicts['TRANSACTION_AMOUNT'] = rec['TransactionAmount']
                    dicts['TRANSACTION_TIME'] = "{} {}".format(
                        rec['LocalTransactionDate'], rec['LocalTransactionTime'])
                    dicts['ENTRY_MODE'] = rec['PointofServiceEntryModeCode']
                    dicts['AUTH_MODE'] = rec['PersonalIdentificationNumberPINData']
                    dicts['TERMINAL_ID'] = rec['CardAcceptorTerminalIdentification']
                    dicts['RETAILER_ID'] = rec['CardAcceptorIdentification']
                    dicts['LOCATION'] = rec['CardAcceptorNameLocation']
                    dicts['RESPONSE_CODE'] = rec['ResponseCode']
                    dicts['RESP_DESC'] = self.response_code_desc.get(
                        rec['ResponseCode'], '')
                    dicts['ACQUIRER_ID'] = rec['AcquiringInstitutionIdentification']
                    dicts['ISSUER_ID'] = rec['ChannelType']
                    dicts['RESPONSE_TIME'] = rec['Token2']
                    dicts['TOTAL_COMMISSIONS'] = rec['TotalCommissions']
                    dicts['TOTAL_TAXES'] = rec['TotalTaxes']
                    dicts['FINAL_AMOUNT'] = rec['FinalAmount']
                    dicts['RULE_DESC'] = rec['Token1'].split('#^#')[0]

                    records.append(dicts)

                # ise_loader("ISE.html", "{}{}.csv".format(report_name,self.today), records, self.cols)
                file_name = "{}_{}_{}.csv".format(
                    channel.AcquiringInstitutionIdentification, report_name, self.today)
                self.create_report(self.path + file_name,
                                   self.specific_cols, sorted(records, key=lambda i: i['TRANSACTION_TIME']))

            print("Acquirer Daily Reports Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
            del records
        except ISERetailer.DoesNotExist as e:
            print('ISERetailer.DoesNotExist - {} Error : {}'.format(report_name, e))
            print("Acquirer Daily Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

        except Exception as e:
            print('{} Error : {}'.format(report_name, e))
            print("Acquirer Daily Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))


    def dailyIssuerReport(self, report_name):

        try:
            channels = IssuerExtractCopy.select(
                IssuerExtractCopy.ForwardingInstitutionIdentification).distinct().iterator()

            for channel in channels:
                # print("channel name",channel.ForwardingInstitutionIdentification)
                data = IssuerExtractCopy.select().order_by(IssuerExtractCopy.LocalTransactionDate.desc()).where(
                    IssuerExtractCopy.ForwardingInstitutionIdentification == channel.ForwardingInstitutionIdentification).dicts().iterator()
                records = []

                for rec in data:
                    dicts = {}

                    dicts['TRACE_ID'] = rec['SystemsTraceAuditNumber']
                    dicts['ACQ_RRN'] = rec['RetrievalReferenceNumber']
                    dicts['TOKEN'] = rec['Track2Data'][3:]
                    dicts['MESSAGE_TYPE'] = rec['MessageType']
                    # self.message_type_desc[ rec['MessageType'] ]
                    dicts['MSG_DESC'] = self.message_type_desc.get(
                        rec['MessageType'], '')
                    dicts['TRANSACTION_SOURCE'] = "POS"
                    dicts['TRANSACTION_TYPE'] = rec['ProcessingCode']
                    dicts['TRAN_SUBTYPE'] = self.transaction_type_desc.get(rec['ProcessingCode'], '').get(
                        'sub_type')  # self.transaction_type_desc[ rec['ProcessingCode'] ]
                    dicts['TRAN_DESC'] = self.transaction_type_desc.get(
                        rec['ProcessingCode'], '').get('desc')
                    dicts['TRANSACTION_AMOUNT'] = rec['TransactionAmount']
                    dicts['TRANSACTION_TIME'] = "{} {}".format(
                        rec['LocalTransactionDate'], rec['LocalTransactionTime'])
                    dicts['ENTRY_MODE'] = rec['PointofServiceEntryModeCode']
                    dicts['AUTH_MODE'] = rec['PersonalIdentificationNumberPINData']
                    dicts['TERMINAL_ID'] = rec['CardAcceptorTerminalIdentification']
                    dicts['RETAILER_ID'] = rec['CardAcceptorIdentification']
                    dicts['LOCATION'] = rec['CardAcceptorNameLocation']
                    dicts['RESPONSE_CODE'] = rec['ResponseCode']
                    dicts['RESP_DESC'] = self.response_code_desc.get(
                        rec['ResponseCode'], '')
                    dicts['ACQUIRER_ID'] = rec['AcquiringInstitutionIdentification']
                    dicts['ISSUER_ID'] = rec['ChannelType']
                    dicts['RESPONSE_TIME'] = rec['Token2']
                    dicts['RULE_DESC'] = rec['Token1'].split('#^#')[0]

                    records.append(dicts)

                # ise_loader("ISE.html", "{}{}.csv".format(report_name,self.today), records, self.cols)
                file_name = "{}_{}_{}.csv".format(
                    channel.ForwardingInstitutionIdentification, report_name, self.today)
                self.create_report(self.path + file_name,
                                   self.specific_cols, sorted(records, key=lambda i: i['TRANSACTION_TIME']))

            print("Issuer Daily Reports Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
            del records
        except IssuerExtractCopy.DoesNotExist as e:
            print('IssuerExtractCopy.DoesNotExist - {} Error : {}'.format(report_name, e))
            print("Issuer Daily Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except Exception as e:
            print('{} Error : {}'.format(report_name, e))
            print("Issuer Daily Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))


    def monthlyAcquirerReport(self, report_name, first_date, last_date):
        # first_date = self.first_date_of_month(first_date)
        # last_date = self.last_date_of_month(last_date)

        first_date = datetime.strptime(first_date, "%Y-%m-%d")
        last_date = datetime.strptime(last_date, "%Y-%m-%d")
        # print("monthly")
        print("first_date", first_date)
        print("last_date", last_date)
        try:
            channels = TransactionHistory.select(TransactionHistory.AcquiringInstitutionIdentification).where(TransactionHistory.LocalTransactionDate.between(
                first_date, last_date)).distinct().iterator()

            for channel in channels:
                print("channel name", channel.AcquiringInstitutionIdentification)
                data = TransactionHistory.select().where(TransactionHistory.LocalTransactionDate.between(
                    first_date, last_date), TransactionHistory.AcquiringInstitutionIdentification == channel.AcquiringInstitutionIdentification).order_by(TransactionHistory.LocalTransactionDate.desc()).dicts().iterator()
                records = []

                for rec in data:
                    # print(rec['LocalTransactionDate'])
                    dicts = {}

                    dicts['TRACE_ID'] = rec['SystemsTraceAuditNumber']
                    dicts['ACQ_RRN'] = rec['RetrievalReferenceNumber']
                    dicts['TOKEN'] = rec['Track2Data'][3:]
                    dicts['MESSAGE_TYPE'] = rec['MessageType']
                    # self.message_type_desc[ rec['MessageType'] ]
                    dicts['MSG_DESC'] = self.message_type_desc.get(
                        rec['MessageType'], '')
                    dicts['TRANSACTION_SOURCE'] = "POS"
                    dicts['TRANSACTION_TYPE'] = rec['ProcessingCode']
                    dicts['TRAN_SUBTYPE'] = self.transaction_type_desc.get(rec['ProcessingCode'], '').get(
                        'sub_type')  # self.transaction_type_desc[ rec['ProcessingCode'] ]
                    dicts['TRAN_DESC'] = self.transaction_type_desc.get(
                        rec['ProcessingCode'], '').get('desc')
                    dicts['TRANSACTION_AMOUNT'] = rec['TransactionAmount']
                    dicts['TRANSACTION_TIME'] = "{} {}".format(
                        rec['LocalTransactionDate'], rec['LocalTransactionTime'])
                    dicts['ENTRY_MODE'] = rec['PointofServiceEntryModeCode']
                    dicts['AUTH_MODE'] = rec['PersonalIdentificationNumberPINData']
                    dicts['TERMINAL_ID'] = rec['CardAcceptorTerminalIdentification']
                    dicts['RETAILER_ID'] = rec['CardAcceptorIdentification']
                    dicts['LOCATION'] = rec['CardAcceptorNameLocation']
                    dicts['RESPONSE_CODE'] = rec['ResponseCode']
                    dicts['RESP_DESC'] = self.response_code_desc.get(
                        rec['ResponseCode'], '')
                    dicts['ACQUIRER_ID'] = rec['AcquiringInstitutionIdentification']
                    dicts['ISSUER_ID'] = rec['ChannelType']
                    dicts['RESPONSE_TIME'] = rec['Token2']
                    dicts['TOTAL_COMMISSIONS'] = rec['TotalCommissions']
                    dicts['TOTAL_TAXES'] = rec['TotalTaxes']
                    dicts['FINAL_AMOUNT'] = rec['FinalAmount']
                    dicts['RULE_DESC'] = rec['Token1'].split('#^#')[0]

                    records.append(dicts)

                # ise_loader("ISE.html", "{}{}.csv".format(report_name,self.today), records, self.cols)
                file_name = "{}_{}_{}.csv".format(
                    channel.AcquiringInstitutionIdentification, report_name, self.today)
                self.create_report(self.path + file_name,
                                   self.specific_cols, sorted(records, key=lambda i: i['TRANSACTION_TIME']))

            # del records
        except TransactionHistory.DoesNotExist as e:
            print(
                'TransactionHistory.DoesNotExist - {} Error : {}'.format(report_name, e))
        except Exception as e:
            print('{} Error : {}'.format(report_name, e))


    def monthlyIssuerReport(self, report_name, first_date, last_date):
        # first_date = self.first_date_of_month(first_date)
        # last_date = self.last_date_of_month(last_date)

        first_date = datetime.strptime(first_date, "%Y-%m-%d")
        last_date = datetime.strptime(last_date, "%Y-%m-%d")
        # print("monthly")
        print("first_date", first_date)
        print("last_date", last_date)
        try:
            channels = TransactionHistoryIssuer.select(TransactionHistoryIssuer.ForwardingInstitutionIdentification).where(TransactionHistoryIssuer.LocalTransactionDate.between(
                first_date, last_date)).distinct().iterator()

            for channel in channels:
                print("channel name", channel.ForwardingInstitutionIdentification)
                data = TransactionHistoryIssuer.select().where(TransactionHistoryIssuer.LocalTransactionDate.between(
                    first_date, last_date), TransactionHistoryIssuer.ForwardingInstitutionIdentification == channel.ForwardingInstitutionIdentification).order_by(TransactionHistoryIssuer.LocalTransactionDate.desc()).dicts().iterator()
                records = []

                for rec in data:
                    # print(rec['LocalTransactionDate'])
                    dicts = {}

                    dicts['TRACE_ID'] = rec['SystemsTraceAuditNumber']
                    dicts['ACQ_RRN'] = rec['RetrievalReferenceNumber']
                    dicts['TOKEN'] = rec['Track2Data'][3:]
                    dicts['MESSAGE_TYPE'] = rec['MessageType']
                    # self.message_type_desc[ rec['MessageType'] ]
                    dicts['MSG_DESC'] = self.message_type_desc.get(
                        rec['MessageType'], '')
                    dicts['TRANSACTION_SOURCE'] = "POS"
                    dicts['TRANSACTION_TYPE'] = rec['ProcessingCode']
                    dicts['TRAN_SUBTYPE'] = self.transaction_type_desc.get(rec['ProcessingCode'], '').get(
                        'sub_type')  # self.transaction_type_desc[ rec['ProcessingCode'] ]
                    dicts['TRAN_DESC'] = self.transaction_type_desc.get(
                        rec['ProcessingCode'], '').get('desc')
                    dicts['TRANSACTION_AMOUNT'] = rec['TransactionAmount']
                    dicts['TRANSACTION_TIME'] = "{} {}".format(
                        rec['LocalTransactionDate'], rec['LocalTransactionTime'])
                    dicts['ENTRY_MODE'] = rec['PointofServiceEntryModeCode']
                    dicts['AUTH_MODE'] = rec['PersonalIdentificationNumberPINData']
                    dicts['TERMINAL_ID'] = rec['CardAcceptorTerminalIdentification']
                    dicts['RETAILER_ID'] = rec['CardAcceptorIdentification']
                    dicts['LOCATION'] = rec['CardAcceptorNameLocation']
                    dicts['RESPONSE_CODE'] = rec['ResponseCode']
                    dicts['RESP_DESC'] = self.response_code_desc.get(
                        rec['ResponseCode'], '')
                    dicts['ACQUIRER_ID'] = rec['AcquiringInstitutionIdentification']
                    dicts['ISSUER_ID'] = rec['ChannelType']
                    dicts['RESPONSE_TIME'] = rec['Token2']
                    dicts['RULE_DESC'] = rec['Token1'].split('#^#')[0]

                    records.append(dicts)

                # ise_loader("ISE.html", "{}{}.csv".format(report_name,self.today), records, self.cols)
                file_name = "{}_{}_{}.csv".format(
                    channel.ForwardingInstitutionIdentification, report_name, self.today)
                self.create_report(self.path + file_name,
                                   self.specific_cols, sorted(records, key=lambda i: i['TRANSACTION_TIME']))

            # del records
        except TransactionHistoryIssuer.DoesNotExist as e:
            print(
                'TransactionHistoryIssuer.DoesNotExist - {} Error : {}'.format(report_name, e))
        except Exception as e:
            print('{} Error : {}'.format(report_name, e))


    def create_report(self, file_name, list_of_columns, dict_of_data):
        try:
            with open(file_name, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=list_of_columns)
                writer.writeheader()
                writer.writerows(list(dict_of_data))
                """for data in list(dict_of_data):
                print(data)
                    writer.writerow(data)"""
        except IOError as e:
            print('I/O Error : {}'.format(e))
        except Exception as e:
            print('Error : {}'.format(e))


    def last_date_of_month(self, date):
        return date.replace(day=calendar.monthrange(date.year, date.month)[1])


    def first_date_of_month(self, date):
        return date.replace(day=1)


    def acq_RevSucPurDec(self, report_name):
        """
        * Mantis 728 Specific :-
        Generate report for AcquirerReversalSuccessPurchaceDecline txns
        """ 

        try:
            getData = """
            SELECT
            MessageType, ProcessingCode, ResponseCode, Track2Data, RetrievalReferenceNumber,
            ChannelType,SystemsTraceAuditNumber,CardAcceptorIdentification,
            LocalTransactionDate, LocalTransactionTime, TransactionAmount
            FROM
            acquirerreversalsuccesspurchacedecline;
            """
            df = read_sql_query(getData, con=engine)
            if not df.empty:
                df.to_csv(f"{self.path}{report_name}_{self.today}.csv")
                print("AcquirerReversalSuccessPurchaceDecline Reports  Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
            else:
                print(f"AcquirerReversalSuccessPurchaceDecline Empty, Report Not Generated at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
        except AcquirerReversalSuccessPurchaceDecline.DoesNotExist as e:
            print('AcquirerReversalSuccessPurchaceDecline.DoesNotExist - {} Error : {}'.format(report_name, e))
            print("AcquirerReversalSuccessPurchaceDecline Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        except Exception as e:
            print('{} Error : {}'.format(report_name, e))
            print("AcquirerReversalSuccessPurchaceDecline Reports Not Generated at {}".format(
                datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))


if __name__ == '__main__':
    pass
    # start = argv[1]
    # end = argv[2]
    # create_report = RetailerReports('./CompensationReports/MonthlyReports/Aug_2022/')
    # create_report.monthlyAcquirerReport("Acquirer_Monthly_Report", start, end)
    # create_report.monthlyIssuerReport("Issuer_Monthly_Report", start, end)
