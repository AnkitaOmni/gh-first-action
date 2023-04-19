
# * Author          :- Ankita Harad
# * Created Date    :- 14/Mar/2023
# * Updated Date    :- 14/Mar/2023
# * Description     :- To Verify Production env cache, Input Location Files, Cronjob and Prod UI 
# * Usage           :- sh CC24_Tables_Bk.sh || ./CC24_Tables_Bk.sh


from glob import glob
from os import system
from datetime import date, datetime
from sendmail_alerts import sendmail_with_html_and_attachment

environment_instance_name = "ColDocker-QA"

try:

    system(f"sh ./Scripts/CC24_Tables_Bk.sh > ./LogFiles/CC24_Tables_bk.log 2>&1")

    html_content = f"""
    Dear Team,
    <br><br>
    We have taken backup of below Tables :<BR>
    01. estadoidpupdate<BR>
    02. chileidpupdate<BR>
    03. estado_report<BR>
    04. chile_report<BR>
    05. fulldaytransactionhistory<BR>
    06. fulldaytransactionretailerhistory<BR>
    07. currentdatetransactionhistory<BR>
    <BR>
    <B>{environment_instance_name} ENV @ {datetime.today()}.</B>
    <BR>
    """
    subject = f"CC24 Tables backup on {environment_instance_name} @{datetime.today().strftime(r'%d-%b-%Y %H:%M:%S')}"
    sendmail_with_html_and_attachment(html_content, subject, glob(f"./LogFiles/CC24_Tables_bk.log"))
    print(f"Backup of CC24 Tables are done & Mail Sent at {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}")

except Exception as error:
    print(f"Error cc24tablebk.py = {error}")    


if __name__ == "__main__":
    pass