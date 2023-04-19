import csv, sys
from glob import glob
from config import Config
from subprocess import call,check_output,CalledProcessError
from datetime import datetime
from utils import search_files
from model import myDB, RetailerId
from base_liquidation import create_directories
from sendmail_alerts import sendmail_with_html_and_attachment


config = Config().get_config_json()
ENV = f"{config['ENV_NAME']}"


def make_json(csvLoaderFilePath):
    new_loader_data = []

    # Open a csv reader called DictReader
    with open(csvLoaderFilePath, encoding='unicode_escape') as csvf:
        csvReader = csv.DictReader(csvf, delimiter='|', doublequote=False)
        try:
            for rows in csvReader:
                data = {}
                data["RetailerId"] = rows['RETAILER_ID']  # "112233454"
                data["EntityId"] = rows['INSTITUTION_ID']  # "00010012"
                data["GroupCode"] = 0  # 1
                data["MallCode"] = 0  # 2
                data["AcquirerRegionCode"] = rows['RETAILER_REGION']  # ""
                data["CompanyName"] = rows['RETAILER_LEGAL_NAME']  # "GeoPagos"
                data["Name"] = rows['RETAILER_NAME'] #.decode('latin-1').encode("utf-8")  # "GeoPagos"
                data["CountryCode"] = rows['COUNTRY'].strip()  # "CH"
                data["StateCode"] = rows['STATE_CODE']  # ""
                data["CityCode"] = 0 if len(rows['CITY_CODE']) == 0 else int(rows['CITY_CODE'])  # 0
                data["CountyCode"] = 0  # 0
                data["Address"] = ""  # "Chille 127 # 15-34 Local 101"
                data["PostalCode"] = rows['POSTAL_CODE']  # "8320000"
                data["Phone"] = rows['CONTACT']  # "+ 56 1 2345678"
                data["CellPhone"] = ""
                data["FaxPhone"] = ""
                data["AfterHoursPhone"] = ""
                data["AfterHoursCellPhone"] = ""
                data["AfterHoursFaxPhone"] = ""
                data["ReferralPhone"] = ""
                data["EmailAddress"] = rows['LEGAL_REPRESENTATIVE_EMAIL_ID'] # "banco@support.com"
                data["AlternateEmailAddress"] = ""
                data["IdentificationTypeCode"] = 0 if len(rows['IDENTIFICATION_DOC_TYPE']) == 0 else int(rows['IDENTIFICATION_DOC_TYPE'])  # 5
                data["IdentificationNumber"] = rows['TAX_ID']
                # data["MCC"] = 0 if len(rows['RETAILER_CATAGORY_CODE']) == 0 else int(rows['RETAILER_CATAGORY_CODE'])  # 5947
                data["MCC"] = rows['RUBRO_CODE'] # 5947
                data["MCCForNoPresentTransaction"] = 0  # 5947
                data["IdForAmex"] = ""
                data["MCCForAmex"] = 0  # 5947
                data["MCCForAmexForNoPresentTransaction"] = 0  # 5947
                data["WorkingHoursCode"] = 0  # 1
                data["DepositOnLineCode"] = 0  # 1
                data["PaymentVendorsCode"] = 0  # 1
                data["AffiliationDate"] = 0  # 0
                data["LastUpdateDateNotMonetary"] = 0  # 0
                data["LastUpdateDateMonetary"] = 0  # 0

                if rows['STATUS'] == 'ACTIVE': data["StatusCode"] = 1
                elif rows['STATUS'] == 'INACTIVE': data["StatusCode"] = 2
                elif rows['STATUS'] == 'TEMPORARILY BLOCKED': data["StatusCode"] = 3
                else: data["StatusCode"] = 4

                data["AssignedAgreeementCode"] = ""     # 0 if len(rows['ACCOUNT_TYPE']) == 0 else int(rows['ACCOUNT_TYPE'])
                data["MovmentType"] = rows['ACCOUNT_TYPE']
                data["AccountNumber"] = rows['ACCOUNT_ID']
                data["BankCode"] = rows['SETTLEMENT_BANK_CODE']                
                new_loader_data.append(data)
                
        except Exception as err:
            print(f"RetId = {rows['RETAILER_ID']}")
            print(err.args)
            

    return new_loader_data


def truncate_retailer():
    try:
        # myDB.truncate_table([RetailerId, TerminalId])
        myDB.execute_sql("""truncate retailerid""")
        print("Cleared Retailer Table\n")
        return True
    except Exception as e:
        print(e)
        print("Error In Cleaning Retailer Table\n")
        return False


def retailer_loader(lst):

    try:
        RetailerId.insert_many(lst).execute()
        del lst
    except Exception as e:
        print("Error, Uploading Records In RetailerId - {}".format(str(e)))


def mv_file(source, target):
    ''' Move File '''
    try:
        call(['mv', source, target])
        print(f"Transfer Location = {target} at {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")
    except Exception as e:
        print(f"File Not Transfered {e}")



if __name__ == '__main__':

    # * Parameters From CLI
    process = sys.argv[1]
    shell_script_path = sys.argv[2]

    if process == "RetailerLoader":
        
        total_retailer_count = 0 # give total count of retailers uploaded to DB
        truncate_retailer_table = 1 # if (files are there at location) and (there is data in files) 
        retailer_load_file_name = r'RETL_REPORT_' # report name to search for
        create_directories(f'{shell_script_path}/ApiLoaders/Retailer/ProcessedFiles/', datetime.now().strftime(r"%b_%Y"))
        destination = f'{shell_script_path}/ApiLoaders/Retailer/ProcessedFiles/{datetime.now().strftime(r"%b_%Y")}/'
        search_directory = f'{shell_script_path}/ApiLoaders/Retailer/InputFiles/'
        files_found = search_files(search_directory, retailer_load_file_name)
        
        print(f"\nUsing Path = {shell_script_path}") # make sure specified ENV is active
        call(['ls', '-lthr', search_directory]) # get listing of source location
        print("\n", "-"*60, "\n")

        if len(files_found) == 0:
            print("Retailer Load Missing From Location ...!!")
            print("Please Put The Retailer Load At Input Location")

        elif len(files_found) > 0:
            #print(f'wc -l {search_directory}*OPTX1_RETL_REPORT_{datetime.now().strftime(r"%Y-%m-%d")}*')
            # * added by matesh[20 Feb 2023 ] - Fix for retailer rectification count between TX and CA
            try:
                TxList = check_output(f'wc -l {search_directory}*OPTX1_RETL_REPORT*',shell=True).decode()
                TxTotal = check_output(f'ls {search_directory}*OPTX1_RETL_REPORT* | wc -l',shell=True).decode()
                TxCount = int(TxList.split('\n')[-2].split()[0]) - int(TxTotal)
            except CalledProcessError as e:
                TxCount = 0
                print("Tx Node File Not Found ")
                print("")
            try:
                CaList = check_output(f'wc -l {search_directory}*OPCA1_RETL_REPORT*',shell=True).decode()
                CaTotal = check_output(f'ls {search_directory}*OPCA1_RETL_REPORT* | wc -l',shell=True).decode()
                CaCount = int(CaList.split('\n')[-2].split()[0]) - int(CaTotal)
            except CalledProcessError as e:
                CaCount = 0
                print("CA Node File Not Found ")
                print("")
                
            CountDiff = False
            if TxCount > CaCount:
                file_check = 'OPCA1'
                CountDiff = True 
            elif CaCount > TxCount:
                file_check = 'OPTX1'
                CountDiff = True  
            for single_file in files_found:
                source = single_file['absolute_file_name']
                if CountDiff and file_check in single_file["file_name"]:
                    try:
                        print(f"Failed to Upload -: {source}")
                        Count = check_output(f'wc -l {source}',shell=True).decode().split()[0]
                        print(f"Count For :- {single_file['file_name']} = {int(Count)-1}")
                        mv_file(source, destination)
                        print("")
                    except Exception as e:
                        pass
                else:
                    print(single_file['absolute_file_name'], single_file["file_name"], single_file["file_date"])                
                    lst = make_json(single_file['absolute_file_name'])            
                    if len(lst) > 0:
                        if truncate_retailer_table == 1:
                            truncate_retailer()
                            truncate_retailer_table = 0 # to stop truncate of retailerid table more than once

                        print(f"Count For :- {single_file['file_name']} = {len(lst)}")
                        retailer_loader(lst)
                        mv_file(source, destination) # to move files to processed location
                        total_retailer_count += len(lst)
                        print("")

                    else:
                        print("No Retailers To Upload, Count - {}".format(len(lst)))
            
        print(f"\nTotal Retailer Count = {total_retailer_count}")
        print(f"\nTotal TX Count = {TxCount}")
        print(f"\nTotal CA Count = {CaCount}")
        
        print("\n", "-"*60, "\n")


    elif process == "Alert":

        html_content = "<H3><p>Retailer loader has been run successfully.</p></H3>"
        subject = f"Compensation {ENV} Retailer Job Processed At  {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}"
        sendmail_with_html_and_attachment(html_content, subject, glob(f"./LogFiles/loader_jobs.log*"))
        print(f"Retailer Loader Job Done & Mail Sent at {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}")


# * Kept For Testing Purpose Only [Please Do Not Delete]
# tree ./ApiLoaders/Retailer/InputFiles/ ./ApiLoaders/Retailer/ProcessedFiles/
# mv ./ApiLoaders/Retailer/ProcessedFiles/*30_* ./ApiLoaders/Retailer/InputFiles/
# clear; python3 man.py RetailerLoader

# call(['tree', search_directory])
# print(f"\nDestination Directory Listing = {destination}")
# os.system('ls -lthr ' + destination + ' | tail -5')
# os.system('mv ' + destination + '*' + " " + search_directory)


