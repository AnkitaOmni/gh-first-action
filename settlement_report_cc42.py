#!/usr/bin/env python
# -*- coding: utf-8 -*-
from model import *
import pandas as pd
from peewee import fn
from datetime import datetime,date
from sendmail_alerts import sendmail_with_html_and_attachment
from model import NewISERetailer, TransactionHistory, IssuerExtract, AcquirerExtract

today = datetime.now().strftime('%y%m%d')  # today's date format YYMMDD
todays = date.today()


def acquirer_issuer_settlement_report():
    
    query1 = NewISERetailerTranxHistory.select(
        NewISERetailerTranxHistory.AcquiringInstitutionIdentification.alias('ACQUIRER'),
        NewISERetailerTranxHistory.ForwardingInstitutionIdentification.alias('ISSUER'),
        NewISERetailerTranxHistory.MessageType.alias('MSG_TYP'),
        NewISERetailerTranxHistory.ProcessingCode.alias('PRO_CODE'),
        fn.COUNT(NewISERetailerTranxHistory.TransactionAmount).alias('COUNT'),
        fn.SUM(NewISERetailerTranxHistory.TransactionAmount).alias('AMOUNT'),
        fn.SUM(NewISERetailerTranxHistory.TotalCommissions).alias('COMMISSIONS'),
        fn.SUM(NewISERetailerTranxHistory.TotalTaxes).alias('TAXES'),
        fn.SUM(NewISERetailerTranxHistory.FinalAmount).alias('NET_AMOUNT'),
    ).where((NewISERetailerTranxHistory.ResponseCode == "00") & NewISERetailerTranxHistory.TimeStamp % f'%{todays}%').group_by(NewISERetailerTranxHistory.AcquiringInstitutionIdentification,
                                                       NewISERetailerTranxHistory.ForwardingInstitutionIdentification,
                                                       NewISERetailerTranxHistory.MessageType,
                                                       NewISERetailerTranxHistory.ProcessingCode).dicts()

  

    acquirer_is = {'0012': 'Geo Pagos','0014': 'Alvi', '2003': 'Digital Acquirer'}

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


def dataframe_to_html(dataframe):
    # to save as html file named as "Table"
    # csv.to_html("Table.htm")

    # assign it to csv variable (string)
    html_file = dataframe.to_html(
        index=False, classes='table table-sm table-bordered', justify='left')
    return html_file


def mail_layout_cc42():
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
    pass

