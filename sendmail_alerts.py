import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import date, timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


today = datetime.now().strftime(r'%y%m%d')  # today's date format YYMMDD


def sendmail_with_html_and_attachment(html_content, mail_subject, attach_files=None):
    """
    * Send Mail Alerts With Html Content & Attachments
    """
    me = 'ColDocker-QA@omnipayments.com'
    recipients = ['dishant@omnipayments.com', 'ankita.harad@omnipayments.com']

    # * Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['From'] = me
    msg['To'] = ', '.join(recipients)

    # * Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(html_content, 'html')
    msg['Subject'] = mail_subject
    msg.attach(part1)

    if attach_files != None:
        try:
            for singleFile in attach_files:  # add files to the message
                baseFileName = os.path.basename(singleFile)
                # * Helps For Testing/Debug
                # print(f"Files = {singleFile} | {baseFileName}")
                attachment = MIMEApplication(open(singleFile, "rb").read(), _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', filename=baseFileName)
                msg.attach(attachment)
        except Exception as e1:
            # To Handel Multiple File Not Found Error
            print("Multiple File Attachment Failed. Error : {}".format(e1))

    # * Send Mail With All Attachments
    try:
        s = smtplib.SMTP('192.168.3.60', 7025)
        # s = smtplib.SMTP('192.168.1.225', 8125)
        s.sendmail(me, recipients, msg.as_string())
        s.quit()

    except smtplib.SMTPException as e:
        print('Error :{}'.format(e), 'error')


if __name__ == '__main__':
    pass

