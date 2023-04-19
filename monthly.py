""" 
# * Author          :-  Dishant
# * Created Date    :-  04/Sep/2022
# * Updated Date    :-  04/Sep/2022
# * Usage           :-  generate monthly reports
# * Job             :-  45 01 2 * * (At 01:45 on day-of-month 2)
# * Monitoring Cmd  :-  clear; ps -aux | grep "monthly.py"; cat LogFiles/monthly.log; tree CompensationReports/MonthlyReports/MMM_YYYY
"""

#!~/comp_env/bin/python3

from glob import glob
from datetime import date, datetime
from calendar import monthrange
from issuer_statistics import IssuerStats
from os import system, chdir, getcwd, path
from acquirer_statistics import AcquirerStats
from base_liquidation import create_directories
from retailer_daily_monthly_report import RetailerReports
from sendmail_alerts import sendmail_with_html_and_attachment

environment_instance_name = "ColDocker-QA"

# * Current Date / Today
currentDate = date.today()
# * Current Month
currMonthFisrtDate = date(currentDate.year, currentDate.month, 1)
currMonthLastDate = date(currentDate.year, currentDate.month, monthrange(currentDate.year, currentDate.month)[1])
# * Previous Month
prevMonthFisrtDate = currentDate.replace(day=1, month=currentDate.month-1)
prevMonthLastDate = date(prevMonthFisrtDate.year, prevMonthFisrtDate.month, monthrange(prevMonthFisrtDate.year, prevMonthFisrtDate.month)[1])

# * Current File Path
currDirPath = path.abspath(getcwd())
# * Acquirer Report Path
acqReportPath = f"./CompensationReports/MonthlyReports/{currentDate.strftime('%b_%Y')}/Acquirer/"
# * Issuer Report Path
issReportPath = f"./CompensationReports/MonthlyReports/{currentDate.strftime('%b_%Y')}/Issuer/"


print(f"currentDate = {currentDate}")
print(f"currDirPath = {currDirPath}")
print(f"currMonthFisrtDate = {currMonthFisrtDate} || currMonthLastDate = {currMonthLastDate}")
print(f"prevMonthFisrtDate = {prevMonthFisrtDate} || prevMonthLastDate = {prevMonthLastDate}\n\n")

create_directories(path=f"./CompensationReports/MonthlyReports/", folder_name=currentDate.strftime(r'%b_%Y'))
create_directories(path=f"./CompensationReports/MonthlyReports/{currentDate.strftime('%b_%Y')}/", folder_name="Acquirer")
create_directories(path=f"./CompensationReports/MonthlyReports/{currentDate.strftime('%b_%Y')}/", folder_name="Issuer")

try:
    # * Acquirer Report
    print(f"\n\nAcquirer Report Loc = {acqReportPath}")
    acqStat = AcquirerStats(f"{acqReportPath}")
    createReport1 = RetailerReports(f"{acqReportPath}")
    createReport1.monthlyAcquirerReport("Acquirer_Monthly_Report", str(prevMonthFisrtDate), str(prevMonthLastDate))
    acqStat.monthly_responsecodes_count_against_messagetypes("Monthly_Acquirer_ResponseCodes", str(prevMonthFisrtDate), str(prevMonthLastDate))
    acqStat.monthly_pointofservice_entrymode_count("Monthly_Acquirer_PointofServiceEntryModeCode", str(prevMonthFisrtDate), str(prevMonthLastDate))
    print(f"\n\nZip Acquirer Reports")
    # print(f"current dir = {getcwd()}")
    chdir(f"{acqReportPath}")
    print(f"current dir = {getcwd()}")
    system(f"rm -f *.zip")
    system(f"zip Acquirer.zip *")
    chdir(f"{currDirPath}/")
    del createReport1, acqStat

    # * Issuer Report
    print(f"\n\nIssuer Report Loc = {issReportPath}")
    issStat = IssuerStats(f"{issReportPath}")
    createReport2 = RetailerReports(f"{issReportPath}")
    createReport2.monthlyIssuerReport("Issuer_Monthly_Report", str(prevMonthFisrtDate), str(prevMonthLastDate))
    issStat.monthly_responsecodes_count_against_messagetypes("Monthly_Issuer_ResponseCodes", str(prevMonthFisrtDate), str(prevMonthLastDate))
    issStat.monthly_pointofservice_entrymode_count("Monthly_Issuer_PointofServiceEntryModeCode", str(prevMonthFisrtDate), str(prevMonthLastDate))
    print(f"\n\nZip Issuer Reports")
    # print(f"current dir = {getcwd()}")
    chdir(f"{issReportPath}")
    print(f"current dir = {getcwd()}")
    system(f"rm -f *.zip")
    system(f"zip Issuer.zip *")
    chdir(f"{currDirPath}/")
    del createReport2, issStat

    print("\n\n")
    system(f"tree ./CompensationReports/MonthlyReports/{currentDate.strftime('%b_%Y')}/")

    html_content = f"""
    Dear Support,

    <br><br>
    Monthly Reports Job has been run successfully.
    <br><br>
    Please Start Verification Of Monthly Reports Kept At :-
    <br>
    <b> /home/compsan/{environment_instance_name}/CompensationReports/MonthlyReports/{datetime.now().strftime(r"%b_%Y")}/ <b>
    <br><br><br>
    """
    subject = f'Compensation {environment_instance_name} Monthly Reports Job for {currentDate.strftime("%b %Y")} Processed At {datetime.today().strftime(r"%Y-%m-%d %H:%M:%S")}'

    # sendmail_with_html_and_attachment(htmlContent=htmlContent, mailSubject=mailSubject, attachFiles=glob(f"./LogFiles/monthly.log*"))
    sendmail_with_html_and_attachment(html_content, subject, glob(f"./LogFiles/monthly.log*"))
    print(f"Monthly Reports Job Done & Mail Sent at {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}")

except Exception as error:
    print(f"Error monthly.py = {error}")

finally:
    del create_directories, RetailerReports, currDirPath
    del currentDate, currMonthFisrtDate, currMonthLastDate
    del prevMonthFisrtDate, prevMonthLastDate, date, monthrange


if __name__ == "__main__":
    pass
