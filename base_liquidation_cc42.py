from base_liquidation import *
from daily_trx_credit_report_cc42 import bank_deposit_trx_daily_details_cc42
from reports_cc42 import Reports
from settlement_report_cc42 import mail_layout_cc42
from liquidation_CC42 import liquidate_transaction
from CC042query import *

zip_backup_loc = f'/comp_repo/{datetime.now().strftime(r"%b_%Y")}/{datetime.now().strftime(r"%d-%b-%y")}/'

def base_liquidation_cc42():

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
      NewISERetailer.insert_many(batch).execute()

  # * Success Trnxs Only
  for txn in AcquirerExtract.select().where(AcquirerExtract.ResponseCode == "00").iterator():
      try: retailer.append(liquidate_transaction(single_txn = txn, ret_account_dict = mem_account))
      except Exception as e: raise

  del mem_account  

  try:
      if len(retailer) > 0:
          with myDB.atomic():
              for batch in chunked(retailer, 1000):
                  NewISERetailer.insert_many(batch).execute()
      del retailer
  except Exception as e:
      print(f"Error Inserting Records In ISERetailer - {str(e)}")


def acquirer_commission_cc42():
    base_liquidation_cc42()
    print(f"Phase One Mismatch Report Generation started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    sp.call("python3 -W ignore p1MissMatchReports.py", shell=True)
    print(f"Phase One Mismatch Report Finished started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")


def acquirer_phase_second_cc42():
    """ CC042 Specific

    """
    print(f"Commission calculation started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    acquirer_commission_cc42()
    print(f"Commission calculation finished at  {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

def final_alert():
    print(f"Summary alert started at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    hc = mail_layout_cc42() # html_content
    sub = f'{ENV} Liquidation/Compensation Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}'
    sendmail_with_html_and_attachment(html_content = hc, mail_subject = sub, attach_files = glob.glob(f"./LogFiles/PhaseTwo_jobs.log*"))
    print(f"Summary alert finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")


def acquirer_reports_generation_cc42():
    # * Folder Name
    folder_name = f"Merchant_Compensation_Report_{current_date_format_2}"
    # # * Zip File Name
    zip_file_name = f"{folder_name}.zip"
    # # * Create Month Directory At All Reports Location
    # create_directories(concillation_report_loc, month_dir)
    # # * Create Directory With Todays Date and Timestamp
    current_dir = create_directories(retailer_report_loc, folder_name)
    backup_dir = create_directories("./CompensationReports/", "RetailerCompansationBackup")


    #### * All Reports Generation Done Here * ####
    r = Reports("", "", current_dir)
    # * Invalid Transactions Report
    r.all_transactions_report()  # * Liquidation Reports
    r.Compsation_table_backup()
    print(f"Backup of RetailerCompansation Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    bank_deposit_trx_daily_details_cc42(current_dir) # * Deposit Reports
    print(f"Report Generation Finished at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    #### * Zip & File Transfers Are Done Here * ####
    # * Comment By Ankita H. [24 Aug 2022] :- Uncomment only on Green Prod
    list_of_files = compress_generated_reports(current_dir)
    make_zip(list_of_files, zip_directory_loc, zip_file_name)
    origin_file_name = dest_file_name = zip_file_name
    #file_transfer(zip_directory_loc, origin_file_name, zip_backup_loc, dest_file_name, host="192.168.3.83", username="comp_prod_ftp", password="comp_prod_ftp$2021", port=22)
    #file_transfer(zip_directory_loc, origin_file_name, zip_Columbiabk_loc, dest_file_name, host="192.168.6.10", username="compsan_bk", password="compsanbk#15Feb2023", port=45450)

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

def acquirer_phase_third():
    acquirer_reports_generation_cc42()
    
def issuer_phase_third():
    queries.copyToIssuerHistory()

if __name__ == "__main__":
    

    # * Parameters From CLI
    process = argv[1]
    try:args1 = argv[2]
    except:pass

    if process == "SummaryMail":
        hc = mail_layout()  # html_content
        summary_mail(html_content=hc, env_instance=ENV)
        print(f"Mail Sent at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "CombineProcessingPhaseOne":
        p1 = acquirer_phase_one(args1)
        p2 = issuer_phase_one(args1)
        if p1 and p2:
            p3 = mp.Process(name='acquirer_phase_second_cc42',target=acquirer_phase_second_cc42)
            p3.start()
            p3.join()
            common_alert()
        else:
            print(f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
                
    elif process == "CombineProcessingPhaseTwo":
        acquirer_phase_third()
        issuer_phase_third()
        final_alert()
        # queries.clean_liquidation_tables()
        queries.truncate_issuerextractcopy_table()
      
    elif process == "AcquirerProcessing":
        p1 = acquirer_phase_one(args1)

        if p1:
            queries.truncate_issuerextractcopy_table()
            queries.clean_issuer_extract_tables()
            common_alert()
            acquirer_phase_second_cc42()
            acquirer_phase_third()
            final_alert()
        else:
            print(f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

    elif process == "AcquirerCVProcessing":
        
        p1 = acquirer_phase_one(args1)
        queries.clean_issuer_extract_tables()

        if p1:
            p3 = mp.Process(name='acquirer_phase_second_cc42',target=acquirer_phase_second_cc42)
            p3.start()
            p3.join()
            common_alert()
        else:
            print(f"Commission calculation Failed At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
            print(f"Exited Process At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")

      # * call all functions in proper order
