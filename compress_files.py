from utils import *
from zipfile import ZipFile



def make_zip(list_of_files, zip_directory_location, zip_file_name):
    try:
        with ZipFile("{}{}".format(zip_directory_location, zip_file_name), 'w',) as zip:
            for file in list_of_files:
                zip.write(file)
        print("All Files Zipped Successfully! at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        print('Error In Compressing Files - {}'.format(str(e)))



def compress_generated_reports(retailer_report_loc,  date=datetime.today().date()):
    searched_files = search_latest_files(retailer_report_loc, "", date)
    list_of_files = [file_name["absolute_file_name"] for file_name in searched_files]
    return list_of_files



if __name__ == "__main__":
    pass
