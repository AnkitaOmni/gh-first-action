#!/home/compsan/comp_env/bin/python3
# coding: utf8

import os
import sys
import pandas as pd
from glob import glob
import ConcillationModule
from datetime import datetime
from file_transfer import mv_file
from sendmail_alerts import sendmail_with_html_and_attachment

if __name__ == '__main__':

    print(f"\nEncoding = {sys.stdout.encoding}")
    print(f"Get Default Encoding = {sys.getdefaultencoding()}")

    ENV = "PROD"
    OUTPUT_PATH = r"./ConcillationModule/BrandWiseReports/"
    EP_IN_PATH = r"./ConcillationModule/EPFiles/InputReports/*"
    #TN70_IN_PATH = r"./ConcillationModule/TN70/InputReports/*"
    T464_IN_PATH = r"./ConcillationModule/T464/InputReports/*"

    EP_OUT_PATH = r"./ConcillationModule/EPFiles/ProcessedReports/"
    #TN70_OUT_PATH = r"./ConcillationModule/TN70/ProcessedReports/"
    T464_OUT_PATH = r"./ConcillationModule/T464/ProcessedReports/"

    try:
        os.system('rm ./ConcillationModule/BrandWiseReports/*.txt')
    except Exception as e:
        pass

    # * Call Respective Function From Moudles 
    visa = ConcillationModule.VisaToExtract(OUTPUT_PATH)
    #mastercard = ConcillationModule.TN70ToExtract(OUTPUT_PATH)
    maestro = ConcillationModule.T464ToExtract(OUTPUT_PATH)
    print(os.getcwd())


    print("\n*************** Start Parsing Brand Files ***************")
    # * Files Parsing And Data Storage To Create DataFrames
    print()
    for each_file in glob(EP_IN_PATH):
        print("EPFiles Each File = ", each_file)
        visa.store_file_data(each_file)
        new_file_name = each_file.split("/")[-1]
        mv_file(each_file, f'{EP_OUT_PATH}{datetime.now().strftime(r"%y%m%d")}_{new_file_name}') # * Using to rename files

    print()
    #for each_file in glob(TN70_IN_PATH):
    #    print("TN70 Each File = ", each_file)
    #    mastercard.store_file_data(each_file)
    #    new_file_name = each_file.split("/")[-1]
    #    mv_file(each_file, f'{TN70_OUT_PATH}')

    print()
    for each_file in glob(T464_IN_PATH):
        print("T464 Each File = ", each_file)
        maestro.store_file_data(each_file)
        new_file_name = each_file.split("/")[-1]
        mv_file(each_file, f'{T464_OUT_PATH}')


    print("\n*************** Start Making Extract Files ***************")
    # * Create Respective Extract Files
    visa.create_frame_by_list_of_file()
    #mastercard.create_frame_by_list_of_file()
    maestro.create_frame_by_list_of_file()
    
    print("\n*************** Start Final Extract Files ***************\n")
    # * Make Final Extract
    df1 = pd.read_csv(glob(f"{OUTPUT_PATH}*.txt")[0], dtype=str, engine='python')
    df2 = pd.read_csv(glob(f"{OUTPUT_PATH}*.txt")[1], dtype=str)
    #df3 = pd.read_csv(glob(f"{OUTPUT_PATH}*.txt")[2], dtype=str)

    final_df = pd.concat([df1, df2])
    final_df.to_csv(f'{OUTPUT_PATH}FINAL_EXTRACT_{datetime.now().strftime(r"%y%m%d")}.txt', index=False)
    print(f'Final Extract = {OUTPUT_PATH}FINAL_EXTRACT_{datetime.now().strftime(r"%y%m%d")}.txt')


    print("\n*************** Start Moving To ProcessedReports ***************")
    try:
        ''' Move To Respective Month and Year Folder '''
        print(f'mv ./ConcillationModule/BrandWiseReports/*.txt ./ConcillationModule/BrandWiseReports/{datetime.now().strftime(r"%b_%Y")}')
        os.system(f'mv ./ConcillationModule/BrandWiseReports/*.txt ./ConcillationModule/BrandWiseReports/{datetime.now().strftime(r"%b_%Y")}')
    except Exception as e:
        pass


    print("\n*************** Start Mail Alert ***************")
    # * Send Alert With Log File
    htm_cont = f"""
    Dear Support,

    <br><br><br>
    Please Start Verification Of Extract Files Kept At
    <br><br>
    Concillation Files Loc :- /home/compsan/{ENV}/ConcillationModule/BrandWiseReports/{datetime.now().strftime(r"%b_%Y")}<br><br>
    Excel Report Loc :- /home/compsan/{ENV}/ConcillationModule/FinalExcelReport/{datetime.now().strftime(r"%b_%Y")}/{datetime.now().strftime(r"%d%b%Y")}_SummaryReport.xlsx<br><br>
    """
    mail_sub = f"Extract Made Using Brand Files {datetime.now().strftime(r'%d/%b/%Y')}"
    try:
        sendmail_with_html_and_attachment(htm_cont, mail_sub, glob("./ConcillationModule/*.xlsx*"))
        print("\n\n\nMail Alert Sent")
    except Exception as e:
        print(f"\n\n\nMail Not Sent Error = {e}")
    finally:
        print("make_issuer_extract.py script run ended...!!\n\n")
    # print(f"Yoo Man = ./ConcillationModule/{datetime.now().strftime(r'%d%b%Y')}_SummaryReport.xlsx')")
