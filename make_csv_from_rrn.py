import os
import shutil
from model import *
import pandas as pd
from datetime import datetime
from utils import search_files

input_rrn_file_name = "RRN_LIST_"
input_rrn_file_loc = "./RRNFiles/InputFiles/"
output_rrn_file_loc = f"./RRNFiles/OutputExtracts/{datetime.now().strftime(r'%b_%Y')}/"
processed_rnn_file_loc = f"./RRNFiles/ProcessedFiles/{datetime.now().strftime(r'%b_%Y')}"


def make_extract():
    try:
        searched_files = search_files(input_rrn_file_loc, input_rrn_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
                input_file_path = rec['link']
                rrn_to_search = pd.read_csv(f"{rec['link']}", dtype=str)
                tuple_of_rrn_to_serach = tuple(set(rrn_to_search['RRN']))

            if len(tuple_of_rrn_to_serach) == 1:
                query = f"""
                        SELECT MessageType,PrimaryBitMap,SecondaryBitMap,PrimaryAccountNumberPAN,ProcessingCode,TransactionAmount,TransactionAmountCardholderBilling,
                        TransmissionDateandTime,ConversionRateCardholderBilling,SystemsTraceAuditNumber,LocalTransactionTime,LocalTransactionDate,ExpirationDate,SettlementDate,
                        CaptureDate,MerchantTypeCode,AcquirerInstitutionCountryCode,IssuerInstututionCountryCode,ForwardingInstitutionCountryCode,PointofServiceEntryModeCode,
                        CardSequenceNumber,"CV" as NetworkInternationalIdentifierCode,PointofServiceConditionCode,AcquiringInstitutionIdentification,ForwardingInstitutionIdentification,
                        Track2Data,RetrievalReferenceNumber,AuthorizationIdentificationResponse,ResponseCode,CardAcceptorTerminalIdentification,CardAcceptorIdentification,
                        CardAcceptorNameLocation,Track1Data,RetailerData,TransactionCurrencyCode,CurrencyCodeCardholderBilling,PersonalIdentificationNumberPINData,AdditionalAmount,
                        IntegratedCircuitCardICC,CardholdersIdentificationNumberandName,AdditionalAmounts,TerminalData,CardData,TerminalPostalCode,Token1,Token2,Token3,
                        PrimaryMessageAuthenticationCodeMAC,ChannelType,CardType
                        FROM transactionhistory WHERE MessageType = '0210' and ProcessingCode = '000000' and RetrievalReferenceNumber IN 
                        ('{tuple_of_rrn_to_serach[0]}');
                        """
                # print(f"Single Tuple Query = {query}")
            else:
                query = f"""
                        SELECT MessageType,PrimaryBitMap,SecondaryBitMap,PrimaryAccountNumberPAN,ProcessingCode,TransactionAmount,TransactionAmountCardholderBilling,
                        TransmissionDateandTime,ConversionRateCardholderBilling,SystemsTraceAuditNumber,LocalTransactionTime,LocalTransactionDate,ExpirationDate,SettlementDate,
                        CaptureDate,MerchantTypeCode,AcquirerInstitutionCountryCode,IssuerInstututionCountryCode,ForwardingInstitutionCountryCode,PointofServiceEntryModeCode,
                        CardSequenceNumber,"CV" as NetworkInternationalIdentifierCode,PointofServiceConditionCode,AcquiringInstitutionIdentification,ForwardingInstitutionIdentification,
                        Track2Data,RetrievalReferenceNumber,AuthorizationIdentificationResponse,ResponseCode,CardAcceptorTerminalIdentification,CardAcceptorIdentification,
                        CardAcceptorNameLocation,Track1Data,RetailerData,TransactionCurrencyCode,CurrencyCodeCardholderBilling,PersonalIdentificationNumberPINData,AdditionalAmount,
                        IntegratedCircuitCardICC,CardholdersIdentificationNumberandName,AdditionalAmounts,TerminalData,CardData,TerminalPostalCode,Token1,Token2,Token3,
                        PrimaryMessageAuthenticationCodeMAC,ChannelType,CardType
                        FROM transactionhistory WHERE MessageType = '0210' and ProcessingCode = '000000' and RetrievalReferenceNumber IN 
                        {tuple_of_rrn_to_serach};
                        """
                # print(f"Multiple Tuple Query = {query}")

        file_path = f"{output_rrn_file_loc}RRN_To_Extract_{datetime.now().strftime(r'%y%m%d')}.txt"
        data = pd.read_sql(query, con=myDB, index_col=None)
        print(data)
        TransactionAmount_to_int = [int(tti) for tti in data['TransactionAmount'].tolist()]
        LocalTransactionTime_remove_days = [str(lttrd).replace("0 days", "").replace(" ", "") for lttrd in data['LocalTransactionTime'].tolist()]
        data['TransactionAmount'] = TransactionAmount_to_int
        data['LocalTransactionTime'] = LocalTransactionTime_remove_days
        data.to_csv(file_path, index=False)
        shutil.move(input_file_path, processed_rnn_file_loc)
        return True, file_path

    except Exception as err:
        print(f"Error In Making Extract From RRN = {err}")
        return False, err


if __name__ == "__main__":
    make_extract()
    pass
