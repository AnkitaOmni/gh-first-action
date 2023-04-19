import os
import glob
import shutil
import queries
import validations
import collections
from model import *
from utils import *
from sys import argv
from reports import *
import subprocess as sp
from config import Config
from conciliation import *
from file_transfer import *
from compress_files import *
import multiprocessing as mp
from peewee import fn, chunked
from settlement_report import *
from datetime import datetime, date
from retailer_daily_monthly_report import *
from liquidation import liquidate_transaction
from jinja2 import Environment, FileSystemLoader
from sendmail_alerts import sendmail_with_html_and_attachment
from load_extract_file import extract_input_file, remove_duplicate
from daily_trx_credit_report import bank_deposit_trx_daily_details



config = Config().get_config_json()
ENV = f"{config['ENV_NAME']}"
extract_file_name = "OMNIEXTRACT_REPORT_"


# * CC0024 Specific : -Acquirer File Full Day Locations
acquirer_fullday_input_extract_loc = "./AcquirerExtractFullDay/InputExtracts/"
acquirer_fullday_processed_extract_loc = f"./AcquirerExtractFullDay/ProcessedExtracts/{datetime.now().strftime(r'%b_%Y')}/"
fullday_extract_file_name = "OMNIEXTRACT_REPORT_"

# * Acquire File Locations
acquirer_input_extract_loc = "./AcquirerExtract/InputExtracts/"
acquirer_processed_extract_loc = f"./AcquirerExtract/ProcessedExtracts/{datetime.now().strftime(r'%b_%Y')}/"

# * Issuer File Locations
issuer_input_extract_loc = "./IssuerExtract/InputExtracts/"
issuer_processed_extract_loc = f"./IssuerExtract/ProcessedExtracts/{datetime.now().strftime(r'%b_%Y')}/"

# * RetailerReports & ZipFile (Local Machine)
retailer_report_loc = f"./CompensationReports/RetailerReports/{datetime.now().strftime(r'%b_%Y')}/"
zip_directory_loc = f"./CompensationReports/ZipRetailerReports/{datetime.now().strftime(r'%Y')}/{datetime.now().strftime(r'%b_%Y')}/"
concillation_report_loc = f"./CompensationReports/ConciliationReports/"

# * ZipRetailerReports & DailyReport Backup Location (REMOTE)
zip_backup_loc = f'/comp_repo/{datetime.now().strftime(r"%b_%Y")}/{datetime.now().strftime(r"%d-%b-%y")}/'
zip_Columbiabk_loc = f'/home/compsan_bk/comp_repo/{datetime.now().strftime(r"%b_%Y")}/{datetime.now().strftime(r"%d-%b-%y")}/'
zip_backup_loc_old_machine = f'/comp_repo/{datetime.now().strftime(r"%b_%Y")}/{datetime.now().strftime(r"%d-%b-%y")}/'


# * Data & Time Stamp For Liquidation Process
current_date_format_1 = datetime.now().strftime(r"%y%m%d")  # today's date format YYMMDD eg. 211208
current_date_format_2 = datetime.today().strftime(r'%y-%m-%d')   # today's date format YY-MM-DD eg. 21-12-08
month_dir = f'{datetime.now().strftime(r"%b_%Y")}'




def ise_loader(temp_name, filename, data, cols):
    dates = datetime.now().strftime("%Y%m%d")
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(temp_name)
    upper_cols = map(lambda x: x.upper(), cols)
    with open("CompensationReports/RetailerReports/"+filename, 'w') as f:
        f.write(template.render(records=data, dates=dates, cols=cols, upper_cols=upper_cols))


def retailer_loader(temp_name, path, filename, header, data, tailer):
    dates = datetime.now().strftime("%Y%m%d")
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(temp_name)
    with open(path + filename, 'w') as f:
        f.write(template.render(records=data, dates=dates,header=header, tailer=tailer))


def copy_to_txn_history():
    myDB.execute_sql("""truncate table iseretailercopy;""")
    myDB.execute_sql("""truncate table update_th_iseretailer;""")

    myDB.execute_sql(queries.makeIseretailerCopy)
    update_count = ISERetailerCopy.select(fn.COUNT(ISERetailerCopy.RetrievalReferenceNumber)).join(
        TransactionHistory,
        on=(
            (ISERetailerCopy.RetrievalReferenceNumber == TransactionHistory.RetrievalReferenceNumber) &
            (ISERetailerCopy.TransmissionDateandTime == TransactionHistory.TransmissionDateandTime) &
            (ISERetailerCopy.Track2Data == TransactionHistory.Track2Data) &
            (ISERetailerCopy.MessageType == TransactionHistory.MessageType) &
            (ISERetailerCopy.ProcessingCode == TransactionHistory.ProcessingCode) &
            (ISERetailerCopy.ResponseCode == TransactionHistory.ResponseCode) &
            (ISERetailerCopy.CardAcceptorIdentification == TransactionHistory.CardAcceptorIdentification)
        )
    ).count()
    # print("Update Count = ", update_count)

    if update_count == None:

        # * INSERT ALL UNIQUE/NEW VALUES TO TH
        myDB.execute_sql(queries.insertIgnoreToTransactionHistory)

    else:

        # * INSERT Common Transactions to Update_TH_ISERetailer - INNER JOIN ON ISERetailerCopy && TransactionHistory
        myDB.execute_sql(queries.insertToUpdate_TH_ISERetailer)
        # * DELETE Common FROM ISERetailerCopy - INNER JOIN ON ISERetailerCopy && TransactionHistory
        myDB.execute_sql(queries.deleteCommonTrnx)
        # * INSERT ALL UnCommon Transactions From ISERetailerCopy TO TH
        myDB.execute_sql(queries.insertToTHAfterInner)
        # * BULK UPDATE TH
        myDB.execute_sql(queries.updateTH)

    return update_count


def upload_extract_file(input_loc, output_loc, extract_file_name, original_table, duplicate_table, pick_date='today'):
    
    try:
        # * function call to search latest files (abs_dir_path, file_name_to_search)
        searched_files = search_files(input_loc, extract_file_name)

        if len(searched_files) > 0:
            totalfilecount=0
            for file in searched_files:

                # * Filter :- Today / WeekDay / All
                goAhead = False
                if pick_date == 'today':
                    if datetime.now().strftime(r'%y%m%d') in file['file_name']: 
                        goAhead = True
                        totalfilecount+=1
                       
                elif pick_date == 'weekend':
                    newDate = datetime.strptime(file['file_name'][-10::1].replace('.txt', '')[:6].strip(), r'%y%m%d').strftime(r'%Y-%m-%d')
                    weekDay = date(int(newDate.split('-')[0]), int(newDate.split('-')[1]), int(newDate.split('-')[2])).weekday()
                    if f"_{datetime.now().strftime(r'%y%m').strip()}" in file['file_name'] and (weekDay == 5 or weekDay == 6):
                        goAhead = True
                        totalfilecount+=1
                    
                elif pick_date == 'all': 
                    goAhead = True  
                    totalfilecount+=1
                
                # * File Upload
                if goAhead:
                    try:
                        extract_input_file(file['absolute_file_name'], original_table)
                    except Exception as e:
                        print(f"Upload File Failed - {file['file_name']} ", e)
                        return False

                    try:
                        # * File Moving
                        shutil.move(file['absolute_file_name'], output_loc)
                        print(f"File Uploaded And Copied To BackUp - {file['file_name']}")

                    except shutil.Error:
                        print(f"File Uploaded, But Not Copied To BackUp, File Already Present - {file['file_name']}")
                        #print(f"Final = {file['file_name']} | {file['absolute_file_name']}")

            if totalfilecount < 1: 
                    print(f"No {pick_date}'s Extract File Present - Upload File Failed")
                    for file in searched_files:
                        print(f"Old file - {file['file_name']}")
                    return False

            remove_duplicate(original_table, duplicate_table)
            print(f"Upload File Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
            return True

        else:
            print("No Extract File Present - Upload File Failed ")
            print(f"Upload File Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
            return False

    except Exception as e1:
        print("Upload File Failed :- ", e1)
        print(f"Upload File Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
        return False


def fullDayLiquidation():

    """
    * CC0024 Specific :-
    For loading Full Day extract files with full day transactions
    """

    declineTrnxs, retailer, mem_account = [], [], dict()

    for acc in RetailerAccount.select().dicts().iterator():
        mem_account[acc["EntityId"], acc["RetailerId"]] = acc

    # * Decline Trnxs Only
    for eachTrnx in FullDayAcquirerExtract.select().where(FullDayAcquirerExtract.ResponseCode != "00").dicts().iterator():
        del eachTrnx["id"]
        eachTrnx["FinalAmount"] = eachTrnx["TransactionAmount"]
        declineTrnxs.append(eachTrnx)

    with myDB.atomic():
        for batch in chunked(declineTrnxs, 1000):
            CurrentDateTransactionHistory.insert_many(batch).execute()

    # * Success Trnxs Only        
    for txn in FullDayAcquirerExtract.select().where(FullDayAcquirerExtract.ResponseCode == "00").iterator():
        try: retailer.append(liquidate_transaction(single_txn = txn, ret_account_dict = mem_account))
        except Exception as e: raise

    del mem_account  

    try:
        if len(retailer) > 0:
          with myDB.atomic():
              for batch in chunked(retailer, 1000):
                  CurrentDateTransactionHistory.insert_many(batch).execute()
        del retailer
    except Exception as e:
      print(f"Error Inserting Records In CurrentDateTransactionHistory - {str(e)}")


def base_liquidation():

    declineTrnxs, retailer, mem_account = [], [], dict()

    for acc in RetailerAccount.select().dicts().iterator():
        mem_account[acc["EntityId"], acc["RetailerId"]] = acc

    # * Decline Trnxs Only
    for eachTrnx in AcquirerExtract.select().where(AcquirerExtract.ResponseCode != "00").dicts().iterator():
        del eachTrnx["id"]
        eachTrnx["FinalAmount"] = eachTrnx["TransactionAmount"]
        declineTrnxs.append(eachTrnx)
    with myDB.atomic():
        for batch in chunked(declineTrnxs, 1000):
            ISERetailer.insert_many(batch).execute()
    
    # * Success Trnxs Only
    for txn in AcquirerExtract.select().where(AcquirerExtract.ResponseCode == "00").iterator():
        try: retailer.append(liquidate_transaction(single_txn = txn, ret_account_dict = mem_account))
        except Exception as e: raise

    del mem_account  

    try:
        if len(retailer) > 0:
            with myDB.atomic():
                for batch in chunked(retailer, 1000):
                    ISERetailer.insert_many(batch).execute()
        del retailer
    except Exception as e:
        print(f"Error Inserting Records In ISERetailer - {str(e)}")


def liquidation_reports():

    i = ISERetailer.select(ISERetailer.AcquiringInstitutionIdentification, ISERetailer.CardAcceptorIdentification, ISERetailer.CardAcceptorTerminalIdentification,
                           ISERetailer.MerchantTypeCode, ISERetailer.MessageType, ISERetailer.ResponseCode, ISERetailer.ProcessingCode, ISERetailer.LocalTransactionTime,
                           ISERetailer.LocalTransactionDate, ISERetailer.SettlementDate, ISERetailer.Track2Data, ISERetailer.SystemsTraceAuditNumber, 
                           ISERetailer.RetrievalReferenceNumber, ISERetailer.CardAcceptorNameLocation, ISERetailer.ChannelType, ISERetailer.CardType, 
                           ISERetailer.TransactionAmount, ISERetailer.RetCardTypeCommision, ISERetailer.RetMccCommision, ISERetailer.RetBinCommision, 
                           ISERetailer.RetTxnIdentifierCommision, ISERetailer.Retailer, ISERetailer.Acquirer, ISERetailer.Issuer, ISERetailer.TotalCommissions, 
                           ISERetailer.Retefuente, ISERetailer.Reteica, ISERetailer.Cree, ISERetailer.Reteiva, ISERetailer.TotalTaxes, ISERetailer.TotalDiscounts, 
                           ISERetailer.FinalAmount).where(ISERetailer.ResponseCode == '00').dicts()

    cols = ['AcquiringInstitutionIdentification', 'CardAcceptorIdentification', 'CardAcceptorTerminalIdentification', 'MerchantTypeCode', 'MessageType', 'ResponseCode',
            'ProcessingCode', 'LocalTransactionTime', 'LocalTransactionDate', 'SettlementDate', 'Track2Data', 'SystemsTraceAuditNumber', 'RetrievalReferenceNumber',
            'CardAcceptorNameLocation', 'ChannelType', 'CardType', 'TransactionAmount', 'RetCardTypeCommision', 'RetMccCommision', 'RetBinCommision',
            'RetTxnIdentifierCommision', 'Retailer', 'Acquirer', 'Issuer', 'TotalCommissions', 'Retefuente', 'Reteica', 'Cree', 'Reteiva', 'TotalTaxes',
            'TotalDiscounts', 'FinalAmount']

    ise_loader("ISE.html", f"Retailer{current_date_format_1}.csv", list(i), cols)


def liquidation_summary_reports():
    i = ISERetailer.select(ISERetailer.AcquiringInstitutionIdentification.alias('ACQ_INST_ID'),
                           ISERetailer.CardAcceptorIdentification.alias('RETAILER_ID'),
                           fn.COUNT(ISERetailer.CardAcceptorIdentification).alias('TOTAL_TXN_CNT'),
                           ISERetailer.MessageType.alias('MESSAGE_TYPE'),
                           ISERetailer.ProcessingCode.alias('PROCESSING_CODE'),
                           fn.SUM(ISERetailer.TransactionAmount).alias('TOTAL_AMOUNT'),
                           fn.SUM(ISERetailer.TotalCommissions).alias('TOTAL_COMMISSION'),
                           fn.SUM(ISERetailer.TotalTaxes).alias('TOTAL_TAX'),
                           fn.SUM(ISERetailer.TotalDiscounts).alias('TOTAL_DISCOUNT'),
                           fn.SUM(ISERetailer.FinalAmount).alias('FINAL_AMOUNT')).where(ISERetailer.ResponseCode == '00').group_by(
        ISERetailer.AcquiringInstitutionIdentification,
        ISERetailer.CardAcceptorIdentification,
        ISERetailer.MessageType,
        ISERetailer.ProcessingCode).dicts()

    cols = ['ACQ_INST_ID', 'RETAILER_ID', 'TOTAL_TXN_CNT', 'MESSAGE_TYPE', 'PROCESSING_CODE', 'TOTAL_AMOUNT',
            'TOTAL_COMMISSION', 'TOTAL_TAX', 'TOTAL_DISCOUNT', 'FINAL_AMOUNT']
    ise_loader("ISE.html", f"RetailerSummary{current_date_format_1}.csv", list(i), cols)


def bech_liquidation_retailer_reports(path):
    '''
    retailer wise report for bech 
    predefined record length which includes header body and trailer
    '''

    for inst in InstitutionId.select().dicts().iterator():
        for ret in RetailerId.select().dicts().iterator():
            if inst["channel_type"] == 0:
                if inst["institution_id_code"] == ret['EntityId']:
                    try:
                        RetailerStatusData = (ConfigurationCatalogs
                                              .select()
                                              .where(
                                                  ConfigurationCatalogs.catalog_name == 'RetailerStatusData',
                                                  ConfigurationCatalogs.code == ret['StatusCode']
                                              ).get())
                        ret_status = RetailerStatusData.description
                    except ConfigurationCatalogs.DoesNotExist:
                        ret_status = "NoStatus"

                    header_output = prepare_header(ret['EntityId'], ret['RetailerId'], ret['IdentificationNumber'])
                    body_output = prepare_body(ret['EntityId'], ret['RetailerId'])
                    trailer_output = prepare_trailer(ret['EntityId'], ret['RetailerId'])

                    retailer_loader("retailer_reports.html", path,
                                    f"{ret['EntityId']}_{ret['RetailerId']}_{ret_status}_DAILY_TXN_DETAILS_{current_date_format_1}.txt",
                                    header_output, list(body_output), trailer_output)


def prepare_header(institution_id, retailer_id, tax_id):
    '''
    header preparation for retailer wise reports
    '''
    today1 = datetime.now().strftime("%Y%m%d")
    header = collections.OrderedDict()

    try:
        ise_ret_rec = ISERetailer.select().where(ISERetailer.AcquiringInstitutionIdentification ==
                                                 institution_id, ISERetailer.CardAcceptorIdentification == retailer_id).get()
        common_channel = ise_ret_rec.ChannelType
        #print("try common channel",common_channel)
    except ISERetailer.DoesNotExist:
        if institution_id == '0012' or institution_id == '0014':
            common_channel = "GPGMVP"
        else:
            common_channel = 'DA'
        #print("except common channel",common_channel)

    # servic = 'ADQPRESEN' if common_channel == 'GPGMVP' else 'ADQDIGITAL'
    if common_channel == 'GPGMVP' or common_channel == 'ALVI':
        servic = 'ADQPRESEN'
    else:
        servic = 'ADQDIGITAL'
        
        
    if '-' in tax_id:
        tax_id_1,tax_id_2 = tax_id.split("-")
    else:
        tax_id_1,tax_id_2 = tax_id,''

    header["ENC-TIP-REG"] = '01'  # length 2
    header["ENC-FEC-REND"] = today1  # length 8 YYYYMMDD - int
    # length 10 "ADQ DIGITAL" or "ADQ PRESEN"
    header["ENC-GLO-SERVIC"] = servic.ljust(10, ' ')
    # length 9 TAXID - int
    header["Codigo-empresa-RUT"] = tax_id_1.rjust(9, '0')
    header["Digito-Verificador"] = tax_id_2.ljust(1, ' ') #chk_digit_tax_id.ljust(1,' ')      #length 1

    return header


def prepare_body(institution_id, retailer_id):
    '''
    body preparation for retailer wise reports
    '''
    body = []

    ise_ret_rec = ISERetailer.select().where(ISERetailer.AcquiringInstitutionIdentification ==
                                             institution_id, ISERetailer.CardAcceptorIdentification == retailer_id)

    #ise_ret_cols = ["D21-TIP-REG","D21-MASKED-PAN","D21-RUT-COMPRA","D21-DIG-COMPRA","D21-ID-COMPRA","D21-GLO-ID-COMPRA","D21-FEC-VEN","D21-ESTADO-PAG","D21-TX-BANCO","D21-FEC-OPE","D21-HOR-OPE","D21-FEC-CONTA","D21-RUT-CUENTA","D21-DIG-CUENTA","D21-CONVENIO","D21-MTO-PAGO-DET", "CANAL","TIPO-MEDIO-DE-PAGO","MEDIO-DE-PAGO","N-DE-LA-CUENTA","CANTIDAD-DE-CUOTAS"]

    for r in ise_ret_rec.iterator():
        """
        1.Purchase Txn -MVP
                -National		COMPRA		1-10 ""COMPRA"", 11.22 Merchant Name, blank filled	
                -International 	COMPRA
        2.Ecommerce Txn -DA
            -if domain_code of BIN =1 
                then National         WEB 1-10 "WEB",11-22 MerchantName,blank filled
            -if domain_code of BIN =2 
                then International    COMPRA-INT  1-10 ""COMPRA INT "",11 is a blank, 12-19 ""Nombre Comercio""  20 "" "". 21-22 ""Country Code"", blank filled.

        """
        #domain_code = 1
        if r.ChannelType == "GPGMVP":
            glo_id = 'COMPRA'.ljust(10, ' ') + r.CardAcceptorNameLocation[:11].ljust(12, ' ') + ''.ljust(8, ' ')
        elif r.ChannelType == "DA":

            if r.PrimaryMessageAuthenticationCodeMAC == "I":
                glo_id = 'COMPRA INT'.ljust(10, ' ') + ''.ljust(1, ' ') + r.CardAcceptorNameLocation[:7].ljust(
                    8, ' ') + ''.ljust(1, ' ') + r.CardAcceptorNameLocation[-2:].ljust(2, ' ') + ''.ljust(8, ' ')  # last position of 2 will be country code
            elif r.PrimaryMessageAuthenticationCodeMAC == "D":
                glo_id = 'WEB'.ljust(10, ' ') + r.CardAcceptorNameLocation[:11].ljust(12, ' ') + ''.ljust(8, ' ')
            else:
                glo_id = ''.ljust(10, ' ') + r.CardAcceptorNameLocation[:11].ljust(12, ' ') + ''.ljust(8, ' ')
        else:
            glo_id = 'COMPRA'.ljust(10, ' ') + r.CardAcceptorNameLocation[:11].ljust(12, ' ') + ''.ljust(8, ' ')

        txn_date = r.LocalTransactionDate.strftime("%Y%m%d")
        txn_time = r.LocalTransactionTime.strftime('%H%M%S')
        msg_and_proc_code = r.MessageType[1:3] + r.ProcessingCode[:2]

        record = collections.OrderedDict()
        record["D21-TIP-REG"] = '02'  # length 2
        # length 19 PAN
        record["D21-MASKED-PAN"] = r.Track2Data[3:].rjust(19, '0')
        # length 9 National ID - int
        record["D21-RUT-COMPRA"] = ''.rjust(9, '0')
        # length 1 TAXID - int need to add feld
        record["D21-DIG-COMPRA"] = ''.ljust(1, ' ')
        # length 12
        record["D21-ID-COMPRA"] = r.RetrievalReferenceNumber.rjust(12, '0')
        # length 7
        record["D21-TX-BANCO"] = r.SystemsTraceAuditNumber.rjust(7, '0')
        # length 28 new field
        record["D21-ORDEN-DE-COMPRA"] = r.CardholdersIdentificationNumberandName.rjust(
            28, '0')
        record["D21-MTI"] = msg_and_proc_code.rjust(4, '0')  # length 4
        record["D21-GLO-ID-COMPRA"] = glo_id  # length 30
        # length 8 Installment due date - int
        record["D21-FEC-VEN"] = ''.rjust(8, '0')
        # length 3 B39.Auth-Res-Code
        record["D21-ESTADO-PAG"] = r.ResponseCode.ljust(3, ' ')
        # record["D21-TX-BANCO"]    = r.SystemsTraceAuditNumber.rjust(7,'0')      #length 7
        record["D21-FEC-OPE"] = txn_date.rjust(8, '0')  # length 8
        record["D21-HOR-OPE"] = txn_time.rjust(6, '0')  # length 6
        record["D21-FEC-CONTA"] = ''.ljust(8, ' ')  # length 8
        record["D21-RUT-CUENTA"] = ''.rjust(9, '0')  # length 9
        record["D21-DIG-CUENTA"] = ''.ljust(1, ' ')  # length 1
        # length 11
        record["D21-CONVENIO"] = r.CardAcceptorTerminalIdentification.rjust(
            11, '0')
        # length 13
        record["D21-MTO-PAGO-DET"] = str(r.TransactionAmount).rjust(13, '0')
        # length 13
        record["D21-Transaction-Fee"] = str(r.Retailer).rjust(13, '0')
        # length 13
        record["D21-Total-Amount"] = str(r.FinalAmount).rjust(13, '0')
        # length 30  need to add feld channel type
        record["CANAL"] = r.ChannelType.ljust(30, ' ')
        # length 8  need to add feld credit or debit
        record["TIPO-MEDIO-DE-PAGO"] = r.CardType.ljust(8, ' ')
        record["MEDIO-DE-PAGO"] = ''.rjust(15, '0')  # length 15
        record["N-DE-LA-CUENTA"] = ''.rjust(4, '0')  # length 4
        record["CANTIDAD-DE-CUOTAS"] = ''.rjust(3, '0')  # length 3

        body.append(record)

    return body


def prepare_trailer(institution_id, retailer_id):
    '''
    trailer preparation for retailer wise reports
    '''
    # accepted_total_transaction_count,accepted_total_final_amount,accepted_total_transaction_amount = 0,0,0
    # rejected_total_transaction_count,rejected_total_final_amount,rejected_total_transaction_amount = 0,0,0
    # total of liquidated and non liquidated
    try:
        approved_records = ISERetailer.select(fn.COUNT(ISERetailer.CardAcceptorIdentification).alias('Transaction_Count'),
                                              fn.SUM(ISERetailer.FinalAmount).alias(
                                                  'Final_Amount'),
                                              fn.SUM(ISERetailer.TransactionAmount).alias('Transaction_Amount')).where(
            (ISERetailer.AcquiringInstitutionIdentification == institution_id) &
            (ISERetailer.CardAcceptorIdentification == retailer_id) &
            (((ISERetailer.MessageType == "0210") &
              (ISERetailer.ProcessingCode.startswith('00')) &
              (ISERetailer.ResponseCode == '00')) |
             ((ISERetailer.MessageType == "0420") &
              (ISERetailer.ProcessingCode.startswith('20')) &
              (ISERetailer.ResponseCode == '00')))
        ).get()
        # print(approved_records.sql())
        approved_total_transaction_count = 0 if approved_records.Transaction_Count == None else int(
            approved_records.Transaction_Count)
        approved_total_final_amount = 0 if approved_records.Final_Amount == None else int(
            approved_records.Final_Amount)
        approved_total_transaction_amount = 0 if approved_records.Transaction_Amount == None else int(
            approved_records.Transaction_Amount)
    except ISERetailer.DoesNotExist:
        approved_total_transaction_count, approved_total_final_amount, approved_total_transaction_amount = 0, 0, 0

    # rejected of liquidated and non liquidated
    try:
        rejected_records = ISERetailer.select(fn.COUNT(ISERetailer.CardAcceptorIdentification).alias('Transaction_Count'),
                                              fn.SUM(ISERetailer.FinalAmount).alias(
                                                  'Final_Amount'),
                                              fn.SUM(ISERetailer.TransactionAmount).alias('Transaction_Amount')).where(
            (ISERetailer.AcquiringInstitutionIdentification == institution_id) &
            (ISERetailer.CardAcceptorIdentification == retailer_id) &
            (((ISERetailer.MessageType == "0420") &
              (ISERetailer.ProcessingCode.startswith('00')) &
              (ISERetailer.ResponseCode == '00')) |
             ((ISERetailer.MessageType == "0210") &
              (ISERetailer.ProcessingCode.startswith('20')) &
              (ISERetailer.ResponseCode == '00')))
        ).get()
        # print(rejected_records.sql())
        rejected_total_transaction_count = 0 if rejected_records.Transaction_Count == None else int(
            rejected_records.Transaction_Count)
        rejected_total_final_amount = 0 if rejected_records.Final_Amount == None else int(
            rejected_records.Final_Amount)
        rejected_total_transaction_amount = 0 if rejected_records.Transaction_Amount == None else int(
            rejected_records.Transaction_Amount)
    except ISERetailer.DoesNotExist:
        rejected_total_transaction_count, rejected_total_final_amount, rejected_total_transaction_amount = 0, 0, 0

    # print("institution_id,retailer_id",institution_id,retailer_id)
    # print("accepted_total_transaction_count,accepted_total_final_amount,accepted_total_transaction_amount",accepted_total_transaction_count,accepted_total_final_amount,accepted_total_transaction_amount)
    # print("rejected_total_transaction_count,rejected_total_final_amount,rejected_total_transaction_amount",rejected_total_transaction_count,rejected_total_final_amount,rejected_total_transaction_amount)

    accepted_count = approved_total_transaction_count - \
        rejected_total_transaction_count
    accepted_amount = approved_total_final_amount - rejected_total_final_amount

    trailer = collections.OrderedDict()

    trailer["CTL-TIP-REG"] = '03'  # length 2
    # length 6 total Numbre of Records - int
    trailer["CTL-REG-TOTAL"] = str(
        approved_total_transaction_count).rjust(6, '0')
    # length 13 Total Amount Liquidated - int
    trailer["CTL-MTO-TOTAL"] = str(
        approved_total_transaction_amount).rjust(13, '0')
    # length 6 total Number of Records Rejected - int
    trailer["CTL-REG-REC"] = str(rejected_total_transaction_count).rjust(6, '0')
    # length 13 total Rejected Amount - int
    trailer["CTL-MTO-REC"] = str(
        rejected_total_transaction_amount).rjust(13, '0')
    # length 6 total Accepted Records - int
    trailer["CTL-REG-ACEP"] = str(abs(accepted_count)).rjust(6, '0')
    # trailer["CTL-MTO-ACEP"]         = str(accepted_amount).rjust(13,'0')    #length 13 total Accepted Amount - int
    # length 13 total Accepted Amount - int
    trailer["CTL-MTO-ACEP"] = str(accepted_amount).rjust(13, '0')
    trailer["FILLER"] = ''.rjust(152, ' ')  # length 148 Filler (Comment)

    return trailer


def summary_mail(html_content, env_instance):
    try:
        subject = f'{env_instance} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}'
        sendmail_with_html_and_attachment(html_content, subject, glob.glob(f"./LogFiles/PhaseOne_jobs.log*")+glob.glob(f"./CompensationReports/ConciliationReports/{datetime.now().strftime(r'%b_%Y')}/*{datetime.now().strftime(r'%Y%m%d')}*"))
    except Exception as e:
        print(f"Mail Not Sent - {str(e)}")
    else:
        print("Mail Sent Successfully")


def create_directories(path, folder_name):

    # define the name of the directory to be created
    # path = "/tmp/year/month/week/day"
    created_dir = path + folder_name + "/"

    # define the access rights
    access_rights = 0o755

    try:
        os.makedirs(created_dir, access_rights)
    except OSError:
        print("Creation of the directory %s failed" % created_dir)
        return created_dir
    else:
        print("Successfully created the directory %s" % created_dir)
        return created_dir


def adjust_report(path, got_rrn_list):
    """ Make AdjustmentReport_YYMMDD.csv """

    try:
        store_adj_data = []

        for each_rrn in got_rrn_list:
            data = ISERetailer.select(
                ISERetailer.AcquiringInstitutionIdentification, ISERetailer.CardAcceptorIdentification, ISERetailer.CardAcceptorTerminalIdentification,
                ISERetailer.MerchantTypeCode, ISERetailer.MessageType, ISERetailer.ResponseCode, ISERetailer.ProcessingCode, ISERetailer.LocalTransactionTime,
                ISERetailer.LocalTransactionDate, ISERetailer.SettlementDate, ISERetailer.Track2Data, ISERetailer.SystemsTraceAuditNumber,
                ISERetailer.RetrievalReferenceNumber, ISERetailer.CardAcceptorNameLocation, ISERetailer.ChannelType, ISERetailer.CardType,
                ISERetailer.TransactionAmount, ISERetailer.RetCardTypeCommision, ISERetailer.RetMccCommision, ISERetailer.RetBinCommision,
                ISERetailer.RetTxnIdentifierCommision, ISERetailer.Retailer, ISERetailer.Acquirer, ISERetailer.Issuer, ISERetailer.TotalCommissions,
                ISERetailer.Retefuente, ISERetailer.Reteica, ISERetailer.Cree, ISERetailer.Reteiva, ISERetailer.TotalTaxes, ISERetailer.TotalDiscounts,
                ISERetailer.FinalAmount
            ).where(
                (ISERetailer.ResponseCode == '00') &
                (ISERetailer.RetrievalReferenceNumber == each_rrn)).dicts()

            for k2 in data:
                store_adj_data.append(k2)

        cols = ['AcquiringInstitutionIdentification', 'CardAcceptorIdentification', 'CardAcceptorTerminalIdentification', 'MerchantTypeCode', 'MessageType', 'ResponseCode',
                'ProcessingCode', 'LocalTransactionTime', 'LocalTransactionDate', 'SettlementDate', 'Track2Data', 'SystemsTraceAuditNumber', 'RetrievalReferenceNumber',
                'CardAcceptorNameLocation', 'ChannelType', 'CardType', 'TransactionAmount', 'RetCardTypeCommision', 'RetMccCommision', 'RetBinCommision', 
                'RetTxnIdentifierCommision','Retailer', 'Acquirer', 'Issuer', 'TotalCommissions', 'Retefuente', 'Reteica', 'Cree', 'Reteiva', 'TotalTaxes', 'TotalDiscounts', 
                'FinalAmount']

        ise_loader("ISE.html", f"{path}/AdjustmentReport_{current_date_format_1}.csv", list(store_adj_data), cols)
        print(f"Adjustment Report Generated at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')} ")
    
    except Exception as e:
        print("Adjustment Report Not Generated", e, e.args)


def conciliation_alert():
    ### * Conciliation * ###
    output_ep_file_loc = concillation_report_loc + month_dir

    file_keys = ['RetrievalReferenceNumber',
                 'TransmissionDateandTime',
                 'Track2Data',
                 'TransactionAmount',
                 'MessageType',
                 'ProcessingCode',
                 'ResponseCode',
                 'CardAcceptorIdentification']

    c = Conciliation(file_keys, output_ep_file_loc)
    summary_frame1, summary_frame2, summary_frame3 = c.create_report()

    total = dataframe_to_html(summary_frame1)
    approved = dataframe_to_html(summary_frame2)
    declined = dataframe_to_html(summary_frame3)
    issuer = dataframe_to_html(issuer_count_at_issuer())
    acquirer = dataframe_to_html(issuer_count_at_acquirer())
    
    issuer1 = dataframe_to_html(issuer_count())
    acquirer1 = dataframe_to_html(acquirer_count())

    # * Disputes Finding
    file_keys = ['RetrievalReferenceNumber',
                 'LocalTransactionDate',
                 'LocalTransactionTime',
                 'Track2Data',
                 'MessageType',
                 'ProcessingCode',
                 'TransactionAmount']
                 

    c = ReversalsDeclinedAgainstApproved(file_keys, output_ep_file_loc)
    summary_frame = c.create_report()


    details = """  
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-GB">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>E-Mail Alert</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <style type="text/css">
  </style>

</head>

<body style="margin: 0; padding: 0;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
    <tbody>
      <tr>
        <td style="padding: 10px 0 10px 0;">

          <table align="center" border="0" cellpadding="0" cellspacing="0" width="97%" style="">
            <tbody>


              <tr>
                <td bgcolor="#ffffff" style="padding: 10px 10px 10px 10px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                    <tbody>
                      <tr>
                        <td style="color: #153643; font-family: Verdana, sans-serif;">
                          <h3 style="margin: 0;">Transaction Mismatch and Count Summary</h3>
                        </td>
                      </tr>

                      
                      <tr>
                        <td>
                          <table border="0" cellpadding="0" cellspacing="0" width="100%"
                            style="border-collapse: collapse;">
                            <tbody>
                              <tr>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Total :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          {total}
                                        </td>
                                      </tr>


                                    </tbody>
                                  </table>
                                </td>
                                <td style="line-height: 0;" width="20">&nbsp;</td>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;"></p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                              </tr>
                              <tr>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Approved :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          {approved}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                                <td style="line-height: 0;" width="20">&nbsp;</td>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Declined :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                           {declined}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                              </tr>
                              <tr>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Issuer :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          {issuer}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                                <td style="line-height: 0;" width="20">&nbsp;</td>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Acquirer :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                           {acquirer}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                              </tr>
                              <tr>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Issuer :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          {issuer1}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                                <td style="line-height: 0;" width="20">&nbsp;</td>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Acquirer :</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                           {acquirer1}
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </td>
              </tr>

            </tbody>
          </table>

        </td>
      </tr>
    </tbody>
  </table>


</body>

</html>

""".format(total=total,approved=approved,declined=declined, issuer=issuer, acquirer=acquirer, issuer1=issuer1, acquirer1=acquirer1)
    return details


def issuer_transaction_load(pick_date):

    # * Clean previous uploaded transaction
    queries.clean_issuer_extract_tables()

    upload_status = upload_extract_file(issuer_input_extract_loc, issuer_processed_extract_loc,
                                        extract_file_name, "issueroriginal", "issuerduplicates",pick_date)
    if (upload_status != False):
        validations.validationRetailerExistIssuer()
        validations.cleanIssuerNonValidated()
        queries.copyToIssuerExtract()
        queries.copyToIssuerExtractCopy()
        #exit(True)
        return True
    else:
        sendmail_with_html_and_attachment(html_content="<h3>No Issuer Extract File Present / No Transactions Found</h3>", mail_subject = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}')
        #exit(False)
        return False

def acquirer_transaction_load(pick_date):

    # * Clean previous uploaded transaction
    queries.clean_acquirer_extract_tables()

    upload_status = upload_extract_file(acquirer_input_extract_loc, acquirer_processed_extract_loc,
                                        extract_file_name, "acquireroriginal", "acquirerduplicates", pick_date)
    if (upload_status != False):
        validations.validationRetailerExistAcquirer()
        validations.cleanAcquirerNonValidated()
        validations.cleanAcquireOriginalReversalSuccess()
        queries.copyToAcquirerExtract()
        #exit(True)
        return True
    else:
        sendmail_with_html_and_attachment(html_content="<h3>No Acquirer Extract File Present / No Transactions Found</h3>", mail_subject = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}')
        #exit(False)
        return False

def fullDayAcquirerExtractLoad(pick_date):
    """
    * CC0024 Specific :-
    For loading extract files with full day transactions
    """

    # * Clean previous uploaded transaction
    queries.fullday_clean_acquirer_extract_tables()

    upload_status = upload_extract_file(acquirer_fullday_input_extract_loc, acquirer_fullday_processed_extract_loc,
                                        fullday_extract_file_name, "fulldayacquireroriginal", "fulldayacquirerduplicates", pick_date)

    if (upload_status != False):
        validations.validationRetailerExistAcquirerFullDay()
        validations.cleanAcquirerNonValidatedFullDay()
        queries.copyToFullDayAcquirerExtract()
        return True

    else:
        # * Send Mail Only When No Extract File (Found / Present)
        sendmail_with_html_and_attachment(html_content="<h3>No Full Day Acquirer Extract File Present / No Transactions Found</h3>", mail_subject = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}')
        return False


def acquirer_commission():
    base_liquidation()
    print(f"Phase One Mismatch Report Generation started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    sp.call("python3 -W ignore p1MissMatchReports.py",shell=True)
    print(f"Phase One Mismatch Report Finished started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")


def common_alert():
    print(f"Conciliation alert started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    body = conciliation_alert()
    summary_mail(html_content=body, env_instance = ENV)
    print(f"Conciliation alert finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
        

def final_alert():
    print(f"Summary alert started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    hc = mail_layout() # html_content
    sub = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}'
    sendmail_with_html_and_attachment(html_content = hc, mail_subject = sub, attach_files = glob.glob(f"./LogFiles/PhaseTwo_jobs.log*"))
    print(f"Summary alert finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")


def acquirer_reports_generation():
    # * Folder Name
    folder_name = f"Merchant_Compensation_Report_{current_date_format_2}"
    # * Zip File Name
    zip_file_name = f"{folder_name}.zip"
    # * Create Month Directory At All Reports Location
    create_directories(concillation_report_loc, month_dir)
    # * Create Directory With Todays Date and Timestamp
    current_dir = create_directories(retailer_report_loc, folder_name)

    #### * All Reports Generation Done Here * ####
    r = Reports("", "", current_dir)
    r.csvReport(AcquirerNotValid, "InvalidTransactionsReport") # * Invalid Transactions Report
    r.all_transactions_report()  # * Liquidation Reports
    r.transactions_summary_report()  # * Liquidation Summary Reports
    bech_liquidation_retailer_reports(current_dir) # * Retailer Wise Report For Bech
    r.all_retailer_report()  # * Retailer Status Reports
    r.blocked_retailer_report() # * Blocked Retailer Report
    create_report = RetailerReports(current_dir)
    # * Commented By Tejaswini [07Sep2022] - Added acq_RevSucPurDec from retailer_daily_montly_report
    create_report.acq_RevSucPurDec("AcquirerReversalSuccessPurchaceDecline") # * AcquirerReversalSuccessPurc
    create_report.dailyAcquirerReport("Daily_Report") # * Daily Reports
    create_report.dailyIssuerReport("Daily_Report") # * Daily Reports
    bank_deposit_trx_daily_details(current_dir) # * Deposit Reports
    print(f"Report Generation Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    #### * Zip & File Transfers Are Done Here * ####
    # * Comment By Ankita H. [24 Aug 2022] :- Uncomment only on Green Prod
    list_of_files = compress_generated_reports(current_dir)
    make_zip(list_of_files, zip_directory_loc, zip_file_name)
    # origin_file_name = dest_file_name = zip_file_name
    # file_transfer(zip_directory_loc, origin_file_name, zip_backup_loc, dest_file_name, host="192.168.3.83", username="comp_prod_ftp", password="comp_prod_ftp$2021", port=22)
    # file_transfer(zip_directory_loc, origin_file_name, zip_Columbiabk_loc, dest_file_name, host="192.168.6.10", username="compsan_bk", password="compsanbk#15Feb2023", port=45450)

    # * Send Mail To Internal Team (Report Generation Completed & Can Start Verification)
    sub = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}'
    details = f"""
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
        <tbody>
            <tr>
            <td style="color: #153643; font-family: Verdana, sans-serif;">
                <h4 style="margin: 0;">Report Generation Completed. Please Start Verification.</h4>
            </td>
            </tr>

            <tr>
            <td style="color: #153643; font-family: Verdana, sans-serif;">
                <h4 style="margin: 0;">Zip Loaction : {zip_backup_loc}{zip_file_name}</h4>
            </td>
            </tr>
        </tbody>
    </table>
    """
    sendmail_with_html_and_attachment(html_content=details, mail_subject=sub)
    print("Internal Mail Alert Sent")


def acquirer_history_load():
    # * All Counts Are Displayed & History Insert / Update Done Here
    received = AcquirerOriginal.select().count()
    print(f"History Insert & Update Started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    update_count = copy_to_txn_history() # * Insert & Update History
    print(f"History Insert & Update Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    print(f"\nReceived Transactions:           {int(received)}")
    invalid = AcquirerNotValid.select().count()
    print(f"Invalid Transactions:            {int(invalid)}")
    valid = AcquirerExtract.select().count()
    print(f"Valid Transactions:              {int(valid)}")
    print(f"\nInserted Acquirer Transactions In History: {int(abs(ISERetailerCopy.select().count()))}")
    print(f"Updated Acquirer Transactions In History:  {int(update_count)}\n")


def acquirer_phase_one(pick_date):
    return acquirer_transaction_load(pick_date)


def acquirer_phase_second():
    print(f"Commission calculation started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    acquirer_commission()
    print(f"Commission calculation finished at  {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")


def acquirer_phase_third():
    acquirer_reports_generation()
    acquirer_history_load()


def issuer_phase_one(pick_date):
    return issuer_transaction_load(pick_date)


def issuer_phase_third():
    queries.copyToIssuerHistory()


if __name__ == "__main__":

    # * Parameters From CLI
    process = argv[1]
    try:
        args1 = argv[2]
    except:
        pass

    if process == "SummaryMail":
        hc = mail_layout()  # html_content
        summary_mail(html_content=hc, env_instance=ENV)
        print(f"Mail Sent at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "CombineProcessing":
        p1 = mp.Process(name='acquirer_phase_one',
                        target=acquirer_phase_one, args=(args1,))
        p2 = mp.Process(name='issuer_phase_one',
                        target=issuer_phase_one, args=(args1,))
        pdb = mp.Process(name='truncate_iseretailer',
                        target=queries.clean_liquidation_tables)
        p1.start()
        p2.start()
        pdb.start()
        p1.join()
        p2.join()
        pdb.join()

        if p1.exitcode and p2.exitcode:
            p3 = mp.Process(name='common_alert', target=common_alert)
            p4 = mp.Process(name='acquirer_phase_second',
                            target=acquirer_phase_second)
            p4.start()
            p3.start()
            p4.join()
            p3.join()

            p5 = mp.Process(name='acquirer_phase_third', target=acquirer_phase_third)
            p6 = mp.Process(name='issuer_phase_third', target=issuer_phase_third)
            p5.start()
            p6.start()
            p5.join()
            p6.join()

            final_alert()
            queries.clean_liquidation_tables()
            queries.truncate_issuerextractcopy_table()
        else:
            print(
                f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(
                f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "CombineProcessingPhaseOne":
        """p1 = mp.Process(name='acquirer_phase_one',
                        target=acquirer_phase_one, args=(args1,))
        p2 = mp.Process(name='issuer_phase_one',
                        target=issuer_phase_one, args=(args1,))

        p1.start()
        p2.start()
        p1.join()
        p2.join()"""
        
        p1 = acquirer_phase_one(args1)
        p2 = issuer_phase_one(args1)
        print(p1,p2)
        if p1 and p2:
            p3 = mp.Process(name='acquirer_phase_second',
                            target=acquirer_phase_second)
            p3.start()
            p3.join()
            common_alert()
        else:
            print(
                f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(
                f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "CombineProcessingPhaseTwo":
        """p5 = mp.Process(name='acquirer_phase_third', target=acquirer_phase_third)
        p6 = mp.Process(name='issuer_phase_third', target=issuer_phase_third)

        p5.start()
        p6.start()
        p5.join()
        p6.join()"""
        acquirer_phase_third()
        issuer_phase_third()
        final_alert()
        queries.clean_liquidation_tables()
        queries.truncate_issuerextractcopy_table()

    elif process == "IssuerProcessing":
        issuer_phase_one(args1)
        issuer_phase_third()
        queries.truncate_issuerextractcopy_table()

    elif process == "AcquirerProcessing":
        p1 = mp.Process(name='acquirer_phase_one',
                        target=acquirer_phase_one, args=(args1,))
        p1.start()
        p1.join()

        if p1.exitcode:
            queries.truncate_issuerextractcopy_table()
            queries.clean_issuer_extract_tables()
            queries.clean_liquidation_tables()
            common_alert()
            acquirer_phase_second()
            acquirer_phase_third()
            final_alert()
        else:
            print(
                f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(
                f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "AcquirerCVProcessing":
        """p1 = mp.Process(name='acquirer_phase_one',
                        target=acquirer_phase_one, args=(args1,))
        p1.start()
        p1.join()"""
        
        p1 = acquirer_phase_one(args1)
        queries.clean_issuer_extract_tables()

        if p1:
            p3 = mp.Process(name='acquirer_phase_second',
                            target=acquirer_phase_second)
            p3.start()
            p3.join()
            common_alert()
        else:
            print(
                f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(
                f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

  # * call all functions in proper order
