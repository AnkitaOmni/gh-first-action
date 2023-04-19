import os
import collections
from model import *
from peewee import fn
from datetime import datetime
from CC042query import *
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
    ''' HED = 55 '''
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


def prepare_body(TaxID, DV, TLA, ACT_ID, MV_TYP, SBC, NO, check=None):
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

    if check == 'PSP':
        body.append(record)
        return body

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
    '''  TRAILER = 55  '''
    trailer = collections.OrderedDict()

    trailer["TIPO-H-T"] = "T"  # length 1 - character
    trailer["TIPO-ARCHIVO"] = "PNA"  # length 3 - character
    trailer["LIBRE-1"] = "INYECTOR".ljust(10, ' ')  # length 10 - character
    trailer["RUT-EMPRESA"] = '0766931839'  # length 10 - int
    trailer["LIBRE-2"] = '001111111111111'  # length 15 - character
    trailer["FECHA-ENIVO"] = DATE  # length 8 YYYYMMDD - int
    trailer["HORA-ENIVO"] = TIME.ljust(8, ' ')  # length 6 - character

    return trailer


def appr_rej_amt(first_query, second_query):
    approved = (NewISERetailer.select(fn.SUM(NewISERetailer.FinalAmount).alias('Final_Amount'))
                .where(first_query &
                       ((
                           (NewISERetailer.MessageType == "0210") &
                           (NewISERetailer.ProcessingCode.startswith('00')) &
                           (NewISERetailer.ResponseCode == '00')
                       ) | (
                           (NewISERetailer.MessageType == "0420") &
                           (NewISERetailer.ProcessingCode.startswith('20')) &
                           (NewISERetailer.ResponseCode == '00')
                       ))).dicts())

    for i1 in approved: app_amt = 0 if str(i1['Final_Amount']) == 'None' else int(i1['Final_Amount'])

    rejected = (NewISERetailer .select(fn.SUM(NewISERetailer.FinalAmount).alias('Final_Amount'))
                .where(second_query & 
                      ((
                        (NewISERetailer.MessageType == "0420") &
                        (NewISERetailer.ProcessingCode.startswith('00')) & 
                        (NewISERetailer.ResponseCode == "00")
                    ) | (
                        (NewISERetailer.MessageType == "0210") & 
                        (NewISERetailer.ProcessingCode.startswith('20')) & 
                        (NewISERetailer.ResponseCode == "00")
                    ))).dicts())

    for i2 in rejected: rej_amt = 0 if str(i2['Final_Amount']) == 'None' else int(i2['Final_Amount'])

    total_liq_amt = app_amt - rej_amt
    return total_liq_amt


def all_dep_rep(CD, PSPL, NPSPL):
    try:
        # print ("\n\nPSP_L = ", PSPL,"NPSP_L = ", NPSPL,"Current Dir = ", CD)
        today = datetime.now().strftime(r"%Y%m%d") # * YYMMDD
        got_psp, got_npsp = 0, 0 # * ALL DEPOSIT REPORT GENERATION

        # * PSP Accumlation
        no, sum_tla, sum_nor = 1, 0, 0
        header, sub_header, body1, trailer, fsum_tla, fsum_nor = "", "", "", "", "", ""
        sp = " "*427

        for k in PSPL:
            with open('{}{}_DEPOSIT_REPORT_{}.txt'.format(CD, k, today), 'rt') as f: lines1 = f.readlines()
            if no == 1:
                header, sub_header, body1, trailer = lines1[0], lines1[1], lines1[2], lines1[4]
                # Check for Negative Signs
                sum_tla = -int(str(lines1[3][1:16]).split("-")[1]) if "-" in lines1[3][1:16] else int(lines1[3][1:16])   # TLA
                sum_nor = int(lines1[3][16:23])  # NOR
                no += 1
                got_psp = 1
            else:
                body1 = body1 + lines1[2]
                # Check for Negative Signs
                if "-" in lines1[3][1:16]:
                    sum_tla = sum_tla - int(str(lines1[3][1:16]).split("-")[1])
                    sum_tla = str(sum_tla).rjust(15, "0")
                else: sum_tla = sum_tla + int(lines1[3][1:16])
                sum_nor = sum_nor + int(lines1[3][16:23])

        fsum_tla, fsum_nor = str(sum_tla).rjust(15, "0"), str(sum_nor).rjust(7, "0")
        psp_t = "3{}{}{}\n".format(fsum_tla, fsum_nor, sp)

        with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
            f.writelines(header)  # Header PSP
            f.writelines(sub_header)  # Sub Header PSP
            f.writelines(body1)  # Body PSP
            f.writelines(psp_t)  # Control PSP
            f.writelines(trailer)  # Trailer PSP

        # * NPSP Accumlation
        no_, sum_tla_, sum_nor_ = 1,  0, 0
        header_, sub_header_, body1_, trailer_,  fsum_tla_, fsum_nor_ = "", "", "", "", "", ""
        sp_ = " "*427

        for m in NPSPL:
            with open('{}{}_DEPOSIT_REPORT_{}.txt'.format(CD, m, today), 'rt') as f_: lines1_ = f_.readlines()
            if no_ == 1:
                # Header is same for all N-PSP,# Sub-Header is same for all N-PSP,# Body for first N-PSP Only,# Trailer is same for all N-PSP
                header_, sub_header_, body1_, trailer_ = lines1_[0], lines1_[1], lines1_[2:-2], lines1_[-1]
                # Check for Negative Signs
                sum_tla_ = -int(str(lines1_[-2][1:16]).split("-")[1]) if "-" in lines1_[-2][1:16] else int(lines1_[-2][1:16])  # TLA
                sum_nor_ = int(lines1_[-2][16:23])  # NOR
                no += 1
                got_npsp = 1

            else:
                body1_ = body1_ + lines1_[2:-2]
                # Check for Negative Signs
                if "-" in lines1_[-2][1:16]:
                    sum_tla_ = sum_tla_ - int(str(lines1_[-2][1:16]).split("-")[1])
                    sum_tla_ = str(sum_tla_).rjust(15, "0")
                else: sum_tla_ = sum_tla_ + int(lines1_[-2][1:16])

                sum_nor_ = sum_nor_ + int(lines1_[-2][16:23])

        fsum_tla_, fsum_nor_ = str(sum_tla_).rjust(15, "0"), str(sum_nor_).rjust(7, "0")
        npsp_t = "3{}{}{}\n".format(fsum_tla_, fsum_nor_, sp_)

        with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
            f.writelines(header_)  # Header N-PSP
            f.writelines(sub_header_)  # Sub Header N-PSP
            f.writelines(body1_)  # Body N-PSP
            f.writelines(npsp_t)  # Control N-PSP
            f.writelines(trailer_)  # Trailer N-PSP

        if (got_psp == 1 and got_npsp == 1):
            with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_: lines11_ = f_.readlines()
            with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_: lines22_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f:
                f.writelines(lines11_)  # PSP
                f.writelines(lines22_)  # NPSP

            os.remove('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
            os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))

        elif (got_psp == 1 and got_npsp != 1):
            with open('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_: lines11_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f_: f_.writelines(lines11_)
            os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))

        elif (got_psp != 1 and got_npsp == 1):
            with open('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today), 'r') as f_: lines22_ = f_.readlines()
            with open('{}ALL_DEPOSIT_{}.txt'.format(CD, today), 'w', newline="\r\n") as f_: f_.writelines(lines22_)  # NPSP
            os.remove('{}{}_ALL_DEPOSIT_{}.txt'.format(CD, "NPSP", today))

        else: pass

        # * Just to make sure PSP & NPS Deposit Reports aee
        try:os.remove('{}PSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
        except Exception as e: pass

        try: os.remove('{}NPSP_ALL_DEPOSIT_{}.txt'.format(CD, today))
        except Exception as e: pass

        print("All Deposit Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))

    except Exception as e: print("All Deposit Report Not Generated")


def bank_deposit_trx_daily_details_cc42(c_dir):  # CurrentDir_and_FolderName
    try:
        inc_min = 0                                    # For Incrementing Minutes
        blank_l, psp_l, npsp_l = [], [], []            # Blank,PSP & N-PSP List
        today_time = datetime.strptime(datetime.now().strftime(r'%d/%m/%Y %H:%M:%S.%f'), r'%d/%m/%Y %H:%M:%S.%f')  # 2023-02-07 05:34:23.941197
        today = datetime.now().strftime(r"%Y%m%d")     # Get Date in YYMMDD 20230207
        # Query To Sort Transction Based On Channel_Type in NewISERetailer Table
        uniq_chn_on_ise = NewISERetailer.select(NewISERetailer.ChannelType).distinct().tuples()
        # Query Get Channel From NewISERetailer
        data_on_insid = InstitutionId.select().dicts()

        # List of Channel Names in NewISERetailer
        chn_name_list_ise = [str(i1[0]) for i1 in uniq_chn_on_ise]
        # List of Channel Names in InstitutionID
        insid_data_list = [i2 for i2 in data_on_insid]

        for i3 in chn_name_list_ise:
            inc_min += 1                               # * Get Incremented Time in HHMMSS
            final_time = today_time + relativedelta(minutes=inc_min)
            HHMMSS = str(final_time).split(" ")[1].split(".")[0].replace(":", "").strip()

            chn_name = i3
            for i4 in insid_data_list:
                if chn_name == i4['channel_name']:
                    # * [Check For PSP]
                    if i4['channel_type'] == True:
                        # * [Check For Check_Digit]
                        if len(str(i4['tax_id'])) == 0:tax_id, chk_digit = "0", " "
                        elif "-" in str(i4['tax_id']): chk_digit, tax_id = str(i4['tax_id']).split("-")[1], str(i4['tax_id']).split("-")[0].replace(".", "")
                        else: tax_id, chk_digit = str(i4['tax_id']).replace(".", ""), " "

                        # * [Check For Empty Values]
                        if tax_id == "" or tax_id == " ": tax_id = "0"
                        if chk_digit == "" or chk_digit == " ": chk_digit = " "
                        if str(i4["bank_code"]) == "" or str(i4["bank_code"]) == " ": i4["bank_code"] = "0"
                        if str(i4["assigned_agreeement_code"]) == "" or str(i4["assigned_agreeement_code"]) == " ": i4["assigned_agreeement_code"] = "0"
                        if str(i4['name_officer']) == "" or str(i4['name_officer']) == " ": i4['name_officer'] = " "
                        if str(i4["movment_type"]) == "" or str(i4["movment_type"]) == " ": i4["movment_type"] = "0"
                        if str(i4["bank_account_number"]) == "" or str(i4["bank_account_number"]) == " ": i4["bank_account_number"] = "0"

                        liq_total,retaillist = 0,[]
                        data = combine_data(str(i4['institution_id_code']),chn_name)
                        for RCretid in data:
                            RcTrnx = Retailercompansation.select(Retailercompansation.RetailerId,Retailercompansation.CutOverDays,Retailercompansation.PendingDays).where((Retailercompansation.Channel == chn_name) & (Retailercompansation.RetailerId == RCretid) & (Retailercompansation.EntityId == str(i4['institution_id_code']))).distinct().tuples().execute()

                            NewIse_rId = [str(k[0]) for k in RcTrnx]
                            Ctoverday = [str(k[1]) for k in RcTrnx]
                            NewIse_Pday = [str(k[2]) for k in RcTrnx]
                            if len(NewIse_rId) != 0 and NewIse_Pday[0] == "0":
                                chn_query = (NewISERetailer.CardAcceptorIdentification == NewIse_rId[0]) & (NewISERetailer.ChannelType == chn_name)
                                ins_query = (NewISERetailer.AcquiringInstitutionIdentification == str(i4['institution_id_code'])) & (NewISERetailer.ChannelType == chn_name)
                                
                                total_liq_amt = appr_rej_amt(chn_query, ins_query)
                                # * Add Up For Liq_Total For Trailer/Control
                                liq_total = liq_total + total_liq_amt

                                retaillist.append(NewIse_rId[0])
                                Retailercompansation.update({Retailercompansation.PendingDays: Ctoverday[0]}).where((Retailercompansation.RetailerId == NewIse_rId[0]) & (Retailercompansation.Channel == chn_name) & (Retailercompansation.EntityId == str(i4['institution_id_code'])) & (Retailercompansation.PendingDays == 0)).execute()
                                
                            else:Retailercompansation.update({Retailercompansation.PendingDays: Retailercompansation.PendingDays -1}).where((Retailercompansation.Channel == chn_name) & (Retailercompansation.EntityId == str(i4['institution_id_code'])) & (Retailercompansation.RetailerId == RCretid )).execute()
                        
                        if len(retaillist) != 0:
                            copyToNewIsToTrnxHistory(retaillist,chn_name,str(i4['institution_id_code']))
                            delete_to_newiseretailer(retaillist,chn_name,str(i4['institution_id_code']))
                            

                        header_output = prepare_header(today, HHMMSS)
                        sub_header_output = prepare_sub_header(i4["assigned_agreeement_code"], today, HHMMSS)
                        body_output = prepare_body(tax_id, chk_digit, liq_total, i4["bank_account_number"], i4["movment_type"], i4["bank_code"], i4['name_officer'], check='PSP')
                        no_of_rec = "1"
                        control_output = prepare_control(liq_total, no_of_rec)
                        trailer_output = prepare_trailer(today, HHMMSS)
                        deposit_report_genrator("deposit_reports.html", "{}{}_TGR_DEPOSIT_REPORT_{}.txt".format(c_dir, chn_name, today), header_output, sub_header_output, list(body_output), control_output, trailer_output)
                        psp_l.append(chn_name)
                    else:
                        # * [Check For NON-PSP] print ("Found NON-PSP = ", i3['institution_id_code'], "+" , i3['channel_name'])
                        # * [Check For Empty Values]
                        if str(i4["assigned_agreeement_code"]) == "" or str(i4["assigned_agreeement_code"]) == " ": i4["assigned_agreeement_code"] = "0"
                        if str(i4['name_officer']) == "" or str(i4['name_officer']) == " ": i4['name_officer'] = " "
                        if str(i4["movment_type"]) == "" or str(i4["movment_type"]) == " ": i4["movment_type"] = "0"
                        if chn_name == "" or chn_name == " ": chn_name = " "

                        uret_id = NewISERetailer.select(NewISERetailer.CardAcceptorIdentification).where(NewISERetailer.ChannelType == chn_name).distinct().dicts()
                        u_ret_id_list = [k1['CardAcceptorIdentification'] for k1 in uret_id]

                        # To Store Liqidation_Total  # list of records
                        liq_total, rec_list,Retailer_id = 0, [],[]
                        # Query For Current_Ret_ID Data
                        for uril in u_ret_id_list:
                            RcTrnx = Retailercompansation.select(Retailercompansation.RetailerId,Retailercompansation.CutOverDays,Retailercompansation.PendingDays).where((Retailercompansation.Channel == chn_name)& (Retailercompansation.EntityId == str(i4['institution_id_code'])) & (Retailercompansation.RetailerId == uril) & (Retailercompansation.PendingDays == '0')).tuples()
                            RCretid = [str(k[0]) for k in RcTrnx]
                            Ctoverday = [str(k[1]) for k in RcTrnx]
                            if uril in RCretid:
                                curr_retid_data = RetailerId.select().where(RetailerId.RetailerId == uril).dicts()
                                if len(curr_retid_data) != 0:       # * To fetch values from query
                                    for crd in curr_retid_data:
                                        if len(crd["AccountNumber"]) == 0: crd["AccountNumber"] = "0"
                                        elif len(crd["BankCode"]) == 0: crd["BankCode"] = "0"

                                        if len(crd['IdentificationNumber']) == 0: tax_id, chk_digit = "0", " "
                                        elif "-" in crd['IdentificationNumber']: chk_digit, tax_id = crd['IdentificationNumber'].split("-")[1], crd['IdentificationNumber'].split("-")[0].replace(".", "")
                                        else: tax_id, chk_digit = crd['IdentificationNumber'].replace(".", ""), " "

                                else: crd['RetailerId'], tax_id, crd["AccountNumber"], crd["BankCode"], chk_digit = uril, "0", "0", "0", " " # ! To store default values

                                cid_chn_query = (NewISERetailer.CardAcceptorIdentification == uril) & (NewISERetailer.ChannelType == chn_name)
                                chn_query = (NewISERetailer.CardAcceptorIdentification == uril) & (NewISERetailer.ChannelType == chn_name)

                                total_liq_amt = appr_rej_amt(cid_chn_query, chn_query)
                                # * Add Up For Liq_Total For Trailer/Control
                                liq_total = liq_total + total_liq_amt

                                Retailer_id.append(uril)

                                # * Body/Details
                                rec_list.append(prepare_body(tax_id, chk_digit, total_liq_amt, crd["AccountNumber"], i4["movment_type"], crd["BankCode"], i4['name_officer']))
                                

                                Retailercompansation.update({Retailercompansation.PendingDays: Ctoverday[0]}).where(
                                                (Retailercompansation.RetailerId == RCretid[0]) & (Retailercompansation.Channel == chn_name) &
                                                (Retailercompansation.EntityId == str(i4['institution_id_code'])) & (Retailercompansation.PendingDays == '0')).execute()
                                
                            else:Retailercompansation.update({Retailercompansation.PendingDays: Retailercompansation.PendingDays -1}).where(
                                                (Retailercompansation.RetailerId == uril) & (Retailercompansation.Channel == chn_name) &
                                                (Retailercompansation.EntityId == str(i4['institution_id_code']))).execute()

                        if len(Retailer_id) != 0:
                            copyToNewIsToTrnxHistory(Retailer_id,chn_name,str(i4['institution_id_code']))
                            delete_to_newiseretailer(Retailer_id,chn_name,str(i4['institution_id_code']))


                        no_of_rec = len(rec_list)   # * Trailer
                        header_output = prepare_header(today, HHMMSS)
                        sub_header_output = prepare_sub_header(i4["assigned_agreeement_code"], today, HHMMSS)
                        control_output = prepare_control(liq_total, no_of_rec)
                        trailer_output = prepare_trailer(today, HHMMSS)
                        deposit_report_genrator("deposit_reports.html", "{}{}_TGR_DEPOSIT_REPORT_{}.txt".format(c_dir, chn_name, today), header_output, sub_header_output, rec_list, control_output, trailer_output)

                        npsp_l.append(chn_name)

        print("PSP & NON_PSP Report Generated at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
        # * Call All Deposit Report Function
        # all_dep_rep(CD=c_dir, PSPL=psp_l, NPSPL=npsp_l)

    except Exception as e:
        print("PSP & NON_PSP Report Not Generated", e,  e.args)


if __name__ == "__main__":
    # all_dep_rep(CD, PSPL, NPSPL)
    pass