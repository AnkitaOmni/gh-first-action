import os
import collections
from model import *
from peewee import fn
from datetime import datetime
from dateutil.relativedelta import relativedelta
from jinja2 import Environment, FileSystemLoader, Template, meta


def deposit_report_genrator(temp_name, filename, header, sub_header, data, control, trailer):
    dates = datetime.now().strftime("%Y%m%d")
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(temp_name)
    template_source = env.loader.get_source(env, temp_name)[0]
    parsed_content = env.parse(template_source)
    variables = meta.find_undeclared_variables(parsed_content)
    with open(filename, 'w') as f:
        f.write(template.render(records=data, dates=dates, header=header,
                                sub_header=sub_header, control=control, trailer=trailer))


def prepare_header(DATE, TIME):
    '''
    HED = 55

    '''
    header = collections.OrderedDict()

    header["TIPO-H-T"] = "H"  # length 1 - character
    header["TIPO-ARCHIVO"] = "PNA"  # length 3 - character
    header["LIBRE-1"] = "INYECTOR".ljust(10, ' ')  # length 10 - character
    header["RUT-EMPRESA"] = '0766931839'  # length 10 - int
    header["LIBRE-2"] = '001111111111111'  # length 15 - character
    header["FECHA-ENIVO"] = DATE  # length 8 YYYYMMDD - int
    header["HORA-ENIVO"] = TIME.ljust(8, ' ')  # length 6 - character

    return header


def prepare_sub_header(AAC, DATE, TIME):
    '''
    SUB-HED = 450

    AAC - Assigned Agreement Code 

    '''
    sub_header = collections.OrderedDict()

    sub_header["TIPO-DE-REGISTRO"] = "1"  # length 1 - int
    sub_header["RUT-EMPRESA"] = "76693183".rjust(9, '0')  # length 9 - int
    sub_header["DIGITO-VERIFICADOR"] = "9"  # length 1 - character
    # length 10 - int
    sub_header["ODIGO-CONVENIO"] = '{}'.format(AAC).rjust(10, '0')
    sub_header["LIBRE"] = ' '*11  # length 11 - character
    sub_header["FECHA-GENERACION"] = DATE  # length 8 YYYYMMDD - int
    sub_header["FECHA-PROCESO"] = DATE  # length 8 YYYYMMDD - int
    sub_header["HORA-GENERACION"] = TIME  # length 6 - int
    sub_header["CODIGO-DE-OPERACION-CCA"] = "0000000000"  # length 10 - int
    sub_header["NUMERO DE NOMINA"] = "000000"  # length 6 - int
    sub_header["DATOS-LIBRES-1"] = "0"*13  # length 13 - alphanumeric
    sub_header["DATOS-LIBRES-2"] = "0"*367  # length 367 - character

    return sub_header


def prepare_body_psp(TaxID, DV, TLA, ACT_ID, MV_TYP, SBC, NO):
    '''
    BODY = 450

    TaxID - Tax ID [DEMO_TAXID]
    TLA - Total Liqidation Amount
    ACT_ID - Account ID [1]
    MV_TYP - Type Of Movement [01]
    SBC - Settlement Bank Code
    NO - Name Officer
    DV - Digital Verification

    '''
    body = []

    record = collections.OrderedDict()

    record["TIPO-REG"] = '2'  # length 1 - int
    # length 9 - int - TaxID ??????
    record["RUT-CLIENTE"] = "{}".format(TaxID).rjust(9, '0')
    record["DIGITO-VERIFICADOR"] = '{}'.format(DV)  # length 1 - character
    # length 60 - character
    record["NOMBRE-FUNCIONARIO"] = "{}".format(NO).ljust(60, ' ')
    # length 17 - int [COME FROM ACT ID] ??????
    record["NUMERO-DE-CUENTA"] = "{}".format(ACT_ID).rjust(17, '0')
    # length 11 - int - optional invoice number
    record["NUMERO-DE-FACTURA"] = "0"*11
    # length 2 - int [Taking 01 only] MOVEMENT TYPE ????
    record["TIPO-DE-MOVIMIENTO"] = "{}".format(MV_TYP).rjust(2, '0')
    # length 3 - int [Settlement Bank Code from OmniUI] ????
    record["CODIGO-DE-BANCO"] = "{}".format(SBC).rjust(3, '0')
    record["05-CODIGO-DE-SUCURSAL"] = "000"  # length 3 - int
    record['CODIGO SECTOR FINANCIERO'] = "00"  # lenght 2 -int
    # length 13 - int [Total Liquidation Amount: Purchase Amount for that Merchant minus the fees.] ?????
    record["MONTO"] = "{}".format(TLA).rjust(13, '0')
    record["CODIGO-PROPIO-EMPRESA"] = "0"*15  # length 15 - int
    record["NUMERO-DE-CUENTA-DE-CARGO"] = "00003066003"  # length 11 - int
    record["Glosa-Pagos-Masivos"] = "0"*245  # length 245 - character
    record["Datos-Libre-1"] = " "*5  # length 5 - character
    record["Identificador-de-pago-masivo"] = " "*10  # length 10 - character
    record["Identificador-de-dato"] = " "*7  # length 7 - character
    record["DATOS-LIBRE-2"] = " "*35  # length 35 - character

    body.append(record)

    return body


def prepare_body_npsp(TaxID, DV, TLA, ACT_ID, MV_TYP, SBC, NO):
    '''
    BODY = 450

    TaxID - Tax ID
    TLA - Total Liqidation Amount
    ACT_ID - Account ID
    MV_TYP - Type Of Movement
    SBC - Settlement Bank Code 
    NO - Name Officer
    DV - Digital Verification

    '''

    record = collections.OrderedDict()

    record["TIPO-REG"] = '2'  # length 1 - int
    # length 9 - int - TaxID ??????
    record["RUT-CLIENTE"] = "{}".format(TaxID).rjust(9, '0')
    record["DIGITO-VERIFICADOR"] = '{}'.format(DV)  # length 1 - character
    # length 60 - character
    record["NOMBRE-FUNCIONARIO"] = "{}".format(NO).ljust(60, ' ')
    # length 17 - int [COME FROM ACT ID] ??????
    record["NUMERO-DE-CUENTA"] = "{}".format(ACT_ID).rjust(17, '0')
    # length 11 - int - optional invoice number
    record["NUMERO-DE-FACTURA"] = "0"*11
    # length 2 - int [Taking 01 only] MOVEMENT TYPE ????
    record["TIPO-DE-MOVIMIENTO"] = "{}".format(MV_TYP).rjust(2, '0')
    # length 3 - int [Settlement Bank Code from OmniUI] ????
    record["CODIGO-DE-BANCO"] = "{}".format(SBC).rjust(3, '0')
    record["05-CODIGO-DE-SUCURSAL"] = "000"  # length 3 - int
    record['CODIGO SECTOR FINANCIERO'] = "00"  # lenght 2 -int
    # length 13 - int [Total Liquidation Amount: Purchase Amount for that Merchant minus the fees.] ?????
    record["MONTO"] = "{}".format(TLA).rjust(13, '0')
    record["CODIGO-PROPIO-EMPRESA"] = "0"*15  # length 15 - int
    record["NUMERO-DE-CUENTA-DE-CARGO"] = "00003066003"  # length 11 - int
    record["Glosa-Pagos-Masivos"] = "0"*245  # length 245 - character
    record["Datos-Libre-1"] = " "*5  # length 5 - character
    record["Identificador-de-pago-masivo"] = " "*10  # length 10 - character
    record["Identificador-de-dato"] = " "*7  # length 7 - character
    record["DATOS-LIBRE-2"] = " "*35  # length 35 - character

    return record


def prepare_control(LT, NRT):
    '''
    CONTROL = 450

    LT - Liquidation Total
    NRT - Number Of Record Type To Sent

    '''
    control = collections.OrderedDict()

    control["TIPO-REG"] = '3'  # length 1 - int
    # length 15 - int [Liqidation Total]
    control["MONTO-A-PROCESAR"] = ("{}").format(str(LT)).rjust(15, "0")
    # length 7 - int [Number of Records Type 2 sent] ???
    control["CANTIDAD-DE-REG"] = ("{}".format(str(NRT))).rjust(7, "0")
    control["LIBRE"] = " "*427  # length 427 - character

    return control


def prepare_trailer(DATE, TIME):
    '''
    TRAILER = 55

    '''
    trailer = collections.OrderedDict()

    trailer["TIPO-H-T"] = "T"  # length 1 - character
    trailer["TIPO-ARCHIVO"] = "PNA"  # length 3 - character
    trailer["LIBRE-1"] = "INYECTOR".ljust(10, ' ')  # length 10 - character
    trailer["RUT-EMPRESA"] = '0766931839'  # length 10 - int
    trailer["LIBRE-2"] = '001111111111111'  # length 15 - character
    trailer["FECHA-ENIVO"] = DATE  # length 8 YYYYMMDD - int
    trailer["HORA-ENIVO"] = TIME.ljust(8, ' ')  # length 6 - character

    return trailer


def all_dep_rep(CD, PSPL, NPSPL):

    try:
        # print "\n\nPSP_L = ", PSPL
        # print "NPSP_L = ", NPSPL
        # print "Current Dir = ", CD

        # Get Date in YYMMDD
        today = datetime.now().strftime(r"%Y%m%d")
        
        # * ALL DEPOSIT REPORT GENERATION
        got_psp, got_npsp = 0, 0

        # * PSP Accumlation
        no = 1
        header, sub_header, body1, trailer = "", "", "", ""
        sum_tla, sum_nor = 0, 0
        fsum_tla, fsum_nor = "", ""
        sp = " "*427

        for k in PSPL:
            with open('{}{}_DEPOSIT_REPORT_{}.txt'.format(CD, k, today), 'rt') as f:
                lines1 = f.readlines()
            if no == 1:
                header = lines1[0]  # Header is same for all PSP
                sub_header = lines1[1]  # Sub-Header is same for all PSP
                body1 = lines1[2]  # Body for first PSP Only
                trailer = lines1[4]  # Trailer is same for all PSP

                # Check for Negative Signs
                if "-" in lines1[3][1:16]:
                    sum_tla = -int(str(lines1[3][1:16]).split("-")[1])
                else:
                    sum_tla = int(lines1[3][1:16])  # TLA
        
                sum_nor = int(lines1[3][16:23])  # NOR
                no += 1
                got_psp = 1

            else:
                body1 = body1 + lines1[2]

                # Check for Negative Signs
                if "-" in lines1[3][1:16]:
                    sum_tla = sum_tla - int(str(lines1[3][1:16]).split("-")[1])
                    sum_tla = str(sum_tla).rjust(15,"0") 
                else:
                    sum_tla = sum_tla + int(lines1[3][1:16])

                sum_nor = sum_nor + int(lines1[3][16:23])

        fsum_tla = str(sum_tla).rjust(15, "0")
        fsum_nor = str(sum_nor).rjust(7, "0")
        psp_t = "3{}{}{}\n".format(fsum_tla, fsum_nor, sp)

        with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
            f.writelines(header)  # Header PSP
            f.writelines(sub_header)  # Sub Header PSP
            f.writelines(body1)  # Body PSP
            f.writelines(psp_t)  # Control PSP
            f.writelines(trailer)  # Trailer PSP

        # * NPSP Accumlation
        no_ = 1
        header_, sub_header_, body1_, trailer_ = "", "", "", ""
        sum_tla_, sum_nor_ = 0, 0
        fsum_tla_, fsum_nor_ = "", ""
        sp_ = " "*427

        for m in NPSPL:
            with open('{}{}_DEPOSIT_REPORT_{}.txt'.format(CD, m, today), 'rt') as f_:
                lines1_ = f_.readlines()

            if no_ == 1:
                header_ = lines1_[0]  # Header is same for all N-PSP
                # Sub-Header is same for all N-PSP
                sub_header_ = lines1_[1]
                body1_ = lines1_[2:-2]  # Body for first N-PSP Only
                trailer_ = lines1_[-1]  # Trailer is same for all N-PSP
                
                # Check for Negative Signs
                if "-" in lines1_[-2][1:16]:
                    sum_tla_ = -int(str(lines1_[-2][1:16]).split("-")[1])
                else:
                    sum_tla_ = int(lines1_[-2][1:16])  # TLA
                    
                sum_nor_ = int(lines1_[-2][16:23])  # NOR
                no += 1
                got_npsp = 1
                
            else:
                body1_ = body1_ + lines1_[2:-2]

                # Check for Negative Signs
                if "-" in lines1_[-2][1:16]:
                    sum_tla_ = sum_tla_ - int(str(lines1_[-2][1:16]).split("-")[1])
                    sum_tla_ = str(sum_tla_).rjust(15,"0") 
                else:
                    sum_tla_ = sum_tla_ + int(lines1_[-2][1:16])

                sum_nor_ = sum_nor_ + int(lines1_[-2][16:23])

        fsum_tla_ = str(sum_tla_).rjust(15, "0")
        fsum_nor_ = str(sum_nor_).rjust(7, "0")
        npsp_t = "3{}{}{}\n".format(fsum_tla_, fsum_nor_, sp_)

        with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
            f.writelines(header_)  # Header N-PSP
            f.writelines(sub_header_)  # Sub Header N-PSP
            f.writelines(body1_)  # Body N-PSP
            f.writelines(npsp_t)  # Control N-PSP
            f.writelines(trailer_)  # Trailer N-PSP

        if (got_psp == 1 and got_npsp == 1):
            with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_:
                lines11_ = f_.readlines()
            with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_:
                lines22_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
                f.writelines(lines11_)  # PSP
                f.writelines(lines22_)  # NPSP
            os.remove('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
            os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))

        elif (got_psp == 1 and got_npsp != 1):
            with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_:
                lines11_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f_:
                f_.writelines(lines11_)
            os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))

        elif (got_psp != 1 and got_npsp == 1):
            with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_:
                lines22_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f_:
                f_.writelines(lines22_)  # NPSP
            os.remove('{}{}_ALL_DEPOSIT_{}.txt'.format(
                CD, "NPSP", today))

        else:
            pass

        # * Just to make sure PSP & NPS Deposit Reports aee
        try:
            os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
        except Exception as e:
            pass

        try:
            os.remove('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
        except Exception as e:
            pass

        print ("All Deposit Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))


    except Exception as e:

        print ("All Deposit Report Not Generated")



def bank_deposit_trx_daily_details(c_dir):

    try:
        # For Incrementing Minutes
        inc_min = 0
        today_time = datetime.strptime(datetime.now().strftime(r'%d/%m/%Y %H:%M:%S.%f'), r'%d/%m/%Y %H:%M:%S.%f')
        # PSP & N-PSP & Blank List
        blank_l, psp_l, npsp_l = [], [], []
        # Get Date in YYMMDD
        today = datetime.now().strftime(r"%Y%m%d")
        # Query To Sort Transction Based On Channel_Type
        cqise = ISERetailer.select(ISERetailer.ChannelType).distinct().tuples()
        # Query Get Channel From ISERetailer
        cqins = InstitutionId.select().dicts()
        # List of Channel Names in ISERetailer
        chn_name_ise = [str(i1[0]) for i1 in cqise]
        # List of Channel Names in InstitutionID
        insid_data = [i2 for i2 in cqins]
        # print "\n", chn_name_ise  # ?
        # # print "\n", insid_data  # ?
        # print "\n"

        # For Loop On [ISERetailer Table Data]
        #CC026 changes Channel based deposit reports
        # for i3 in chn_name_ise:
        for i3 in chn_name_ise: 

            # * Get Incremented Time in HHMMSS
            inc_min += 1
            final_time = today_time + relativedelta(minutes = inc_min)
            HHMMSS = str(final_time).split(" ")[1].split(".")[0].replace(":","").strip()

            chn_name = i3
            for i4 in insid_data:
                # * [Collect Data]
                chnNameIns = i4['channel_name']
                chn_typ = i4['channel_type']
                assg_arg_code = str(i4["assigned_agreeement_code"])
                movment_typ = str(i4["movment_type"])
                act_id = str(i4["bank_account_number"])
                sett_bnk_code = str(i4["bank_code"])
                name_officer = str(i4['name_officer'])
                tx_id1 = str(i4['tax_id'])
                ins_id_code = str(i4['institution_id_code'])

                # * [Check For Channel]
                if chn_name == chnNameIns:
                    # * [Check For PSP]
                    if chn_typ == True:
                        # print "Found PSP = ", i3['institution_id_code'], "+" , i3['channel_name']  # ?

                        # * [Check For Check_Digit]
                        if len(tx_id1) == 0:
                            tax_id = "0"
                            chk_digit = " "
                        elif "-" in tx_id1:
                            chk_digit = tx_id1.split("-")[1]
                            tax_id = tx_id1.split("-")[0].replace(".", "")
                        else:
                            tax_id = tx_id1.replace(".", "")
                            chk_digit = " "

                        # * [Check For Empty Values]
                        if sett_bnk_code == "" or sett_bnk_code == " ": sett_bnk_code = "0"
                        if assg_arg_code == "" or assg_arg_code == " ": assg_arg_code = "0"
                        if name_officer == "" or name_officer == " ": name_officer = " "
                        if movment_typ == "" or movment_typ == " ": movment_typ = "0"
                        if chk_digit == "" or chk_digit == " ": chk_digit = " "
                        if tax_id == "" or tax_id == " ": tax_id = "0"
                        if act_id == "" or act_id == " ": act_id = "0"

                        # * [# print PSP DATA FETCHED]
                        # print "IIC, ACC, NO, Tax_ID, CD, BAN, MT, BC, CN = ", ins_id_code, assg_arg_code, name_officer, tax_id, chk_digit, act_id, movment_typ, sett_bnk_code, chn_name  # ? 

                        # * [GET APPROVED & REJECTED AMOUNT]
                        approved = ISERetailer.select(fn.SUM(ISERetailer.FinalAmount).alias('Final_Amount')).where(

                            (ISERetailer.ChannelType == chn_name) &

                            (((ISERetailer.MessageType == "0210") &
                                (ISERetailer.ProcessingCode.startswith('00')) &
                                (ISERetailer.ResponseCode == '00')) |

                                ((ISERetailer.MessageType == "0420") &
                                (ISERetailer.ProcessingCode.startswith('20')) &
                                (ISERetailer.ResponseCode == '00')))
                        ).dicts()

                        for i1 in approved:
                            # print "Approved = ", i1['Final_Amount']  # ?
                            app = i1['Final_Amount']
                            if str(app) == 'None':
                                app_amt = 0
                            else:
                                app_amt = int(app)

                        rejected = ISERetailer.select(fn.SUM(ISERetailer.FinalAmount).alias('Final_Amount')).where(

                            (ISERetailer.AcquiringInstitutionIdentification == ins_id_code) &
                            (ISERetailer.ChannelType == chn_name) &

                            (((ISERetailer.MessageType == "0420") &
                                (ISERetailer.ProcessingCode.startswith('00')) &
                                (ISERetailer.ResponseCode == "00")) |

                                ((ISERetailer.MessageType == "0210") &
                                (ISERetailer.ProcessingCode.startswith('20')) &
                                (ISERetailer.ResponseCode == "00")))
                        ).dicts()

                        for i2 in rejected:
                            # print "Rejected = ", i2['Final_Amount']  # ?
                            rej = i2['Final_Amount']
                            if str(rej) == 'None':
                                rej_amt = 0
                            else:
                                rej_amt = int(rej)

                        total_liq_amt = app_amt - rej_amt

                        # print "TLA = ", total_liq_amt

                        # * Add Up For Liq_Total For Trailer/Control
                        liq_total = total_liq_amt
                        # print(f'Liq Total = {chn_name}-{liq_total}') # ! TEST

                        header_output = prepare_header(today, HHMMSS)  # * HEADER
                        sub_header_output = prepare_sub_header(
                            assg_arg_code, today, HHMMSS)  # * SUB-HEADER
                        body_output = prepare_body_psp(
                            tax_id, chk_digit, total_liq_amt, act_id, movment_typ, sett_bnk_code, name_officer)   # * BODY

                        no_of_rec = "1"
                        control_output = prepare_control(liq_total, no_of_rec) # * CONTROL
                        trailer_output = prepare_trailer(today, HHMMSS) # * TRIALER
                        deposit_report_genrator("deposit_reports.html", "{}{}_DEPOSIT_REPORT_{}.txt".format(
                            c_dir, chn_name, today), header_output, sub_header_output, list(body_output), control_output, trailer_output)
                        
                        psp_l.append(chn_name)
                     
                        # print("\n")
                        # ! [PSP ENDS]

                    else:
                        # * [Check For NON-PSP]
                        # print "Found NON-PSP = ", i3['institution_id_code'], "+" , i3['channel_name']  # ?

                        # * [Check For Empty Values]
                        if assg_arg_code == "" or assg_arg_code == " ": assg_arg_code = "0"
                        if name_officer == "" or name_officer == " ": name_officer = " "
                        if movment_typ == "" or movment_typ == " ": movment_typ = "0"
                        if chn_name == "" or chn_name == " ": chn_name = " "

                        # print "IIC, ACC, NO, Tax_ID, CD, BAN, MT, BC, CN = ", ins_id_code, assg_arg_code, name_officer, tax_id, chk_digit, act_id, movment_typ, sett_bnk_code, chn_name  # ?

                        # * [Get Disinct Ret_ID]
                        uret_id = ISERetailer.select(ISERetailer.CardAcceptorIdentification).where(
                            ISERetailer.ChannelType == chn_name).distinct().dicts()
                        u_ret_id_list = [k1['CardAcceptorIdentification']
                                        for k1 in uret_id]

                        # print "Unique Ret ID = ", u_ret_id_list

                        liq_total = 0  # To Store Liqidation_Total
                        rec_list = [] # list of records

                        for uril in u_ret_id_list:
                            # Query For Current_Ret_ID Data
                            curr_retid_data = RetailerId.select().where(
                                RetailerId.RetailerId == uril).dicts()

                            if len(curr_retid_data) != 0:
                                # * To fetch values from query
                                # # print("Fetched_Values")
                                for crd in curr_retid_data:
                                    ret_id = crd['RetailerId']
                                    act_id = crd["AccountNumber"]
                                    sett_bnk_code = crd["BankCode"]
                                    tx_id1 = crd['IdentificationNumber']

                                    if len(act_id) == 0:
                                        act_id = "0"
                                    elif len(sett_bnk_code) == 0:
                                        sett_bnk_code = "0"

                                    if len(tx_id1) == 0:
                                        tax_id = "0"
                                        chk_digit = " "
                                    elif "-" in tx_id1:
                                        chk_digit = tx_id1.split("-")[1]
                                        tax_id = tx_id1.split("-")[0].replace(".", "")
                                    else:
                                        tax_id = tx_id1.replace(".", "")
                                        chk_digit = " "
                            else:
                                # ! To store default values
                                # # print("Default_Values")
                                ret_id = uril
                                tax_id = "0"
                                act_id = "0"
                                sett_bnk_code = "0"
                                chk_digit = " "

                            approved = ISERetailer.select(fn.SUM(ISERetailer.FinalAmount).alias('Final_Amount')).where(
                                (ISERetailer.CardAcceptorIdentification == uril) &
                                (ISERetailer.ChannelType == chn_name) &

                                (((ISERetailer.MessageType == "0210") &
                                (ISERetailer.ProcessingCode.startswith('00')) &
                                (ISERetailer.ResponseCode == '00')) |

                                ((ISERetailer.MessageType == "0420") &
                                (ISERetailer.ProcessingCode.startswith('20')) &
                                (ISERetailer.ResponseCode == '00')))
                            ).dicts()

                            for i1 in approved:
                                # print "Approved = ", i1['Final_Amount']  # ?
                                app = i1['Final_Amount']
                                if str(app) == 'None':
                                    app_amt = 0
                                else:
                                    app_amt = int(app)

                            rejected = ISERetailer.select(fn.SUM(ISERetailer.FinalAmount).alias('Final_Amount')).where(
                                (ISERetailer.CardAcceptorIdentification == uril) &
                                (ISERetailer.ChannelType == chn_name) &

                                (((ISERetailer.MessageType == "0420") &
                                (ISERetailer.ProcessingCode.startswith('00')) &
                                (ISERetailer.ResponseCode == "00")) |

                                ((ISERetailer.MessageType == "0210") &
                                (ISERetailer.ProcessingCode.startswith('20')) &
                                (ISERetailer.ResponseCode == "00")))
                            ).dicts()

                            for i2 in rejected:
                                # print "Rejected = ", i2['Final_Amount']  # ?
                                rej = i2['Final_Amount']
                                if str(rej) == 'None':
                                    rej_amt = 0
                                else:
                                    rej_amt = int(rej)

                            total_liq_amt = app_amt - rej_amt

                            # * Body/Details
                            rec_list.append(prepare_body_npsp(
                                tax_id, chk_digit, total_liq_amt, act_id, movment_typ, sett_bnk_code, name_officer))

                            # * Add Up For Liq_Total For Trailer/Control
                            liq_total = liq_total + total_liq_amt
                            # print(f'Liq Total = {chn_name}-{liq_total}') # ! TEST

                        # * Trailer
                        no_of_rec = len(rec_list)

                        header_output = prepare_header(today, HHMMSS)  # * HEADER
                        sub_header_output = prepare_sub_header(
                            assg_arg_code, today, HHMMSS)  # * SUB-HEADER

                        control_output = prepare_control(liq_total, no_of_rec)  # * CONTROL
                        trailer_output = prepare_trailer(today, HHMMSS) # * TRAILER
                        deposit_report_genrator("deposit_reports.html", "{}{}_DEPOSIT_REPORT_{}.txt".format(
                            c_dir, chn_name, today), header_output, sub_header_output, rec_list, control_output, trailer_output)
                        
                        npsp_l.append(chn_name)
                        # print("\n")
                        # ! [NON_PSP ENDS]


        # print "\nBlank List = ", blank_l
        # print "\nToday Date = ", today  # ?
        # print "HHMMSS = ", HHMMSS  # ?

        print("PSP & NON_PSP Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

        # * Call All Deposit Report Function
        all_dep_rep(CD=c_dir, PSPL=psp_l, NPSPL=npsp_l)



    except Exception as e:

        print("PSP & NON_PSP Report Not Generated", e,  e.args)



if __name__ == "__main__":
    # all_dep_rep(CD, PSPL, NPSPL)
    pass
