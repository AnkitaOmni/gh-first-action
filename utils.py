
import os
from time import time
from collections import OrderedDict
from datetime import timedelta, datetime


def getFinalAmt(df):
    purAmt = df.loc[(df['MessageType'] == '0210') & (df['ProcessingCode'] == '000000')]['FinalAmount'].sum()
    refrevAmt = df.loc[(df['MessageType'] == '0420') & (df['ProcessingCode'] == '200000')]['FinalAmount'].sum()
    revAmt = df.loc[(df['MessageType'] == '0420') & (df['ProcessingCode'] == '000000')]['FinalAmount'].sum()
    refAmt = df.loc[(df['MessageType'] == '0210') & (df['ProcessingCode'] == '200000')]['FinalAmount'].sum()
    finalAmt = round((purAmt+refrevAmt) - (revAmt+refAmt))
    del df, purAmt, refrevAmt, revAmt, refAmt
    return finalAmt


def search_latest_files(directory, search_file_name, date):
    file_found = []
    try:
        y = int(date.split("-")[0])
        m = int(date.split("-")[1])
        d = int(date.split("-")[2])
        cur_date = datetime(y, m, d, 0, 0).date()
    except Exception as e:
        cur_date = date

    for file_name in os.listdir(directory):
        record = OrderedDict()
        absolute_file_name = directory + file_name
        file_date = datetime.fromtimestamp(os.path.getmtime(absolute_file_name)).date()

        if file_date == cur_date:
            if search_file_name in os.path.basename(absolute_file_name):
                record["absolute_file_name"] = absolute_file_name
                record["file_name"] = file_name
                record["file_date"] = file_date
                file_found.append(record)
    return file_found


def search_files(directory, search_file_name):
    file_found = []
    for file_name in os.listdir(directory):
        record = OrderedDict()
        absolute_file_name = directory + file_name
        file_date = datetime.fromtimestamp(os.path.getmtime(absolute_file_name)).date()

        if search_file_name in os.path.basename(absolute_file_name):
            record["absolute_file_name"] = absolute_file_name
            record["file_name"] = file_name
            record["file_date"] = file_date

            file_found.append(record)
    return file_found


def calculate_time(func):
    def innerFun(*args, **kwargs):
        st = time()
        func(*args, **kwargs)
        et = time()
        print(f"{func.__name__} : Execution Time = {str(timedelta(seconds=et-st))}")
    return innerFun


if __name__ == "__main__":
    pass
