
# * Author          :- Ankita Harad
# * Created Date    :- 15/Jan/2023
# * Updated Date    :- 15/Jan/2023
# * Description     :- To Verify Production env cache, Input Location Files, Cronjob and Prod UI 
# * Usage           :- sh ProdLookUp.sh || ./ProdLookUp.sh


from glob import glob
from os import system
from datetime import date, datetime
from sendmail_alerts import sendmail_with_html_and_attachment

currentDate = date.today()
environment_instance_name = "ColDocker-QA"

try:

    system(f"sh ./Scripts/QALookUp.sh > ./LogFiles/QALookUp.log 2>&1")

    html_content = f"""
    Dear Team,
    <br><br>
    Please find cronjob, Cache, Input Location Files and ColDocker-QA UI status from {environment_instance_name} Environment at {datetime.today()}.
    """
    subject = f"Compensation {environment_instance_name} Look Up At {currentDate.strftime('%d %b %Y')}"
    sendmail_with_html_and_attachment(html_content, subject, glob(f"./LogFiles/ProdLookUp.log"))
    print(f"ColDocker-QA Look Up Done & Mail Sent at {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}")

except Exception as error:
    print(f"Error ProdLookUp.py = {error}")    


if __name__ == "__main__":
    pass