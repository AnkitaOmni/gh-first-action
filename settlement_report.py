#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from peewee import fn
from datetime import datetime
from sendmail_alerts import sendmail_with_html_and_attachment
from model import ISERetailer, TransactionHistory, IssuerExtract, AcquirerExtract

today = datetime.now().strftime('%y%m%d')  # today's date format YYMMDD


def issuer_settlement_report():
  
    query1 = ISERetailer.select(
        ISERetailer.ForwardingInstitutionIdentification.alias('NAME'),
        fn.COUNT(ISERetailer.TransactionAmount).alias('COUNT'),
        fn.SUM(ISERetailer.TransactionAmount).alias('AMOUNT'),
        ISERetailer.MessageType.alias('MSG_TYP'),
        ISERetailer.ProcessingCode.alias('PRO_CODE'),
        fn.SUM(ISERetailer.TotalCommissions).alias('COMMISSIONS'),
        fn.SUM(ISERetailer.TotalTaxes).alias('TAXES'),
        fn.SUM(ISERetailer.FinalAmount).alias('NET_AMOUNT'),
    ).where(ISERetailer.ResponseCode == "00").group_by(ISERetailer.ForwardingInstitutionIdentification,
                                                       ISERetailer.MessageType,
                                                       ISERetailer.ProcessingCode).dicts()

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)
    print(data_frame.to_string())

    for x in data_frame.index:
        if data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Purchase'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Reversal'
        elif data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund Reversal'

        data_frame.loc[x, "NAME"] = issuer_is.get(
            data_frame.loc[x, "NAME"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        del data_frame["PRO_CODE"]
        del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['NAME', 'TYPE', 'COUNT', 'AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()


def acquirer_settlement_report():
    query1 = ISERetailer.select(
        ISERetailer.AcquiringInstitutionIdentification.alias('NAME'),
        fn.COUNT(ISERetailer.TransactionAmount).alias('COUNT'),
        fn.SUM(ISERetailer.TransactionAmount).alias('AMOUNT'),
        ISERetailer.MessageType.alias('MSG_TYP'),
        ISERetailer.ProcessingCode.alias('PRO_CODE'),
        fn.SUM(ISERetailer.TotalCommissions).alias('COMMISSIONS'),
        fn.SUM(ISERetailer.TotalTaxes).alias('TAXES'),
        fn.SUM(ISERetailer.FinalAmount).alias('NET_AMOUNT'),
    ).where(ISERetailer.ResponseCode == "00").group_by(ISERetailer.AcquiringInstitutionIdentification,
                                                       ISERetailer.MessageType,
                                                       ISERetailer.ProcessingCode).dicts()

    acquirer_is = {'0012': 'Geo Pagos',
                   '0014': 'Alvi', '2003': 'Digital Acquirer'}

    data_frame = pd.DataFrame(query1)
    # print(data_frame.to_string())

    for x in data_frame.index:
        if data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Purchase'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Reversal'
        elif data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund Reversal'

        data_frame.loc[x, "NAME"] = acquirer_is.get(
            data_frame.loc[x, "NAME"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        del data_frame["PRO_CODE"]
        del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['NAME', 'TYPE', 'COUNT',
                                 'AMOUNT', 'COMMISSIONS', 'TAXES', 'NET_AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()



def acquirer_issuer_settlement_report():
    query1 = ISERetailer.select(
        ISERetailer.AcquiringInstitutionIdentification.alias('ACQUIRER'),
        ISERetailer.ForwardingInstitutionIdentification.alias('ISSUER'),
        ISERetailer.MessageType.alias('MSG_TYP'),
        ISERetailer.ProcessingCode.alias('PRO_CODE'),
        fn.COUNT(ISERetailer.TransactionAmount).alias('COUNT'),
        fn.SUM(ISERetailer.TransactionAmount).alias('AMOUNT'),
        fn.SUM(ISERetailer.TotalCommissions).alias('COMMISSIONS'),
        fn.SUM(ISERetailer.TotalTaxes).alias('TAXES'),
        fn.SUM(ISERetailer.FinalAmount).alias('NET_AMOUNT'),
    ).where(ISERetailer.ResponseCode == "00").group_by(ISERetailer.AcquiringInstitutionIdentification,
                                                       ISERetailer.ForwardingInstitutionIdentification,
                                                       ISERetailer.MessageType,
                                                       ISERetailer.ProcessingCode).dicts()

    # SELECT `t1`.`LocalTransactionDate` AS TXN_DATE,
    # `t1`.`AcquiringInstitutionIdentification` AS ACQUIRER,
    # `t1`.`ForwardingInstitutionIdentification` AS ISSUER,
    # `t1`.`MessageType` AS MSG_TYP,
    # `t1`.`ProcessingCode` AS PRO_CODE,
    # COUNT(`t1`.`CardAcceptorIdentification`) AS COUNT,
    # SUM(`t1`.`TransactionAmount`) AS AMOUNT,
    # SUM(`t1`.`TotalCommissions`) AS COMMISSIONS,
    # SUM(`t1`.`TotalTaxes`) AS TAXES,
    # SUM(`t1`.`FinalAmount`) AS NET_AMOUNT FROM `transactionhistory` AS t1
    # WHERE (`t1`.`ResponseCode` = "00") AND LocalTransactionDate BETWEEN "2021-05-01" AND "2021-05-05"
    # GROUP BY `t1`.`LocalTransactionDate`,
    # `t1`.`AcquiringInstitutionIdentification`,
    # `t1`.`ForwardingInstitutionIdentification`,
    # `t1`.`MessageType`,
    # `t1`.`ProcessingCode`

    acquirer_is = {'0012': 'Geo Pagos',
                   '0014': 'Alvi', '2003': 'Digital Acquirer'}

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)

    for x in data_frame.index:
        if data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Purchase'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Reversal'
        elif data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund Reversal'

        data_frame.loc[x, "ACQUIRER"] = acquirer_is.get(
            data_frame.loc[x, "ACQUIRER"], 'UnKnown')

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        del data_frame["PRO_CODE"]
        del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['ACQUIRER', 'ISSUER', 'TYPE',
                                 'COUNT', 'AMOUNT', 'COMMISSIONS', 'TAXES', 'NET_AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()


def acquirer_issuer_settlement_report1(first_date, last_date):
    first_date = datetime.strptime(first_date, "%Y-%m-%d")
    last_date = datetime.strptime(last_date, "%Y-%m-%d")

    query1 = TransactionHistory.select(
        TransactionHistory.LocalTransactionDate.alias('DATE'),
        TransactionHistory.AcquiringInstitutionIdentification.alias(
            'ACQUIRER'),
        TransactionHistory.ForwardingInstitutionIdentification.alias('ISSUER'),
        TransactionHistory.MessageType.alias('MSG_TYP'),
        TransactionHistory.ProcessingCode.alias('PRO_CODE'),
        fn.COUNT(TransactionHistory.TransactionAmount).alias('COUNT'),
        fn.SUM(TransactionHistory.TransactionAmount).alias('AMOUNT'),
        fn.SUM(TransactionHistory.TotalCommissions).alias('COMMISSIONS'),
        fn.SUM(TransactionHistory.TotalTaxes).alias('TAXES'),
        fn.SUM(TransactionHistory.FinalAmount).alias('NET_AMOUNT'),
    ).where(TransactionHistory.ResponseCode == "00",
            TransactionHistory.LocalTransactionDate.between(first_date, last_date)).group_by(TransactionHistory.LocalTransactionDate,
                                                                                             TransactionHistory.AcquiringInstitutionIdentification,
                                                                                             TransactionHistory.ForwardingInstitutionIdentification,
                                                                                             TransactionHistory.MessageType,
                                                                                             TransactionHistory.ProcessingCode).dicts()

    # SELECT `t1`.`LocalTransactionDate` AS TXN_DATE,
    # `t1`.`AcquiringInstitutionIdentification` AS ACQUIRER,
    # `t1`.`ForwardingInstitutionIdentification` AS ISSUER,
    # `t1`.`MessageType` AS MSG_TYP,
    # `t1`.`ProcessingCode` AS PRO_CODE,
    # COUNT(`t1`.`CardAcceptorIdentification`) AS COUNT,
    # SUM(`t1`.`TransactionAmount`) AS AMOUNT,
    # SUM(`t1`.`TotalCommissions`) AS COMMISSIONS,
    # SUM(`t1`.`TotalTaxes`) AS TAXES,
    # SUM(`t1`.`FinalAmount`) AS NET_AMOUNT FROM `transactionhistory` AS t1
    # WHERE (`t1`.`ResponseCode` = "00") AND LocalTransactionDate BETWEEN "2021-05-01" AND "2021-05-05"
    # GROUP BY `t1`.`LocalTransactionDate`,
    # `t1`.`AcquiringInstitutionIdentification`,
    # `t1`.`ForwardingInstitutionIdentification`,
    # `t1`.`MessageType`,
    # `t1`.`ProcessingCode`

    acquirer_is = {'0012': 'Geo Pagos',
                   '0014': 'Alvi', '2003': 'Digital Acquirer'}

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)

    for x in data_frame.index:
        if data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Purchase'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '000000':
            data_frame.loc[x, "TYPE"] = 'Reversal'
        elif data_frame.loc[x, "MSG_TYP"] == '0210' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund'
        elif data_frame.loc[x, "MSG_TYP"] == '0420' and data_frame.loc[x, "PRO_CODE"] == '200000':
            data_frame.loc[x, "TYPE"] = 'Refund Reversal'

        data_frame.loc[x, "ACQUIRER"] = acquirer_is.get(
            data_frame.loc[x, "ACQUIRER"], 'UnKnown')

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        del data_frame["PRO_CODE"]
        del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['DATE', 'ACQUIRER', 'ISSUER', 'TYPE',
                                 'COUNT', 'AMOUNT', 'COMMISSIONS', 'TAXES', 'NET_AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()


def issuer_count_at_issuer():
    query1 = IssuerExtract.select(
        IssuerExtract.ForwardingInstitutionIdentification.alias('ISSUER'),
        fn.COUNT(IssuerExtract.TransactionAmount).alias('COUNT'),
        fn.SUM(IssuerExtract.TransactionAmount).alias('AMOUNT')
    ).where(IssuerExtract.ResponseCode == "00").group_by(IssuerExtract.ForwardingInstitutionIdentification).dicts()

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)
    # print(data_frame.to_string())

    for x in data_frame.index:

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
    #     # delete message and processing code columns
    #     # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
    #     # data_frame.pop("MSG_TYP")
    #     del data_frame["PRO_CODE"]
    #     del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['ISSUER', 'COUNT', 'AMOUNT']]
    #     # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
    #     # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()


def issuer_count_at_acquirer():
    query1 = AcquirerExtract.select(
        AcquirerExtract.ForwardingInstitutionIdentification.alias('ISSUER'),
        fn.COUNT(AcquirerExtract.TransactionAmount).alias('COUNT'),
        fn.SUM(AcquirerExtract.TransactionAmount).alias('AMOUNT')
    ).where(AcquirerExtract.ResponseCode == "00").group_by(AcquirerExtract.ForwardingInstitutionIdentification).dicts()

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)
    # print(data_frame.to_string())

    for x in data_frame.index:

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
    #     # delete message and processing code columns
    #     # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
    #     # data_frame.pop("MSG_TYP")
    #     del data_frame["PRO_CODE"]
    #     del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['ISSUER', 'COUNT', 'AMOUNT']]
    #     # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
    #     # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()

def acquirer_count():
    query1 = AcquirerExtract.select(
        AcquirerExtract.AcquiringInstitutionIdentification.alias('ACQUIRER'),
        AcquirerExtract.ForwardingInstitutionIdentification.alias('ISSUER'),
        fn.COUNT(AcquirerExtract.TransactionAmount).alias('COUNT'),
        fn.SUM(AcquirerExtract.TransactionAmount).alias('AMOUNT')
    ).where(AcquirerExtract.ResponseCode == "00").group_by(AcquirerExtract.AcquiringInstitutionIdentification,
                                                       AcquirerExtract.ForwardingInstitutionIdentification).dicts()

    acquirer_is = {'0012': 'Geo Pagos',
                   '0014': 'Alvi', '2003': 'Digital Acquirer'}

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)
    # print(data_frame.to_string())

    for x in data_frame.index:
        

        data_frame.loc[x, "ACQUIRER"] = acquirer_is.get(
            data_frame.loc[x, "ACQUIRER"], 'UnKnown')

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        # del data_frame["PRO_CODE"]
        # del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['ACQUIRER', 'ISSUER', 'COUNT', 'AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()

def issuer_count():
    query1 = IssuerExtract.select(
        IssuerExtract.AcquiringInstitutionIdentification.alias('ACQUIRER'),
        IssuerExtract.ForwardingInstitutionIdentification.alias('ISSUER'),
        fn.COUNT(IssuerExtract.TransactionAmount).alias('COUNT'),
        fn.SUM(IssuerExtract.TransactionAmount).alias('AMOUNT')
    ).where(IssuerExtract.ResponseCode == "00").group_by(IssuerExtract.AcquiringInstitutionIdentification,
                                                       IssuerExtract.ForwardingInstitutionIdentification).dicts()

    acquirer_is = {'0012': 'Geo Pagos',
                   '0014': 'Alvi', '2003': 'Digital Acquirer'}

    issuer_is = {'2001': 'Master Card', '2002': 'Maestro', '8051': 'Visa'}

    data_frame = pd.DataFrame(query1)
    # print(data_frame.to_string())

    for x in data_frame.index:
        

        data_frame.loc[x, "ACQUIRER"] = acquirer_is.get(
            data_frame.loc[x, "ACQUIRER"], 'UnKnown')

        data_frame.loc[x, "ISSUER"] = issuer_is.get(
            data_frame.loc[x, "ISSUER"], 'UnKnown')

    if not data_frame.empty:
        # delete message and processing code columns
        # data_frame.drop(['MSG_TYP', 'PRO_CODE'], inplace=True)
        # data_frame.pop("MSG_TYP")
        # del data_frame["PRO_CODE"]
        # del data_frame["MSG_TYP"]

        # re align column positions
        data_frame = data_frame[['ACQUIRER', 'ISSUER', 'COUNT', 'AMOUNT']]
        # column_names = ['NAME', 'TYPE', 'COUNT', 'AMOUNT']
        # data_frame = data_frame.reindex(columns=column_names)

    return data_frame  # .to_string()

def csv_to_html(filename='CompensationReports/RetailerReports/BRAND_Summary_{}.csv'.format(today)):
    csv = pd.read_csv(filename)

    # to save as html file named as "Table"
    # csv.to_html("Table.htm")

    # assign it to csv variable (string)
    html_file = csv.to_html()
    return html_file


def dataframe_to_html(dataframe):
    # to save as html file named as "Table"
    # csv.to_html("Table.htm")

    # assign it to csv variable (string)
    html_file = dataframe.to_html(
        index=False, classes='table table-sm table-bordered', justify='left')
    return html_file


def mail_layout():
    # issuer_df = issuer_settlement_report()
    acquirer_issuer_df = acquirer_issuer_settlement_report()

    # issuer_html = dataframe_to_html(issuer_df)
    acquirer_html = dataframe_to_html(acquirer_issuer_df)
    # * Added For testng by Dishant [30July2021] :- PL 196 testing 
    # print(issuer_df)
    # print("\n")
    # print(acquirer_issuer_df)

    # html = '<h3><b> Liquidation process has been run successfully </b></h3><br>'
    # html += issuer_html
    # html += acquirer_html

    html = """  
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-GB">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Demystifying Email Design</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <style type="text/css">
  </style>

</head>

<body style="margin: 0; padding: 0;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
    <tbody>
      <tr>
        <td style="padding: 10px 0 10px 0;">

          <table align="center" border="0" cellpadding="0" cellspacing="0" width="97%" style="">
            <tbody>


              <tr>
                <td bgcolor="#ffffff" style="padding: 10px 10px 10px 10px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                    <tbody>
                      <tr>
                        <td style="color: #153643; font-family: Verdana, sans-serif;">
                          <h3 style="margin: 0;">Liquidation process has been run successfully.</h3>
                        </td>
                      </tr>

                      
                      <tr>
                        <td>
                          <table border="0" cellpadding="0" cellspacing="0" width="100%"
                            style="border-collapse: collapse;">
                            <tbody>
                              <tr>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;">Acquirer</p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          {acquirer}
                                        </td>
                                      </tr>


                                    </tbody>
                                  </table>
                                </td>
                                <td style="line-height: 0;" width="20">&nbsp;</td>
                                <td width="260" valign="top">
                                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                    style="border-collapse: collapse;">
                                    <tbody>
                                      <tr>
                                        <td
                                          style="color: #153643; font-family: Verdana, sans-serif;  line-height: 24px; padding: 25px 0 0 0;">
                                          <p style="margin: 0;"></p>
                                        </td>
                                      </tr>
                                      <tr>
                                        <td>
                                          
                                        </td>
                                      </tr>

                                    </tbody>
                                  </table>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </td>
              </tr>

            </tbody>
          </table>

        </td>
      </tr>
    </tbody>
  </table>


</body>

</html>

""".format(acquirer=acquirer_html)

    return html


if __name__ == "__main__":
    # issuer_df = issuer_settlement_report()
    # acquirer_df = acquirer_settlement_report()
    # acq_iss = acquirer_issuer_settlement_report()
    # acq_iss1 = acquirer_issuer_settlement_report1("2021-05-01", "2021-05-06")
    # print(issuer_df)
    # print("\n")
    # print(acquirer_df)
    # print("\n")
    # print(acq_iss)
    # print("\n")
    # print(acq_iss1)
    # print(mail_layout())

    # issuer_html = dataframe_to_html(issuer_df)
    # print(issuer_html)

    # html_content = mail_layout()
    # # print(html_content)

    # subject = 'Liquidation/Compensation Processed At {}'.format(
    #     datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    # sendmail_as_html(html_content, subject, filename='liquidation_jobs.log')

    # sendmail_as_html('<h3><b> Liquidation process has been run successfully </b></h3><br> {}'.format(issuer_html), subject, filename='liquidation_jobs.log')
    # issuer = dataframe_to_html(issuer_count_at_issuer())
    # acquirer = dataframe_to_html(acquirer_count())
    # print(issuer)
    # print("\n")
    # print(acquirer)
    # print("\n")


    # details = """<h3>Report Generation Completed. Please Start Verification.<p>Zip Loaction : {}{}</p></h3>""".format(zip_backup_loc, zip_file_name)
    # sendmail_with_html_and_attachment(html_content = details, mail_subject="NEW_CERT Liquidation Internal Alert")


    pass

