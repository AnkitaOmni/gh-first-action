import os
import pandas as pd
from glob import glob
from config import Config
from datetime import datetime
from file_transfer import file_transfer
from database import DatabaseConnections
from retailer_daily_monthly_report import RetailerReports
from sendmail_alerts import sendmail_with_html_and_attachment


conf = Config()
acqMoreIssMissData = issMoreAcqMissData = acqorgDec_issrevsuc = None
db = DatabaseConnections()
engine = db.mysql_connection()
reportLoc = f"./CompensationReports/ConciliationReports/{datetime.now().strftime(r'%b_%Y')}"
reportNameP1MissAtAcq = f"ApproveMissingAtAcquirer_{datetime.now().strftime(r'%Y%m%d')}.csv"
reportNameP1MissAtIss = f"ApproveMissingAtIssuer_{datetime.now().strftime(r'%Y%m%d')}.csv"
reportNameacqorgDec_issrevsuc = f"InternalReversal_{datetime.now().strftime(r'%Y%m%d')}.csv"
acqRevSucPurDec = f"AcquirerReversalSuccessPurchaceDecline"
renamedCols = {
    'MT': 'MessageType', 'PC': 'ProcessingCode', 'Brand': 'ForwardingInstitutionIdentification',
    'RC': 'ResponseCode', 'Switch': 'AcquiringInstitutionIdentification', 'RRN': 'RetrievalReferenceNumber',
    'CardNo': 'Track2Data', 'RetId': 'CardAcceptorIdentification', 'TrxDate': 'LocalTransactionDate',
    'TrxTime': 'LocalTransactionTime', 'TraceId': 'SystemsTraceAuditNumber', 'Channel': 'ChannelType',
    'Amt': 'TransactionAmount'
}
queryAcqMoreIssMiss = """call PhaseOne_AcqMoreIssMiss;"""
queryIssMoreAcqMiss = """call PhaseOne_IssMoreAcqMiss;"""
queryacqorgDec_issrevsuc = """CALL AcquirerOriginalDecline_IssuerReversalSuccess;"""


try:
    cursor = engine.cursor(buffered=True, dictionary=True)
    results = cursor.execute(queryAcqMoreIssMiss, multi=True)
    for cur in results:
        if cur.with_rows:
            acqMoreIssMissData=pd.DataFrame(cur.fetchall())
    if acqMoreIssMissData.empty:
        print("No Mismatch Transactions At Issuer Side")
    else:
        acqMoreIssMissData.rename(columns=renamedCols, inplace=True)
        acqMoreIssMissData.to_csv(f"{reportLoc}/{reportNameP1MissAtIss}", index=False)
        print(f"Report Name = {os.getcwd()}/{reportLoc.replace('./', '')}/{reportNameP1MissAtIss}")

    results = cursor.execute(queryIssMoreAcqMiss, multi=True)
    for cur in results:
        if cur.with_rows:
            issMoreAcqMissData=pd.DataFrame(cur.fetchall())
    if issMoreAcqMissData.empty:
        print("No Mismatch Transactions At Acquirer Side")
    else:
        issMoreAcqMissData.rename(columns=renamedCols, inplace=True)
        issMoreAcqMissData.to_csv(f"{reportLoc}/{reportNameP1MissAtAcq}", index=False)
        print(f"Report Name = {os.getcwd()}/{reportLoc.replace('./', '')}/{reportNameP1MissAtAcq}")
    
    results = cursor.execute(queryacqorgDec_issrevsuc, multi=True)
    for cur in results:
        if cur.with_rows:
            acqorgDec_issrevsuc=pd.DataFrame(cur.fetchall())
    if acqorgDec_issrevsuc.empty:
        print("No Decline Transactions At Acquirer Side Which is Reversal At Issuer Side")
    else:
        acqorgDec_issrevsuc.rename(columns=renamedCols, inplace=True)
        acqorgDec_issrevsuc.to_csv(f"{reportLoc}/{reportNameacqorgDec_issrevsuc}", index=False)
        print(f"Report Name = {os.getcwd()}/{reportLoc.replace('./', '')}/{reportNameacqorgDec_issrevsuc}")

except Exception as err:
    print(f"Error1 = {err.args}")

finally:
    engine.commit()
    engine.close()


try:
    create_report = RetailerReports(f"{reportLoc}/")
    create_report.acq_RevSucPurDec(acqRevSucPurDec)
    acq_report_old_file = f"./{reportLoc}/{acqRevSucPurDec}_{datetime.now().strftime(r'%y%m%d')}.csv"
    acq_report_new_file = f"./{reportLoc}/{acqRevSucPurDec}_{datetime.now().strftime(r'%Y%m%d')}.csv"
    os.rename(acq_report_old_file, acq_report_new_file)
except:
    print(f"AcquirerReversalSuccessPurchaceDecline File Not Found")



if __name__ == '__main__':
    pass

# * Commented By Dishant [11 Jul 2022] :- Do not delete this helps in testing
# print(f"Loc = {reportLoc}/{reportNameP1MissAtIss}")
# print(f"Loc = {reportLoc}/{reportNameacqorgDec_issrevsuc}")
# print(os.system(f"zip -Dm {reportLoc}/phase1_{datetime.now().strftime(r'%Y%m%d')}.zip {reportLoc}/*{datetime.now().strftime(r'%Y%m%d')}*"))
# print(os.system(f"ls -lthr {reportLoc}/*{datetime.now().strftime(r'%Y%m%d')}*"))
# print(reportLoc, f"/phase1_{datetime.now().strftime(r'%Y%m%d')}.zip", 
# f"/home/comp_prod_ftp/comp_repo/{datetime.now().strftime(r'%b_%Y')}/{datetime.now().strftime(r'%d-%b-%y')}/", 
# f"phase1_{datetime.now().strftime(r'%Y%m%d')}.zip")
# * Commented By Dishant [11 Jul 2022] :- Stop Making Zip & Backup FTP
# os.system(f"zip -Dm {reportLoc}/phase1_{datetime.now().strftime(r'%Y%m%d')}.zip {reportLoc}/*{datetime.now().strftime(r'%Y%m%d')}*")
# file_transfer(reportLoc, f"/phase1_{datetime.now().strftime(r'%Y%m%d')}.zip", 
# f"/home/comp_prod_ftp/comp_repo/{datetime.now().strftime(r'%b_%Y')}/{datetime.now().strftime(r'%d-%b-%y')}/", 
# f"phase1_{datetime.now().strftime(r'%Y%m%d')}.zip", host="192.168.1.87", username="comp_prod_ftp", password="comp_prod_ftp$2021")


# sendmail_with_html_and_attachment("<H3>PFA All Phase-One Reports.</H3>", 
# f"{conf.get_config_json().get('ENV_NAME', None)} Liquidation/Compensation Phase-One Reports {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}", 
# glob(f"{reportLoc}/*{datetime.now().strftime(r'%Y%m%d')}*"))



