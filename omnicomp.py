# -*- coding: utf-8 -*-

"""
    OmniCompensator
    OmniPayments Inc,
    compensationfactory@omnipayments.com 
    :# copyright #: (C) 2023 by OmniPayments Inc

"""

import re, os
from acl import *
from model import *
from utils import *
import glob, csv, ast
import shutil, queries
from logging import DEBUG
from make_hashmap import *
from functools import wraps
from datetime import date as dt
from datetime import datetime, timedelta
from database import DatabaseConnections
from werkzeug.utils import secure_filename
from make_csv_from_rrn import make_extract
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (Flask, redirect, url_for, render_template, request, flash, send_from_directory, jsonify, session)



################## * Constants/Variables * ##################

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
SECRET_KEY="069511e4c31117d1e98ae9619f7a3703e3d03f575255f1bc"

# * Everyday Extract Files
input_extract_file_name = "OMNIEXTRACT_REPORT_"
input_extract_file_loc =   "./AcquirerExtract/InputExtracts/"
fullday_input_extract_file_loc = "./AcquirerExtractFullDay/InputExtracts/"

# * RRN To Extract File
input_rrn_file_name = "RRN_LIST_"
input_rrn_file_loc =   "./RRNFiles/InputFiles/"
output_rrn_file_loc =   f"./RRNFiles/OutputExtracts/{datetime.now().strftime(r'%b_%Y')}/"

# * Adjustment File
file_adjust_loc = "./MastercardIPM/OutputCSV/"

# * SqlAlchemy Engine
db = DatabaseConnections()
myDB = db.peewee_connection()


################## * App Utility * ##################

def get_date():
    """ Return current date """
    return str(datetime.now().date())


def format_datetime(timestamp):
    """ Format a timestamp for display """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d_%H:%M')


def add_space(label):
    return re.sub(r"(\w)([A-Z])",r"\1 \2",label)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_id(username):
    """ Convenience method to look up the id for a username """
    try:
        rv = Users.get(Users.username == username)
    except Exception as e:
        rv = None
    return rv if rv else None


def check_password_strong(passwd):
    error = ""
    if len(passwd) < 8:
        error = "8 digits long"
    if passwd.islower():
        error = error+"Uppercase letter"
    if passwd.isupper():
        error = error+"Lowercase letter"
    if not any(c.isdigit() for c in passwd):
        error = error+" Number"
    if passwd.isdigit():
        error = error+"Any letter"
    return error if error else 0


################## * App Config * ##################

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.logger.setLevel(DEBUG)
app.secret_key = SECRET_KEY
app.config.from_object(__name__)
app.jinja_env.filters['add_space'] = add_space
app.jinja_env.filters['datetimeformat'] = format_datetime

################## * App Common * ##################

@app.before_request
def _db_connect():
    myDB.connect()


@app.teardown_request
def _db_close(exc):
    if not myDB.is_closed():
        myDB.close()


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html")


################## * LOGIN REQUIRED * ##################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


################## * All Endpoints * ##################

@app.get('/')
@login_required
def home():   
    FMT ='%H:%M:%S'
    currentTime = datetime.now().strftime(f"{FMT}")
    print('############ ui data',queries.UI_HomeTab())
    retailerCount, invalidApprovedCount, distRespCodes, iseRetCnt, issExtCpCnt, brandCnt, switchCnt = queries.UI_HomeTab()
    retailerLoadTime = str(datetime.strptime("22:35:00", FMT) - datetime.strptime(currentTime, FMT)).replace("-1 day,", "")
    phaseOneTime = str(datetime.strptime("22:45:00", FMT) - datetime.strptime(currentTime, FMT)).replace("-1 day,", "")
    phaseTwoTime = str(datetime.strptime("23:59:59", FMT) - datetime.strptime(currentTime, FMT)).replace("-1 day,","")
    return render_template('index.html', retailerCount=retailerCount,invalidApprovedCount=invalidApprovedCount, issExtCpCnt=issExtCpCnt,distRespCodes=distRespCodes, iseRetCnt=iseRetCnt, brandCnt=brandCnt, switchCnt=switchCnt, retailerLoadTime=retailerLoadTime,phaseOneTime=phaseOneTime, phaseTwoTime=phaseTwoTime)



@app.get('/upload_rrn')
@app.post('/upload_rrn')
@login_required
def upload_rrn():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    data = []
    searched_files = search_files(input_rrn_file_loc, input_rrn_file_name)

    if len(searched_files) != 0:
        for file in searched_files:
            rec = {}
            rec = {'link': file['absolute_file_name'], 'file': os.path.basename(
                file['absolute_file_name'])}
            data.append(rec)
    files_list_get = search_latest_files(output_rrn_file_loc, "", datetime.now().strftime(r'%Y-%m-%d'))

    if request.method == "POST":
        if 'upload_rrn_file' in request.form.keys():


            try:
                f = request.files['myfile']
                f.save(secure_filename(f.filename))
                try:
                    shutil.move(f.filename, input_rrn_file_loc)
                    flash("File Uploaded Is "+str(f.filename), 'success')
                except Exception as e:
                    os.remove(f.filename)
                    flash("File Already Exists", 'error')

            except Exception as e:
                flash("No File Selected To Upload", "error")

        elif 'make_extract_from_rrn' in request.form.keys():
            bol_value, error_or_path = make_extract()
            if bol_value:
                flash(f"Extract Created = {error_or_path}", 'success')
            else:
                flash(f"Extract Creation Failed ...!!", 'error')
                flash(f"Extract Creation Failed = {error_or_path}", 'error')
    
        else:
            pass
        
        data_new = []
        searched_files = search_files(input_rrn_file_loc, input_rrn_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(
                    file['absolute_file_name'])}
                data_new.append(rec)

        files_list_post = search_latest_files(
            output_rrn_file_loc, "", datetime.now().strftime(r'%Y-%m-%d'))
        return render_template('make_csv_from_rrn.html', result=data_new, result2=files_list_post)
       
    return render_template('make_csv_from_rrn.html', result=data, result2=files_list_get)
  
 

@app.get('/upload_file_screen')
@app.post('/upload_file_screen')
@login_required
def upload_file_screen():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])
    data = []
    searched_files = search_files(input_extract_file_loc, input_extract_file_name)

    if len(searched_files) != 0:
        for file in searched_files:
            rec = {}
            rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
            data.append(rec)
    
    if request.method == "POST":
        try:
            f  = request.files['myfile']
            f.save(secure_filename(f.filename))
            try:
                shutil.move(f.filename,input_extract_file_loc)
                flash("File Uploaded Is "+str(f.filename), 'success')
            except Exception as e:
                os.remove(f.filename)
                flash("File Already Exists", 'error')

        except Exception as e:
            flash("No File Selected To Upload","error")
            # flash("Error Encountered - {} ".format(e),"error")

        data_new = []
        searched_files = search_files(input_extract_file_loc, input_extract_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
                data_new.append(rec)

        return render_template('upload_file_screen.html',result=data_new)
    
    return render_template('upload_file_screen.html',result=data)


@app.get('/upload_fullday_htm_txt')
@app.post('/upload_fullday_htm_txt')
@login_required
def upload_fullday_htm_txt():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    data = []
    #function call to search latest files (abs_dir_path, file_name_to_search)
    searched_files = search_files(fullday_input_extract_file_loc, input_extract_file_name)

    if len(searched_files) != 0:
        for file in searched_files:
            rec = {}
            rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
            data.append(rec)
    
    if request.method == "POST":
        try:
            f  = request.files['myfile']
            f.save(secure_filename(f.filename))
            try:
                shutil.move(f.filename, fullday_input_extract_file_loc)
                flash("File Uploaded Is "+str(f.filename), 'success')
            except Exception as e:
                os.remove(f.filename)
                flash("File Already Exists", 'error')

        except Exception as e:
            flash("No File Selected To Upload","error")
            # flash("Error Encountered - {} ".format(e),"error")

        data_new = []
        searched_files = search_files(fullday_input_extract_file_loc, input_extract_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
                data_new.append(rec)

        return render_template('upload_fullday_htm_txt.html',result=data_new)
    return render_template('upload_fullday_htm_txt.html',result=data)


@app.get('/upload_gplink_htm_txt')
@app.post('/upload_gplink_htm_txt')
@login_required
def upload_gplink_htm_txt():
    # endpoint = request.endpoint
    # is_allowed_to_read(endpoint, session["permissions"])

    data = []
    gplinkLoc = "./GPLINK/AcquirerExtractFullDay/InputExtracts/"
    searched_files = search_files(gplinkLoc, input_extract_file_name)

    if len(searched_files) != 0:
        for file in searched_files:
            rec = {}
            rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
            data.append(rec)
    
    if request.method == "POST":
        try:
            f  = request.files['myfile']
            f.save(secure_filename(f.filename))
            try:
                shutil.move(f.filename, gplinkLoc)
                flash("File Uploaded Is "+str(f.filename), 'success')
            except Exception as e:
                os.remove(f.filename)
                flash("File Already Exists", 'error')

        except Exception as e:
            flash("No File Selected To Upload","error")
            # flash("Error Encountered - {} ".format(e),"error")

        data_new = []
        searched_files = search_files(gplinkLoc, input_extract_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
                data_new.append(rec)

        return render_template('upload_gplink_htm_txt.html',result=data_new)
    return render_template('upload_gplink_htm_txt.html',result=data)


@app.route('/upload_file_adjust', methods=['GET', 'POST'])
@login_required
def upload_file_adjust():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])
    data = []
    searched_files = search_files(file_adjust_loc, input_extract_file_name)

    if len(searched_files) != 0:
        for file in searched_files:
            rec = {}
            rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
            data.append(rec)

    if request.method == "POST":
        try:
            f  = request.files['myfile']
            f.save(secure_filename(f.filename))
            try:
                shutil.move(f.filename,file_adjust_loc)
                flash("File Uploaded Is "+str(f.filename), 'success')
            except Exception as e:
                os.remove(f.filename)
                flash("File Already Exists", 'error')

        except Exception as e:
            flash("No File Selected To Upload","error")
            # flash("Error Encountered - {} ".format(e),"error")

        data_new = []
        searched_files = search_files(file_adjust_loc, input_extract_file_name)
        if len(searched_files) != 0:
            for file in searched_files:
                rec = {}
                rec = {'link': file['absolute_file_name'], 'file': os.path.basename(file['absolute_file_name'])}
                data_new.append(rec)
        return render_template('upload_file_adjust_screen.html',result=data_new)
    return render_template('upload_file_adjust_screen.html',result=data)



# * Not Working [Ankita H.]
@app.get('/catalogs')
@app.post('/catalogs')
@login_required
def catalogs():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    catalogs = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == request.args.get('search')).dicts()
    InstitutionIdType = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "InstitutionIdType").dicts()
    CardBrandId = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CardBrandId").dicts()
    CardBrandType = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CardBrandType").dicts()
    FIID = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "FIID").dicts()

    if request.method == 'POST':
        catalogs= ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == request.args.get('search')).dicts()
        if "update" in request.form.keys():
            cat = ConfigurationCatalogs.get(ConfigurationCatalogs.code == request.form["code1"],ConfigurationCatalogs.catalog_name ==  request.form["catalog_name1"])

            cat.description = request.form["description1"]
            cat.catalog_name = request.form["catalog_name1"]
            cat.save()

            return redirect(url_for('catalogs') + "?search=" + request.args.get('search'))

        elif "delete" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            TypeCode = dict_you["code"]
            CataLog = dict_you["catalog_name"]

            ConfigurationCatalogs.get(ConfigurationCatalogs.code == TypeCode,
                                      ConfigurationCatalogs.catalog_name == CataLog).delete_instance()
            return redirect(url_for('catalogs') + "?search=" + CataLog)
            #return redirect(url_for('catalogs') + "?search=" + request.args.get('search'))
        else:
            form_data = request.form.to_dict()
            ConfigurationCatalogs.create(**form_data)

        return redirect(url_for('catalogs') + "?search=" + request.args.get('search'))

    return render_template('catalogs.html', catalogs=catalogs,InstitutionIdType=InstitutionIdType,CardBrandId=CardBrandId,CardBrandType=CardBrandType,FIID=FIID)


@app.get('/institution')
@app.post('/institution')
@login_required
def institution():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    ins_type = "Entidades Financieras"
    institution_id_type = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "InstitutionIdType").dicts()
    institution_id = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "InstitutionIdCode", ConfigurationCatalogs.related == ins_type).dicts()
    result = InstitutionId.select().dicts()
    fiid = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "FIID").dicts()

    if request.method == 'POST':
        if "delete" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            TypeCode = dict_you["TypeCode"]
            channel_name = dict_you["ChannelName"]
            TypeId = dict_you["TypeId"]
            InstitutionId.delete().where(InstitutionId.institution_id_type_code == TypeCode,
                                         InstitutionId.channel_name == channel_name,
                                         InstitutionId.institution_id_code == TypeId).execute()
            flash("Record Deleted", "success")
            
            return redirect(url_for('institution'))

        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys()}
            key = dict_you["key"]
            key1 = dict_you["key1"]

            print(key)
            print(key1)
            try:

                result = InstitutionId.select().where((InstitutionId.institution_id_type_code == key)
                                                     (InstitutionId.channel_name == key)
                                                      | (InstitutionId.institution_id_code == key1)).dicts()
                print(result)
                if len(result) == 0:
                    flash('The search item {} could not be found! :'.format(
                        key), 'error')

                return render_template('institution_search.html', ins_type=ins_type, institution_id_type=institution_id_type, institution_id=institution_id, result=result, fiid=fiid)

            except Exception as e:
                flash('Error in Search :{}'.format(e), 'error')
            return redirect(url_for('institution'))

        elif "update" in request.form.keys():
            # Made by dishant 7May2021
            a = request.form.to_dict()
            dict_you1 = {key: a[key] for key in a.keys()}
            
            try:
                InstitutionId.update(
                    fiid=str(dict_you1['fiid2']),
                    assigned_agreeement_code=str(dict_you1['aac2']),
                    name_officer=str(dict_you1['name_officer2']),
                    tax_id=str(dict_you1['tax_id2']),
                    bank_account_number=str(dict_you1['bank_account_number2']),
                    movment_type=str(dict_you1['movment_type2']),
                    bank_code=str(dict_you1['bank_code2']),
                    # channel_name=str(dict_you1['channel_name2']),
                    channel_type=int(dict_you1['channel_type2'])
                ).where(InstitutionId.institution_id_code == str(dict_you1['iic_OG']) and InstitutionId.channel_name ==str(dict_you1['channel_name2']) ).execute()
                flash("Record Updated", "success")

            except Exception as e:
                flash('Error in Update :{}'.format(dict_you1.keys()), 'error')
                flash('Error in Update :{}'.format(dict_you1), 'error')
                flash('Error in Update :{}'.format(e), 'error')

            return render_template('institution_search.html', ins_type=ins_type, institution_id_type=institution_id_type, institution_id=institution_id, result=result, fiid=fiid)

        else:
            if "create" in request.form.keys():
                a = request.form.to_dict()
                to_parse = {key: a[key] for key in a.keys() if a[key] != ""}
                print(to_parse)
                to_parse["institution_id_type_code"] = ConfigurationCatalogs.get(
                    ConfigurationCatalogs.description.contains(to_parse["institution_id_type_desc"])).code

                to_parse["institution_id_code"] = ConfigurationCatalogs.get(
                    ConfigurationCatalogs.description.contains(to_parse["institution_id_desc"])).code

                try:
                    #InstitutionId.create(**to_parse)
                    InstitutionId.create(institution_id_type_code=to_parse["institution_id_type_code"],
                                         institution_id_type_desc=request.form["institution_id_type_desc"],
                                         institution_id_code=to_parse["institution_id_code"],
                                         institution_id_desc=request.form["institution_id_desc"],
                                         fiid=request.form["fiid"],
                                         assigned_agreeement_code=request.form["aac"],
                                         name_officer=request.form["name_officer"],
                                         tax_id=request.form["tax_id"],
                                         bank_account_number=request.form["bank_account_number"],
                                         movment_type=request.form["movment_type"],
                                         bank_code=request.form["bank_code"],
                                         channel_name=request.form["channel_name"],
                                         channel_type=int(request.form["channel_type"]))
                    flash("Record created", "success")
                except Exception as e:
                    flash('Error in Create :{}'.format(e), 'error')
                    flash('Error in Create :{}'.format(e.args), 'error')
                    flash('Error in Create :{}'.format(to_parse), 'error')

        return redirect(url_for('institution'))
    return render_template('institution_search.html', ins_type=ins_type, institution_id_type=institution_id_type, institution_id=institution_id, result=result, fiid=fiid)


@app.get('/retailer_account')
@app.post('/retailer_account')
@login_required
def retailer_account():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    retailer_account = []
    retailer_account_cols = RetailerAccount._meta.sorted_field_names
    result = {}
    result = RetailerAccount.select().dicts()

    Terminal_Id,Terminal_Id = {},TerminalId.select(TerminalId.TerminalId).dicts()
    Retailer_Id = RetailerId.select(RetailerId.RetailerId).dicts()
    RetEntityId={}
    RetEntityId = InstitutionId.select().dicts()
    CardBrand,CardBrand ={},CardBrandId.select().dicts()

    # Generic Drop-Downs
    RetailerAccountsAccountTypeCode,RetailerAccountsAccountTypeCode ={},ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerAccountTypeCode').dicts()
    RetailerAccountsRetefuenteCode,RetailerAccountsRetefuenteCode ={},ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsRetefuenteCode").dicts()
    RetailerAccountsRetefuente,RetailerAccountsRetefuente ={},ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsRetefuente").dicts()
    RetailerAccountsReteicaCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsReteicaCode").dicts()
    RetailerAccountsReteica = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsReteica").dicts()
    RetailerAccountsCreeCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsCreeCode").dicts()
    RetailerAccountsCree = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsCree").dicts()
    RetailerAccountsReteivaCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsReteivaCode").dicts()
    RetailerAccountsReteiva = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "RetailerAccountsReteiva").dicts()

    # Data For Drop-Downs
    selects = [Retailer_Id, RetEntityId, CardBrand, Terminal_Id, RetailerAccountsAccountTypeCode, 0, RetailerAccountsRetefuenteCode, 0,
               RetailerAccountsReteicaCode, 0, RetailerAccountsCreeCode, 0, RetailerAccountsCree, 0,
               RetailerAccountsReteivaCode, 0,RetailerAccountsReteica,0,RetailerAccountsReteiva,0]

    if request.method == 'POST':

        if "update_s" in request.form.keys():
            a = request.form.to_dict()

            dict_you1 = {key: a[key] for key in a.keys() if a[key] != ""}

            try:

                RetailerAccount.update(
                    TerminalId=str(dict_you1['TerminalId']),
                    CardProductId=str(dict_you1['CardProductId']),
                    AccountTypeCode=int(dict_you1['AccountTypeCode']),
                    AccountNumber=int(dict_you1['AccountNumber']),
                    RetefuenteCode=int(dict_you1['RetefuenteCode']),
                    Retefuente=float(dict_you1['Retefuente']),
                    ReteicaCode=int(dict_you1['ReteicaCode']),
                    Reteica=float(dict_you1['Reteica']),
                    ImpoconsumoCode=int(dict_you1['ImpoconsumoCode']),
                    Impoconsumo=float(dict_you1['Impoconsumo']),
                    CreeCode=int(dict_you1['CreeCode']),
                    Cree=float(dict_you1['Cree']),
                    ReteivaCode=int(dict_you1['ReteivaCode']),
                    Reteiva=float(dict_you1['Reteiva'])
                ).where((RetailerAccount.RetailerId == str(dict_you1['RID_H'])) &
                        (RetailerAccount.EntityId == str(dict_you1['EID_H']))).execute()

                flash('Sucessfully Updated ', 'success')
                # flash(dict_you1, 'success')

            except Exception as e:
                flash('Error in Update :{}'.format(e), 'error')
                # flash('Error in UpdateS :{}'.format(e.args), 'error')
                # flash('Error in UpdateS :{}'.format(dict_you1), 'error')

            return redirect(url_for('retailer_account'))

        elif "delete" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            ret_id = dict_you["RetailerId"]
            termid = a["TerminalId"]
            CrdId = a["CardProductId"]
            EntId = a["EntityId"]

            try:
                RetailerAccount.delete().where(RetailerAccount.RetailerId == ret_id,
                                               RetailerAccount.TerminalId == termid, 
                                               RetailerAccount.CardProductId == CrdId,
                                               RetailerAccount.EntityId == EntId).execute()
                flash('Sucessfully deleted', 'success')

            except Exception as e:
                flash('Error in Delete :{}'.format(e), 'error')
            return redirect(url_for('retailer_account'))

        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys()}

            """
            key = dict_you["key1"]    # Retailer_ID
            key1 = dict_you["key2"]   # Terminal_ID
            key2 = dict_you["key3"]   # Card_Product_ID

            """
            key = dict_you["key1"]
            key1 = dict_you["key2"]
            key2 = dict_you["key3"]

            try:
                # All Spaces Set
                if key == " " or key1 == " " or key2 == " ":
                    raise ZeroDivisionError

                # All Empty Set
                elif key == "" and key1 == "" and key2 == "":
                    raise IndexError

                # All Filled Set
                elif key != "" and key1 != "" and key2 != "":
                    result = RetailerAccount.select().where((RetailerAccount.RetailerId == key) &
                                                            (RetailerAccount.TerminalId == key1) &
                                                            (RetailerAccount.CardProductId == key2)).dicts()

                # Key2 Absent
                elif key != "" and key1 != "" and key2 == "":
                    result = RetailerAccount.select().where((RetailerAccount.RetailerId == key) &
                                                            (RetailerAccount.TerminalId == key1)).dicts()

                # Key1 Absent
                elif key != "" and key1 == "" and key2 != "":
                    result = RetailerAccount.select().where((RetailerAccount.RetailerId == key) &
                                                            (RetailerAccount.CardProductId == key2)).dicts()

                # Key Absent
                elif key == "" and key1 != "" and key2 != "":
                    result = RetailerAccount.select().where((RetailerAccount.TerminalId == key1) &
                                                            (RetailerAccount.CardProductId == key2)).dicts()

                # Only Key [RID]
                elif (key != " " or key != "") and (key1 == " " or key1 == "") and (key2 == " " or key2 == ""):
                    result = RetailerAccount.select().where(
                        RetailerAccount.RetailerId == key).dicts()

                # Only Key1 [TID]
                elif (key1 != " " or key1 != "") and (key == " " or key == "") and (key2 == " " or key2 == ""):
                    result = RetailerAccount.select().where(
                        RetailerAccount.TerminalId == key1).dicts()

                # Only Key2 [CPID]
                elif (key2 != " " or key2 != "") and (key1 == " " or key1 == "") and (key == " " or key == ""):
                    result = RetailerAccount.select().where(
                        RetailerAccount.CardProductId == key2).dicts()

                print("Lenght Result = ", len(result))
                if len(result) == 0:
                    result = RetailerAccount.select().dicts()
                    raise ValueError
                else:
                    flash('The search item {} {} {} found...!'.format(
                        key, key1, key2), 'success')

                return render_template('retailer_account.html', selects=selects, result=result, retailer_account=retailer_account,RetailerAccountsAccountTypeCode=RetailerAccountsAccountTypeCode,RetailerAccountsRetefuenteCode=RetailerAccountsRetefuenteCode,RetailerAccountsRetefuente=RetailerAccountsRetefuente,RetailerAccountsReteicaCode=RetailerAccountsReteicaCode,RetailerAccountsReteica=RetailerAccountsReteica,RetailerAccountsCreeCode=RetailerAccountsCreeCode,RetailerAccountsCree=RetailerAccountsCree,RetailerAccountsReteivaCode=RetailerAccountsReteivaCode,RetailerAccountsReteiva=RetailerAccountsReteiva,retailer_account_cols=retailer_account_cols,RetEntityId=RetEntityId,Terminal_Id=Terminal_Id,CardBrand=CardBrand,)

            except ValueError:
                flash('Value Not Found...!!', 'error')

            except ZeroDivisionError:
                flash('Empty / Space value not allowed :', 'error')
                flash('The search item {},{},{} could not be found! :'.format(key, key1, key2), 'error')

            except IndexError:
                flash('Empty / Space value not allowed :', 'error')
                flash('The search item {},{},{} could not be found! :'.format(key, key1, key2), 'error')

            except Exception as e:
                print("Lenght Result = ", len(result))
                flash('Error in Search :{}'.format(e), 'error')

            return redirect(url_for('retailer_account'))

        else:
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            print(dict_you)
            try:
                RetailerAccount.create(**dict_you)
                flash('Sucessfully created', 'success')

            except Exception as e:
                flash('Error in Create :{}'.format(e), 'error')
            return redirect(url_for('retailer_account'))
            
    return render_template('retailer_account.html', selects=selects, result=result, retailer_account=retailer_account,RetailerAccountsAccountTypeCode=RetailerAccountsAccountTypeCode,RetailerAccountsRetefuenteCode=RetailerAccountsRetefuenteCode,RetailerAccountsRetefuente=RetailerAccountsRetefuente,RetailerAccountsReteicaCode=RetailerAccountsReteicaCode,RetailerAccountsReteica=RetailerAccountsReteica,RetailerAccountsCreeCode=RetailerAccountsCreeCode,RetailerAccountsCree=RetailerAccountsCree,RetailerAccountsReteivaCode=RetailerAccountsReteivaCode,RetailerAccountsReteiva=RetailerAccountsReteiva,retailer_account_cols=retailer_account_cols,RetEntityId=RetEntityId,Terminal_Id=Terminal_Id,CardBrand=CardBrand,)



@app.get('/retailers')
@app.post('/retailers')
@login_required
def retailers():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    retailer_cols = RetailerId._meta.sorted_field_names
    result = {}

    # * removing selects cols
    result = RetailerId.select().limit(20).dicts()
    RetailerEntityId = InstitutionId.select().dicts() # out catalogs
    RetailerGroupCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerGroupData').dicts() #catalog
    RetailerMallCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerMallData').dicts() #catalog
    RetailerAcquirerRegionCode = RetailerAcquirerRegion.select().dicts()
    RetailerIdentificationTypeCode = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'IdentificationTypeData').dicts()
    RetailerMCC= ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerMMCData').dicts()
    RetailerMCCForAmex= ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerMCCData').dicts()
    RetailerWorkingHoursCode =ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerWorkingHoursData').dicts()
    RetailerDepositOnLineCode=ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerDepositOnLineData').dicts()
    RetailerPaymentVendorsCode =ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerPaymentVendorsData').dicts()
    RetailerStatusCode=ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerStatusData').dicts()
    RetailerCountryCode = CountryCodes.select().dicts()
    RetailerCityCode = StateAndCity.select().dicts()
    RetailerStateCode = StateAndCity.select(StateAndCity.state_description,StateAndCity.state_code).distinct().dicts()
    RetailerNOMCC= ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerNOMMCData').dicts()
    RetailerNOMCCForAmex= ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == 'RetailerNOMCCData').dicts()

    if(len(RetailerEntityId) != 0 ): EntityId=RetailerEntityId.peek(RetailerEntityId.__len__())
    else: EntityId=0
    if(len(RetailerGroupCode) != 0 ): GroupCode=RetailerGroupCode.peek(RetailerGroupCode.__len__())
    else: GroupCode=0
    if(len(RetailerMallCode) != 0 ): MallCode=RetailerMallCode.peek(RetailerMallCode.__len__())
    else: MallCode=0
    if(len(RetailerAcquirerRegionCode) != 0 ): AcquirerRegionCode=RetailerAcquirerRegionCode.peek(RetailerAcquirerRegionCode.__len__())
    else: AcquirerRegionCode=0
    if(len(RetailerIdentificationTypeCode) != 0 ): IdentificationTypeCode=RetailerIdentificationTypeCode.peek(RetailerIdentificationTypeCode.__len__())
    else: IdentificationTypeCode=0
    if(len(RetailerMCC) != 0 ): MCC=RetailerMCC.peek(RetailerMCC.__len__())
    else: MCC=0
    if(len(RetailerMCCForAmex) != 0 ): MCCForAmex=RetailerMCCForAmex.peek(RetailerMCCForAmex.__len__())
    else: MCCForAmex=0
    if(len(RetailerWorkingHoursCode) != 0 ): WorkingHoursCode=RetailerWorkingHoursCode.peek(RetailerWorkingHoursCode.__len__())
    else: WorkingHoursCode=0
    if(len(RetailerDepositOnLineCode) != 0 ): DepositOnLineCode=RetailerDepositOnLineCode.peek(RetailerDepositOnLineCode.__len__())
    else: DepositOnLineCode=0
    if(len(RetailerPaymentVendorsCode) != 0 ): PaymentVendorsCode=RetailerPaymentVendorsCode.peek(RetailerPaymentVendorsCode.__len__())
    else: PaymentVendorsCode=0
    if(len(RetailerStatusCode) != 0 ): StatusCode=RetailerStatusCode.peek(RetailerStatusCode.__len__())
    else: StatusCode=0
    if(len(RetailerCountryCode) != 0 ): CountryCode=RetailerCountryCode.peek(RetailerCountryCode.__len__())
    else: CountryCode=0
    if(len(RetailerCityCode) != 0 ): CityCode=RetailerCityCode.peek(RetailerCityCode.__len__())
    else: CityCode=0
    if(len(RetailerStateCode) != 0 ): StateCode=RetailerStateCode.peek(RetailerStateCode.__len__())
    else: StateCode=0
    if(len(RetailerNOMCC) != 0 ): NOMCC=RetailerNOMCC.peek(RetailerNOMCC.__len__())
    else: NOMCC=0
    if(len(RetailerNOMCCForAmex) != 0 ): NOMCCAMEX=RetailerNOMCCForAmex.peek(RetailerNOMCCForAmex.__len__())
    else: NOMCCAMEX=0

    # Adding drop-down selects
    selects = [0,EntityId,GroupCode,MallCode,AcquirerRegionCode,0,0,CountryCode,StateCode,CityCode,CountryCode,0,0,0,0,0,0,0,0,0,0,0,IdentificationTypeCode,0,MCC,MCC,0,MCC,MCC,WorkingHoursCode,DepositOnLineCode,PaymentVendorsCode,0,0,0,StatusCode]
    if request.method == 'POST':
        if "update_s" in request.form.keys():
    	    # print("Inside Update_s")
            a = request.form.to_dict()
            retailer_id = a["RetailerId"]
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""  and key != "RetailerId" and key != "checkdigit"}

            try:
                ino = re.search("^\d{8}-[a-zA-Z0-9]$|^\d{8}$", str(dict_you["IdentificationNumber"]))
                if ino == None : ino = False
                else: ino = True

                if ino:
                    pass
                else:
                    raise TypeError

                RetailerId.update(**dict_you).where(RetailerId.RetailerId == retailer_id).execute()
                flash('Sucessfully updated','success')

            except TypeError:
                # print("ValueError")
                flash('Please give Tax_ID/ Identification number in correct format eg :- 12345678-K or 12345678-0 or 12345678','error')

            except Exception as e:
                flash('Error in Update :{}'.format(e),'error')

            return redirect(url_for('retailers'))


        elif "delete" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            retailer_id = dict_you["RetailerId"]

            try:
                RetailerId.delete().where(RetailerId.RetailerId == retailer_id).execute()
                flash('Sucessfully deleted','success')

            except Exception as e:
                flash('Error in Delete :{}'.format(e),'error')

            return redirect(url_for('retailers'))

        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}

            try:
                key = dict_you["key1"]
                result = RetailerId.select().where(RetailerId.RetailerId == key ).dicts()
                if len(result) == 0:
                    flash('The search item {} could not be found! :'.format(key),'error')

                return render_template('retailers.html', catalogs=catalogs,result=result, retailer_cols = retailer_cols,selects = selects)

            except Exception as e:
                flash('Error in Search, please put some value','error')

            return redirect(url_for('retailers'))

        else:
            a = request.form.to_dict()
            try:
                dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
                # All Possible Validations For RetailerID
                data = str(dict_you["RetailerId"])
                print("RID = ",data)
                special_characters1 = "'!@#$%^&*()-+?._=,;\`[]<>/'"
                special_characters2 = '"!@#$%^&*()-+?_.=,;\`[]<>/"'
                
                ino = re.search("^\d{8}-[a-zA-Z0-9]$|^\d{8}$", str(dict_you["IdentificationNumber"]))
                if ino == None : ino = False
                else: ino = True

                if ino:
                    pass
                else:
                    raise TypeError

                if "RetailerId" not in dict_you:
                    raise IndexError
                elif any(c in special_characters2 for c in data):
                    raise ValueError
                elif any(c in special_characters1 for c in data):
                    raise ValueError
                elif data == " " or data == "": 
                    raise ZeroDivisionError 
                elif " " in data: 
                    raise ZeroDivisionError
                else:
                    print("Inside Else")
                    RetailerId.create(**dict_you)
                    flash('Sucessfully created','success')
                    # flash(dict_you, 'success')
                    # flash(data, 'success')

            # except ValueError:
            #     # print("ValueError")
            #     flash('Retailer ID cannot have special characters ...!!','error')

            except TypeError:
                # print("ValueError")
                flash('Please give Tax_ID/ Identification number in correct format eg :- 12345678-K or 12345678-0 or 12345678','error')

            except ZeroDivisionError:
                # print("ZeroDivisionError")
                flash('Retailer ID cannot have Empty/Space value ...!!','error')
            
            except Exception as e:
                # print("E = ",e)
                flash('Error in Create :{}'.format(e.args),'error')
                # flash(dict_you, 'error')
                # flash(data, 'error')
            
            return redirect(url_for('retailers'))
    
    return render_template('retailers.html',catalogs=catalogs,result=result, retailer_cols = retailer_cols,selects = selects)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Logs the User In """
    print('session', session, flush=True)
    if "user_id" in session:
        return redirect(url_for('home'))
    user_error = None
    pwd_error = None
    if request.method == 'POST':
        print('check username from ui',request.form['username'],flush=True)
        try:
            user = Users.get(Users.username == request.form['username'])
            print(user)
        except Exception as e:
            user = None
        print('user object', user, flush=True)
        if user is None:
            user_error = 'Invalid username'
        elif not check_password_hash(user.pw_hash, request.form['password']):
            pwd_error = 'Invalid password'
        elif not user.status:
            error = 'User freezed'
        else:
            flash('You were logged in', 'success')
            session['user_id'] = user.username
            session['email'] = user.email
            session['institution'] = list(InstitutionId.select().dicts())
            session['role'] = user.role
            session['permissions'] = str(user.permissions)
            session['cur_institution'] = user.institution
            return redirect(url_for('home'))
    return render_template('login.html', user_error=user_error, pwd_error=pwd_error)


@app.get('/register')
@app.post('/register')
def register():
    """ Registers the user """

    # print("Get Method Register URL")
    users = []
    for user in Users.select():
        try:
            permissions = ast.literal_eval(user.permissions)
        except:
            permissions = {}
        users.append((user.created_date, user.username, user.role,
                      user.email, permissions, user.status))
    enterprise_cols = EnterpriseInfo._meta.sorted_field_names
    result = {}
    # dropdown selects from catalogs
    RetailerEntityId = InstitutionId.select().dicts() # out catalogs
    EntityId = RetailerEntityId.peek(RetailerEntityId.__len__())

    selects = [EntityId, 0, 0, 0, 0, 0]

    error = None

    if request.method == 'POST':
        # Create
        if "create" in request.form.keys():
            a = request.form.to_dict()

            dict_you = {key: a[key] for key in a.keys() if a[key] != "" and a[key] != "myFile"}
            try:
                EnterpriseInfo.create(**dict_you)
                flash('Sucessfully created', 'success')
            except Exception as e:
                flash('Error in Create :{}'.format(e), 'error')
        #elif "upload" in request.form.keys():
            f = request.files['myFile']
            if allowed_file(f.filename):
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename("enterprise.png")))
            else:
                flash('Please input appropriate image', 'error')
            return render_template('profile.html', users=users, error=error, result=result, enterprise_cols=enterprise_cols, selects=selects)


        # Search
        elif "search" in request.form.keys():
            rfk = request.form.to_dict()
            print("Inside Search")
            print("RFK = ", rfk)
            update_users = []
            for searched_user in Users.select().where(Users.username == rfk['table_search']):
                try:
                    permissions = ast.literal_eval(searched_user.permissions)
                except:
                    permissions = {}
                update_users.append((searched_user.created_date, searched_user.username,
                                     searched_user.role, searched_user.email, permissions, searched_user.status))

            # del users[:]
            # users = update_users
            print("Updated_User = ", update_users)
            print("error, result, enterprise_cols,selects = ", error, result, enterprise_cols, selects)
            return render_template('profile.html', users=update_users, error=error, result=result, enterprise_cols=enterprise_cols, selects=selects)

        
        else:
            if "drop" in request.form.keys():
            
                if get_user_id(request.form['username']) is None:
                   error = 'You have to enter a valid username'
            
                else:
                    user = Users.get(username=request.form['username'])
                    user.delete_instance()
                    flash('You were successfully deleted the user', 'success')
                    return redirect(url_for('login'))
            
                flash('User could not be deleted: {}'.format(error), 'error')

            
            if "update" in request.form.keys():
                
                if get_user_id(request.form['username']) is None:
                   error = 'You have to enter a valid username'
                
                elif not request.form['password']:
                    error = 'You have to enter a password'
                
                elif check_password_strong(request.form['password']) != 0:
                    error = 'Password should be : {}'.format(check_password_strong(request.form['password']))
                
                elif request.form['password'] != request.form['password2']:
                    error = 'The two passwords do not match'
                
                else:
                    user = Users.get(username=request.form['username'])
                    user.pw_hash = generate_password_hash(
                        request.form['password'])
                    user.save()
                    flash('You were successfully changed the password', 'success')
                    return redirect(url_for('login'))

                flash('User password could not be changed: {}'.format(error), 'error')

            
            else:
                
                if not request.form['username']:
                    error = 'You have to enter a username'
                
                elif not request.form['email'] or \
                        '@' not in request.form['email']:
                    error = 'You have to enter a valid email address'
                
                elif not request.form['password']:
                    error = 'You have to enter a password'
                
                elif check_password_strong(request.form['password']) != 0:
                    error = 'Password should be : {}'.format(check_password_strong(request.form['password']))
                
                elif request.form['password'] != request.form['password2']:
                    error = 'The two passwords do not match'
                
                elif get_user_id(request.form['username']) is not None:
                    error = 'The username is already taken'
                
                else:
                    user = Users(username=request.form['username'], role=request.form['role'], institution=request.form['institution'], permissions=request.form['permissions'], email=request.form['email'],pw_hash=generate_password_hash(request.form['password']))
                    user.save()
                    flash('You were successfully registered and can login now', 'success')
                    
                    return redirect(url_for('login'))
                
                flash('User could not be created: {}'.format(error), 'error')
    
    return render_template('profile.html', users=users, error=error, result=result, enterprise_cols=enterprise_cols, selects=selects)


@app.get('/reports_download')
@app.post('/reports_download')
@login_required
def reports_download():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    retailer_reports = "./CompensationReports/ZipRetailerReports/"
    adjustment_reports = "./CompensationReports/AdjustmentReports/"
    conciliation_reports = "./CompensationReports/ConciliationReports/"

    searched_files = search_latest_files(retailer_reports, "", datetime.today().date())

    if request.method == 'POST':
        
        if "download" in request.form.keys():
            # print("\n\nPOST METHOD")
            # print("\nForm Keys = ",request.form.keys())
            # print(request.form.to_dict())

            selected_date = request.form['select_date']
            if selected_date == "" or selected_date == " ":
                flash('Please Select A Date..!!!', 'error')
            else:
                # Selected Date Split
                sdy, sdm, sdd = "", "", ""
                sd = str(selected_date)

                data1 = sd.split("-")
                sdy = str(data1[0])

                if "0" in str(data1[1])[0]:
                    sdm = str(data1[1]).replace("0", "")
                else:
                    sdm = str(data1[1])

                if "0" in str(data1[2])[0]:
                    sdd = str(data1[2]).replace("0", "")
                else:
                    sdd = str(data1[2])

                # Today Date Split
                tdy, tdm, tdd = "", "", ""
                data = str(datetime.today().date()).split("-")
                tdy = str(data[0])

                if "0" in str(data[1])[0]:
                    tdm = str(data[1]).replace("0", "")
                else:
                    tdm = str(data[1])

                if "0" in str(data[2])[0]:
                    tdd = str(data[2]).replace("0", "")
                else:
                    tdd = str(data[2])

                # Compare Dates
                TD = datetime(int(tdy), int(tdm), int(tdd))
                SD = datetime(int(sdy), int(sdm), int(sdd))

                if SD > TD:
                    flash('Future Date Not Allowed..!!!', 'error')

                else:

                    if(request.form['result_type'] == "01"):
                        result_type = retailer_reports
                    elif(request.form['result_type'] == "02"):
                        result_type = adjustment_reports
                    elif(request.form['result_type'] == "03"):
                        result_type = conciliation_reports

                    sd_ = str(sdy)+"-"+str(sdm)+"-"+str(sdd)
                    searched_files = search_latest_files(result_type, "", sd_)
                    flash(f'All Files For Date = {sd}', 'success')
                    return render_template('reports_download.html', result=searched_files)

        else:

            data = str(datetime.today().date()).split("-")
            return render_template('reports_download.html', result=data)

    return render_template('reports_download.html', result=searched_files)


@app.get('/commission_slab_range')
@app.post('/commission_slab_range')
@login_required
def commission_slab_range():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    result = CommissionSlabRange.select().dicts()
    CST = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")
    i_id = InstitutionId.select()
    iid_rid = RetailerId.select()

    if request.method == 'POST':

        # DELETE BLOCK
        if "delete" in request.form.keys():
            a = request.form.to_dict()
            # print(a)
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            # print("Dict You = ", dict_you)
            RID = dict_you["retailer_id"]
            IID = dict_you["institution_id"]
            LR = dict_you["lr"]
            HR = dict_you["hr"]
            CST = dict_you["cst"]
            VAL = dict_you["val"]
            try:
                CommissionSlabRange.delete().where((CommissionSlabRange.retailer_id == str(RID)) &
                                                   (CommissionSlabRange.institution_id == str(IID)) &
                                                   (CommissionSlabRange.low_range == int(LR)) &
                                                   (CommissionSlabRange.high_range == int(HR)) &
                                                   (CommissionSlabRange.commision_subtype == str(CST)) &
                                                   (CommissionSlabRange.value == float(VAL))).execute()
                flash('Sucessfully deleted', 'success')

            except Exception as e:
                flash('Error in Delete :{}'.format(e), 'error')
            return render_template('comm_slab_range.html', data=result, IID=i_id, C_S_T=CST, IR=iid_rid)

        # SEARCH BLOCK
        elif "search" in request.form.keys():
            s = request.form.to_dict()
            dict_you3 = {key: s[key] for key in s.keys() if s[key] != ""}

            try:
                if not dict_you3:
                    raise ValueError

                key = dict_you3["key1"]

                search_data = CommissionSlabRange.select().where(
                    CommissionSlabRange.retailer_id == str(key))

                if len(search_data) == 0:
                    flash('The search item {} could not be found! :'.format(
                        key), 'error')

                return render_template('comm_slab_range.html', data=search_data, IID=i_id, C_S_T=CST, IR=iid_rid)

            except ValueError:
                flash('Error in Search, empty value not allowed', 'error')
                return render_template('comm_slab_range.html', data=result, IID=i_id, C_S_T=CST, IR=iid_rid)

            except Exception as e:
                flash('Error in Search, please put correct value', 'error')
            return render_template('comm_slab_range.html', data=search_data, IID=i_id, C_S_T=CST, IR=iid_rid)

        # UPDATE BLOCK
        elif "update" in request.form.keys():

            up1 = request.form.to_dict()
            dict_you1 = {key: up1[key] for key in up1.keys() if up1[key] != ""}

            try:

                CommissionSlabRange.update(
                    commision_subtype=str(dict_you1['com_sub_type']),
                    low_range=int(dict_you1['lr']),
                    high_range=int(dict_you1['hr']),
                    value=float(dict_you1['val'])
                ).where((CommissionSlabRange.retailer_id == str(dict_you1["retailer_id"])) &
                        (CommissionSlabRange.institution_id == str(dict_you1["inst_id"])) &
                        (CommissionSlabRange.commision_subtype == str(dict_you1["cst"])) &
                        (CommissionSlabRange.high_range == int(dict_you1["hr_h"])) &
                        (CommissionSlabRange.low_range == int(dict_you1["lr_h"])) &
                        (CommissionSlabRange.value == float(dict_you1["val_h"]))).execute()

                flash('Sucessfully update', 'success')

            except Exception as e:
                flash('Error in Delete :{}'.format(e), 'error')

            return render_template('comm_slab_range.html', data=result, IID=i_id, C_S_T=CST, IR=iid_rid)

        else:
            # CREATE
            try:

                CommissionSlabRange.create(
                    institution_id=str(request.form['inst_id']),
                    retailer_id=str(request.form['retailer_id']),
                    commision_subtype=str(request.form['com_sub_type']),
                    low_range=int(request.form['lr']),
                    high_range=int(request.form['hr']),
                    value=float(request.form['val'])
                )
                flash('Sucessfully Added', 'success')

            except Exception as e:
                flash('Empty values are not allowed..!!', 'error')

            return render_template('comm_slab_range.html', data=result, IID=i_id, C_S_T=CST, IR=iid_rid)

    return render_template('comm_slab_range.html', data=result, IID=i_id, C_S_T=CST, IR=iid_rid)


@app.get('/commission_type')
@app.post('/commission_type')
@login_required
def commission_type():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    RCOF = RetailerCommissionRules.select()
    CT = ConfigurationCatalogs.select().where(
        ConfigurationCatalogs.catalog_name == "CommisionType")
    CST = ConfigurationCatalogs.select().where(
        ConfigurationCatalogs.catalog_name == "CommisionSubType")
    i_id = InstitutionId.select()
    iid_rid = RetailerId.select()

    if request.method == 'POST':

        # DELETE BLOCK
        if "delete" in request.form.keys():
            a = request.form.to_dict()

            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            st   = True if str(dict_you["status"]) == "True" else False
            
            try:

                RetailerCommissionRules.delete().where(
                    (RetailerCommissionRules.retailer_id == str(dict_you["retailer_id"])) &
                    (RetailerCommissionRules.institution_id == str(dict_you["institution_id"])) &
                    (RetailerCommissionRules.channel == str(dict_you["channel"])) &
                    (RetailerCommissionRules.commision_sub_type == str(dict_you["commision_sub_type"])) &
                    (RetailerCommissionRules.commision_type == str(dict_you["commision_type"])) &
                    (RetailerCommissionRules.card_type == str(dict_you["card_type"])) &
                    (RetailerCommissionRules.mcc == str(dict_you["mcc"])) &
                    (RetailerCommissionRules.bin == str(dict_you["bin"])) &
                    (RetailerCommissionRules.transaction_identifier == str(dict_you["transaction_identifier"])) &
                    (RetailerCommissionRules.status == st) &
                    (RetailerCommissionRules.rubro == str(dict_you["rubro"]))&
                    (RetailerCommissionRules.priority == str(dict_you["priority"]))
                ).execute()

                flash('Sucessfully Deleted', 'success')

            except Exception as e:

                flash('Error in Delete :{}'.format(e), 'error')
            
            RCOF_d = RetailerCommissionRules.select()
            CT_d = ConfigurationCatalogs.select().where(
                ConfigurationCatalogs.catalog_name == "CommisionType")
            CST_d = ConfigurationCatalogs.select().where(
                ConfigurationCatalogs.catalog_name == "CommisionSubType")
            i_id_d = InstitutionId.select()
            iid_rid_d = RetailerId.select()

            # * Commented By Dishant [24_Aug_2021] :- redirect was not working hence updated values were not seen
            # return redirect(url_for('commission_type'))
            return render_template('commission_type.html', IID=i_id_d, rcof=RCOF_d, C_T=CT_d, C_S_T=CST_d, IR=iid_rid_d)

        # SEARCH BLOCK
        elif "search" in request.form.keys():
            s = request.form.to_dict()

            dict_you3 = {key: s[key] for key in s.keys() if s[key] != ""}

            try:
                key = dict_you3["key1"]

                search_data = RetailerCommissionRules.select().where(
                    RetailerCommissionRules.retailer_id == str(key))

                if len(search_data) == 0:
                    flash('The search item {} could not be found! :'.format(
                        key), 'error')
                return render_template('commission_type.html', IID=i_id, rcof=search_data, C_T=CT, C_S_T=CST, IR=iid_rid)

            except Exception as e:
                flash('Error in Search, please put correct value', 'error')
            return redirect(url_for('commission_type'))

        # UPDATE BLOCK
        if "update" in request.form.keys():
            up1 = request.form.to_dict()

            dict_you1 = {key: up1[key] for key in up1.keys() if up1[key] != ""}
            

            try:
                st    = True if str(dict_you1["upm2_st"]) == "True" else False
                if str(dict_you1["ret_id"]) != 'DEFAULT':
                    check_retailer_id = RetailerId.select().where((RetailerId.RetailerId == str(dict_you1["ret_id"]))).execute()
                    if len(check_retailer_id) < 1: raise Exception
       
                RetailerCommissionRules.update(institution_id=str(dict_you1["institution_id"]),
                                                retailer_id=str(dict_you1["ret_id"]),
                                                channel=str(dict_you1["channel_upm2"]),
                                                commision_type=str(dict_you1['upm2_com_t']),
                                                commision_sub_type=str(dict_you1['upm2_com_st']),
                                                card_type=str(dict_you1["upm2_ct"]),
                                                mcc=str(dict_you1["upm2_mct"]),
                                                bin=str(dict_you1["upm2_bin"]),
                                                transaction_identifier=str(dict_you1["upm2_tid"]),
                                                status  = st,
                                                priority=str(dict_you1["ump2_priority"]),
                                                region=str(dict_you1["region"]),
                                                rubro = str(dict_you1["upm2_rb"])
                                                ).where(
                                                    (RetailerCommissionRules.retailer_id == str(dict_you1["ret_id"])) & 
                                                    (RetailerCommissionRules.institution_id == str(dict_you1["institution_id"])) &
                                                    (RetailerCommissionRules.channel == str(dict_you1["channel_upm2"]))
                                                    ).execute()

                flash('Sucessfully update', 'success')

            except Exception as e:
                flash('Error in Update :{}'.format(e), 'error')
                flash('Retailer ID not present in database', 'error')


            RCOF_U = RetailerCommissionRules.select()
            CT_U = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionType")
            CST_U = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")

            # * Commented By Dishant [24_Aug_2021] :- redirect was not working hence updated values were not seen
            # return redirect(url_for('commission_type'))
            return render_template('commission_type.html', IID=i_id, rcof=RCOF_U, C_T=CT_U, C_S_T=CST_U, IR=iid_rid)
            

        # CREATE BLOCK
        else:
            try:
                a1 = request.form.to_dict()
                dict_you2 = {key: a1[key] for key in a1.keys() if a1[key] != ""}

                st   = True if str(dict_you2["status"]) == "1" else False
                if str(dict_you2["retailer_id"]) != 'DEFAULT':
                    check_retailer_id = RetailerId.select().where((RetailerId.RetailerId == str(dict_you2["retailer_id"]))).execute()
                    if len(check_retailer_id) < 1: raise Exception
                
                RetailerCommissionRules.create(institution_id=str(dict_you2['inst_id']),
                                                retailer_id=str(dict_you2['retailer_id']),
                                                channel=str(dict_you2['channel_name']),
                                                commision_type=str(dict_you2['com_type']),
                                                commision_sub_type=str(dict_you2['com_sub_type']),
                                                card_type=str(dict_you2["card_type"]),
                                                mcc=str(dict_you2["mcc_ct"]),
                                                bin=str(dict_you2["bin"]),
                                                transaction_identifier=str(dict_you2["tran_id"]),
                                                status = st,
                                                priority=str(dict_you2['priority']),
                                                region=str(dict_you2["region"]),
                                                rubro = str(dict_you2["rubro"]))

                flash('Commission Profile Created Sucessfully', 'sucess')

            except Exception as e:
                flash('Error in Create Commission Profile:{}'.format(e), 'error')
                flash('Retailer ID not present in database', 'error')

            RCOF = RetailerCommissionRules.select()
            CT = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionType")
            CST = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")
            i_id = InstitutionId.select()
            iid_rid = RetailerId.select()

        # * Commented By Dishant [27Aug2021] :- Flash msg was not seen on UI
        # return redirect(url_for('commission_type'))
        return render_template('commission_type.html', IID=i_id, rcof=RCOF, C_T=CT, C_S_T=CST, IR=iid_rid)

    return render_template('commission_type.html', IID=i_id, rcof=RCOF, C_T=CT, C_S_T=CST, IR=iid_rid)


@app.get('/retailer_commission')
@app.post('/retailer_commission')
@login_required
def retailer_commission():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    # Fetch Values From DataBase
    ret_comm = RetailerCommissionValues.select().dicts()
    iid_rid = RetailerId.select()
    pro_code = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsTransactionType")
    msg_type = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsMessageType")
    res_code = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsResponseCode")
    i_id = InstitutionId.select()
    iid_rid = RetailerId.select()

    if request.method == 'POST':
        ip = request.form.to_dict()

        # DELETE BLOCK
        if "delete" in request.form.keys():
            a = request.form.to_dict()

            dict_you3 = {key: a[key] for key in a.keys() if a[key] != ""}
            try:

                RetailerCommissionValues.delete().where((RetailerCommissionValues.retailer_id == str(dict_you3["retailer_id"])) &
                (RetailerCommissionValues.institution_id == str(dict_you3["institution_id"])) & 
                (RetailerCommissionValues.channel == str(dict_you3["channel"])) &
                (RetailerCommissionValues.message_type == str(dict_you3["message_type"])) &
                (RetailerCommissionValues.processing_code == str(dict_you3["processing_code"])) &
                (RetailerCommissionValues.response_code == str(dict_you3["response_code"])) &
                (RetailerCommissionValues.debit_value == str(dict_you3["debit_value"])) &
                (RetailerCommissionValues.credit_value == str(dict_you3["credit_value"])) &
                (RetailerCommissionValues.prepaid_value == str(dict_you3["prepaid_value"])) &
                (RetailerCommissionValues.mcc == str(dict_you3["mcc"])) &
                (RetailerCommissionValues.mcc_debit_value == str(dict_you3["mcc_debit_value"])) &
                (RetailerCommissionValues.mcc_credit_value == str(dict_you3["mcc_credit_value"])) &
                (RetailerCommissionValues.mcc_prepaid_value == str(dict_you3["mcc_prepaid_value"])) &
                (RetailerCommissionValues.bin == str(dict_you3["bin"])) &
                (RetailerCommissionValues.bin_value == str(dict_you3["bin_value"])) &
                (RetailerCommissionValues.domestic_value == str(dict_you3["dom_val"])) &
                (RetailerCommissionValues.international_value == str(dict_you3["i_val"])) &
                (RetailerCommissionValues.rubro == str(dict_you3["rubro"])) &
                (RetailerCommissionValues.rubro_debit_value == str(dict_you3["rubro_debit_value"])) &
                (RetailerCommissionValues.rubro_credit_value == str(dict_you3["rubro_credit_value"])) &
                (RetailerCommissionValues.rubro_prepaid_value == str(dict_you3["rubro_prepaid_value"])) 
                ).execute()

                flash('Sucessfully deleted', 'success')

            except Exception as e:
                flash('Error in delete', 'error')
            
            # * Commented By Dishant [24_Aug_2021] :- the redirect was givng old values and not the updated once on screen
            return redirect(url_for('retailer_commission'))
            # return render_template('ret_commission.html', IID=i_id, Pro_Code=pro_code, Ret_Com1=iid_rid, Ret_Com=ret_comm, Msg_Type=msg_type, Res_Code=res_code, IR = iid_rid)


        # SEARCH BLOCK
        elif "search" in request.form.keys():
            a = request.form.to_dict()

            dict_you2 = {key: a[key] for key in a.keys() if a[key] != ""}

            try:
                key = dict_you2["key1"]

                search_data = RetailerCommissionValues.select().where(RetailerCommissionValues.retailer_id == str(key) )

                if len(search_data) == 0:
                    flash('The search item {} could not be found! :'.format(key),'error')
                return render_template('ret_commission.html', IID=i_id, IR = iid_rid, Pro_Code=pro_code, Ret_Com1=iid_rid, Ret_Com=search_data, Msg_Type=msg_type, Res_Code=res_code)
                
            except Exception as e:
                flash('Error in Search, please put correct value','error')

            return redirect(url_for('retailer_commission'))

        # UPDATE BLOCK
        elif "update" in request.form.keys():
            try:

                a = request.form.to_dict()
                dict_you1 = {key: a[key] for key in a.keys() if a[key] != ""}
                check_retailer_id = (RetailerCommissionRules.select().where((RetailerCommissionRules.institution_id == str(dict_you1["upm2_institution_id"])) & (RetailerCommissionRules.retailer_id == str(dict_you1["upm2_retailer_id"])) & (RetailerCommissionRules.channel == str(dict_you1["upm2_channel_H"]))).dicts().iterator())                                              
                data=[k for k in check_retailer_id]
                card_type_data=[ct['commision_type'] for ct in data]
                if((('1' in card_type_data) and ('3' in card_type_data)) or (('2' in card_type_data) and ('3' in card_type_data))):pass
                else:
                    for k in data:
                        if k['commision_type'] == '1' or k['commision_type'] == '2':
                            if ':' not in str(dict_you1["upm2_debit_value"]) and ':' not in str(dict_you1["upm2_credit_value"]) and ':' not in str(dict_you1["upm2_prepaid_value"]) and ':' not in str(dict_you1["upm2_mcc_debit_value"]) and ':'  not in str(dict_you1["upm2_mcc_credit_value"]) and ':' not in str(dict_you1["upm2_mcc_prepaid_value"]) and ':' not in str(dict_you1["upm2_bin_value"]) and ':' not in str(dict_you1["upm2_rubro_debit_value"]) and ':' not in str(dict_you1["upm2_rubro_credit_value"]) and ':' not in str(dict_you1["upm2_rubro_prepaid_value"]) and ':' not in str(dict_you1["upm2_region_debit_value"]) and ':' not in str(dict_you1["upm2_region_credit_value"]) and ':' not in str(dict_you1["upm2_region_prepaid_value"]):result=True
                            else:raise ValueError
                        elif k['commision_type'] == '3' and k['card_type']== '1':
                            if ':'  in str(dict_you1["upm2_debit_value"]) and ':'  in str(dict_you1["upm2_credit_value"]) and ':' in str(dict_you1["upm2_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['mcc'] == '1' :
                            if ':'  in str(dict_you1["upm2_mcc_debit_value"]) and ':'  in str(dict_you1["upm2_mcc_credit_value"]) and ':' in str(dict_you1["upm2_mcc_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['bin'] == '1' :
                            if ':'  in str(dict_you1["upm2_bin_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['rubro'] == '1' :
                            if ':'  in str(dict_you1["upm2_rubro_debit_value"]) and ':'  in str(dict_you1["upm2_rubro_credit_value"]) and ':' in str(dict_you1["upm2_rubro_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['region'] == '1' :
                            if ':'  in str(dict_you1["upm2_region_debit_value"]) and ':'  in str(dict_you1["upm2_region_credit_value"]) and ':' in str(dict_you1["upm2_region_prepaid_value"]):result=True
                            else: raise AttributeError
                try:
                    RetailerCommissionValues.update(
                                                    channel=str(dict_you1["upm2_channel"]),
                                                    message_type=str(dict_you1["upm2_message_type"]),
                                                    processing_code=str(dict_you1["upm2_processing_code"]),
                                                    response_code=str(dict_you1["upm2_response_code"]),
                                                    debit_value=str(dict_you1["upm2_debit_value"]),
                                                    credit_value=str(dict_you1["upm2_credit_value"]),
                                                    prepaid_value=str(dict_you1["upm2_prepaid_value"]),
                                                    mcc=str(dict_you1["upm2_mcc"]),
                                                    mcc_debit_value=str(dict_you1["upm2_mcc_debit_value"]),
                                                    mcc_credit_value=str(dict_you1["upm2_mcc_credit_value"]),
                                                    mcc_prepaid_value=str(dict_you1["upm2_mcc_prepaid_value"]),
                                                    bin=str(dict_you1["upm2_bin"]),
                                                    bin_value=str(dict_you1["upm2_bin_value"]),
                                                    domestic_value=str(dict_you1["upm2_d_value"]),
                                                    international_value=str(dict_you1["upm2_i_value"]),
                                                    rubro=str(dict_you1["upm2_rubro"]),
                                                    rubro_debit_value=str(dict_you1["upm2_rubro_debit_value"]),
                                                    rubro_credit_value=str(dict_you1["upm2_rubro_credit_value"]),
                                                    rubro_prepaid_value=str(dict_you1["upm2_rubro_prepaid_value"]),
                                                    region=str(request.form.get("upm2_region",'')),
                                                    region_debit_value=str(dict_you1["upm2_region_debit_value"]),
                                                    region_credit_value=str(dict_you1["upm2_region_credit_value"]),
                                                    region_prepaid_value=str(dict_you1["upm2_region_prepaid_value"]),
                                                    ).where(
                                                        (RetailerCommissionValues.institution_id == str(dict_you1["upm2_institution_id"])) &
                                                        (RetailerCommissionValues.retailer_id == str(dict_you1["upm2_retailer_id"])) &
                                                        (RetailerCommissionValues.channel == str(dict_you1["upm2_channel_H"])) &
                                                        (RetailerCommissionValues.message_type == str(dict_you1["upm2_message_type_H"])) &
                                                        (RetailerCommissionValues.processing_code == str(dict_you1["upm2_processing_code_H"])) &
                                                        (RetailerCommissionValues.response_code == str(dict_you1["upm2_response_code_H"])) &
                                                        (RetailerCommissionValues.debit_value == str(dict_you1["upm2_debit_value_H"])) &
                                                        (RetailerCommissionValues.credit_value == str(dict_you1["upm2_credit_value_H"])) &
                                                        (RetailerCommissionValues.prepaid_value == str(dict_you1["upm2_prepaid_value_H"])) &
                                                        (RetailerCommissionValues.mcc == str(dict_you1["upm2_mcc_H"])) & 
                                                        (RetailerCommissionValues.mcc_debit_value == str(dict_you1["upm2_mcc_debit_value_H"])) &
                                                        (RetailerCommissionValues.mcc_credit_value == str(dict_you1["upm2_mcc_credit_value_H"])) &
                                                        (RetailerCommissionValues.mcc_prepaid_value == str(dict_you1["upm2_mcc_prepaid_value_H"])) &
                                                        (RetailerCommissionValues.bin == str(dict_you1["upm2_bin_H"])) &
                                                        (RetailerCommissionValues.bin_value == str(dict_you1["upm2_bin_value_H"])) &
                                                        (RetailerCommissionValues.domestic_value == str(dict_you1["upm2_d_value_H"])) &
                                                        (RetailerCommissionValues.international_value == str(dict_you1["upm2_i_value_H"])) &
                                                        (RetailerCommissionValues.rubro == str(dict_you1["upm2_rubro_H"])) & 
                                                        (RetailerCommissionValues.rubro_debit_value == str(dict_you1["upm2_rubro_debit_value_H"])) &
                                                        (RetailerCommissionValues.rubro_credit_value == str(dict_you1["upm2_rubro_credit_value_H"])) &
                                                        (RetailerCommissionValues.rubro_prepaid_value == str(dict_you1["upm2_rubro_prepaid_value_H"])) &
                                                        (RetailerCommissionValues.region_debit_value == str(dict_you1["upm2_region_debit_value_H"])) &
                                                        (RetailerCommissionValues.region_credit_value == str(dict_you1["upm2_region_credit_value_H"])) &
                                                        (RetailerCommissionValues.region_prepaid_value == str(dict_you1["upm2_region_prepaid_value_H"])) 
                                                    ).execute()
                    flash('Updated Sucessfully', 'success')
                            
                            
                except Exception as e:
                    flash('Error Update Unsucessfull:{}'.format(e), 'error')
            except AttributeError:
                flash('Update Unsucessfull', 'error')
                flash('Wrong Values for Entities, missing : ', 'error')
            except ValueError:
                flash('Wrong Values colon : Not allow in Percentage & Fixed type', 'error')

            return redirect(url_for('retailer_commission'))

        # CREATE BLOCK 
        else:
            try:
                a = request.form.to_dict()
                dict_you3 = {key: a[key] for key in a.keys() if a[key] != ""}
                check_retailer_id = (RetailerCommissionRules.select().where((RetailerCommissionRules.institution_id == str(dict_you3["inst_id"])) & (RetailerCommissionRules.retailer_id == str(dict_you3["retailer_id"])) & (RetailerCommissionRules.channel == str(dict_you3["channel"]))).dicts().iterator())                                              
                data=[k for k in check_retailer_id]
                card_type_data=[ct['commision_type'] for ct in data]
                if((('1' in card_type_data) and ('3' in card_type_data)) or (('2' in card_type_data) and ('3' in card_type_data))):pass
                else:
                    for k in data:
                        if k['commision_type'] == '1' or k['commision_type'] == '2':
                            if ':' not in str(dict_you3["debit_value"]) and ':' not in str(dict_you3["credit_value"]) and ':' not in str(dict_you3["prepaid_value"]) and ':' not in str(dict_you3["mcc_debit_value"]) and ':' not in str(dict_you3["mcc_credit_value"]) and ':' not in str(dict_you3["mcc_prepaid_value"]) and ':' not in str(dict_you3["bin_value"]) and ':' not in str(dict_you3["rubro_debit_value"]) and ':' not in str(dict_you3["rubro_credit_value"]) and ':' not in str(dict_you3["rubro_prepaid_value"]) and ':' not in str(dict_you3["region_debit_value"]) and ':' not in str(dict_you3["region_credit_value"]) and ':' not in str(dict_you3["region_prepaid_value"]):result=True
                            else:raise ValueError
                        elif k['commision_type'] == '3' and k['card_type']== '1':
                            if ':'  in str(dict_you3["debit_value"]) and ':'  in str(dict_you3["credit_value"]) and ':' in str(dict_you3["prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['mcc'] == '1' :
                            if ':'  in str(dict_you3["mcc_debit_value"]) and ':'  in str(dict_you3["mcc_credit_value"]) and ':' in str(dict_you3["mcc_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['bin'] == '1' :
                            if ':'  in str(dict_you3["bin_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['rubro'] == '1' :
                            if ':'  in str(dict_you3["rubro_debit_value"]) and ':'  in str(dict_you3["rubro_credit_value"]) and ':' in str(dict_you3["rubro_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['commision_type'] == '3' and k['region'] == '1' :
                            if ':'  in str(dict_you3["region_debit_value"]) and ':'  in str(dict_you3["region_credit_value"]) and ':' in str(dict_you3["region_prepaid_value"]):result=True
                            else: raise AttributeError
                try:
                    RetailerCommissionValues.create(institution_id=str(request.form.get("inst_id",'')),
                                                        retailer_id=str(request.form.get("retailer_id",'')),
                                                        channel=str(request.form.get("channel",'')),
                                                        message_type=str(request.form.get("message_type",'')),
                                                        processing_code=str(request.form.get("processing_code",'')),
                                                        response_code=str(request.form.get("response_code",'')),
                                                        debit_value=str(request.form.get("debit_value",0)),
                                                        credit_value=str(request.form.get("credit_value",0)),
                                                        prepaid_value=str(request.form.get("prepaid_value",0)),
                                                        mcc=str(request.form.get("mcc",'')),
                                                        mcc_debit_value=str(request.form.get("mcc_debit_value",0)),
                                                        mcc_credit_value=str(request.form.get("mcc_credit_value",0)),
                                                        mcc_prepaid_value=str(request.form.get("mcc_prepaid_value",0)),
                                                        bin=str(request.form.get("bin")),
                                                        bin_value=str(request.form.get("bin_value")),
                                                        domestic_value=str(request.form.get("d_value")),
                                                        international_value=str(request.form.get("i_value")),
                                                        rubro=str(request.form.get("rubro",'')),
                                                        rubro_debit_value=str(request.form.get("rubro_debit_value",0)),
                                                        rubro_credit_value=str(request.form.get("rubro_credit_value",0)),
                                                        rubro_prepaid_value=str(request.form.get("rubro_prepaid_value",0)),
                                                        region=str(request.form.get("region",'')),
                                                        region_debit_value=str(request.form.get("region_debit_value",0)),
                                                        region_credit_value=str(request.form.get("region_credit_value",0)),
                                                        region_prepaid_value=str(request.form.get("region_prepaid_value",0))
                                                        )
                    flash('Commission Profile Created Sucessfully', 'success')

                except Exception as e:
                    flash('Error in Create Commission Profile:{}'.format(e), 'error')

            except AttributeError:
                flash('Error in Create Commission Profile', 'error')
                flash('Wrong Values for Entities, missing : ', 'error')
            except ValueError:
                flash('Wrong Values colon : Not allow in Percentage & Fixed type', 'error')
            return redirect(url_for('retailer_commission'))

    return render_template('ret_commission.html', IID=i_id, Pro_Code=pro_code, Ret_Com1=iid_rid, Ret_Com=ret_comm, Msg_Type=msg_type, Res_Code=res_code, IR = iid_rid)


@app.get('/commission_slabs')
@app.post('/commission_slabs')
@login_required
def commission_slabs():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    error = 0
    com = []
    prox_id = 0

    slabs_types = ["Interval", "Plain", "By_amount"]
    commission_types = ["Fixed_value", "By_percentage"]

    for conf in CommissionSlabs.select(CommissionSlabs.id):
        if(prox_id <= conf.id):
            prox_id = conf.id + 1

    for conf in CommissionSlabs.select().where(CommissionSlabs.profile_id == request.args.get('profile_id')):
        com.append((conf.id, conf.profile_id, conf.slabs_type, conf.commission_type, conf.min_limit, conf.max_limit, conf.value))

    error = None
    if request.method == 'POST':
        if not request.form['profile_id1']:
            t = CommissionSlabs.update(id=request.form["id"],
                                       profile_id=request.form["profile_id"],
                                       slabs_type=request.form["slabs_type"],
                                       commission_type=request.form["commission_type"],
                                       min_limit=request.form["min_limit"],
                                       max_limit=request.form["max_limit"],
                                       value=request.form["value"]
                                       ).where(CommissionSlabs.id == request.form["id"])
            t.execute()
        else:

            print(request.form)
            CommissionSlabs.create(id=prox_id,
                                   profile_id=request.form["profile_id1"],
                                   slabs_type=request.form["slabs_type1"],
                                   commission_type=request.form["commission_type1"],
                                   min_limit=request.form["min_limit1"],
                                   max_limit=request.form["max_limit1"],
                                   value=request.form["value1"])

        return redirect(url_for('commission_slabs', profile_id=request.args.get('profile_id')))

    return render_template('commission_slabs.html', com=com, slabs_types=slabs_types, commission_types=commission_types, profile_id=request.args.get('profile_id'))


@app.route('/logout')
@login_required
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.get('/enable_validations')
@app.post('/enable_validations')
def enable_validations():    
    result = {}
    institutions = InstitutionId.select().limit(3).dicts()
    vals = EnableValidations.select().dicts()

    if request.method == 'POST':
        if "filter" in request.form.keys():
            a = request.form.to_dict()
            data = {key: a[key] for key in a.keys() if a[key] != ""}
            print(data["val_group"])
            return render_template('enable_validations.html', result=vals, institutions=institutions, colname=data["val_group"])

        else:
            dataupdate = request.get_json()
            #data = {key: a[key] for key in a.keys() if a[key] != ""}
            for data in dataupdate:
                EnableValidations.update(Val_status=data["Val_status"]).where(
                    EnableValidations.Val_group == data["Val_group"], EnableValidations.Val_desc == data["Val_desc"]).execute()
            #data = dataupdate.to_dict()

            #EnableValidations.insert_many(dataupdate).execute()

            #flash('Changes saved successfully','success')
            #return render_template('enable_validations.html',result=vals , institutions=institutions )

        return redirect(url_for('enable_validations'))
    return render_template('enable_validations.html', result=vals, institutions=institutions, colname='Retailer')


@app.get('/transaction_history')
@app.post('/transaction_history')
@login_required
def transaction_history():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    extract_file_cols = TransactionHistory._meta.sorted_field_names
    result = TransactionHistory.select().dicts().limit(100)
    if request.method == 'POST':
        if "copy_adj_s" in request.form.keys():
            a = request.form.to_dict()
            dict_add = {}
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            for key in dict_you.keys():
                if(key != "id"):
                    dict_add[key] = dict_you[key]

            try:
                print(dict_add, 'request from txn_adj')
                dict_add["TimeStamp"] = TransactionHistory.select().where(TransactionHistory.MessageType == dict_add["MessageType"], TransactionHistory.SystemsTraceAuditNumber == dict_add["SystemsTraceAuditNumber"], TransactionHistory.SettlementDate == dict_add["SettlementDate"]).dicts()[0]["TimeStamp"]
                ManualAdjustmentsExtractFile.create(**dict_add)
                flash('Reversal Created Sucessfully', 'sucess')
            except Exception as e:
                raise
            return redirect(url_for('transaction_history'))

        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}

            try: key1 = dict_you["key1"]
            except: key1 = 0
            try: key2 = dict_you["key2"]
            except: key2 = 0
            try: key3 = dict_you["key3"]
            except: key3 = 0
            try: key4 = dict_you["key4"]
            except: key4 = 0

            try:
                """
                key1 = MessageType
                key2 = RetailerData (CardAcceptorIdentification)
                key3 = Tran Date [MMDD]
                key4 = RetrievalReferenceNumber

                """
                if key1 == 0 and key2 == 0 and key3 == 0 and key4 == 0:
                    flash('No Input Data Entered In Serach Box ...!! :'.format(
                        key1, key2, key3, key4), 'error')
                    result = TransactionHistory.select().dicts().limit(100)
                    return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Search using MessageType
                elif key1 != 0 and key2 == 0 and key3 == 0 and key4 == 0:
                    result = TransactionHistory.select().where(
                        TransactionHistory.MessageType == key1).dicts().limit(100)
                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('The search Message Type - {} could not be found! :'.format(key1), 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Search using RetailerData
                elif key2 != 0 and key1 == 0 and key3 == 0 and key4 == 0:
                    result = TransactionHistory.select().where(
                        TransactionHistory.CardAcceptorIdentification == key2).dicts().limit(100)
                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('The search Retailer ID - {} could not be found! :'.format(key2), 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Search using RetrievalReferenceNumber
                elif key4 != 0 and key2 == 0 and key3 == 0 and key1 == 0:
                    result = TransactionHistory.select().where(
                        TransactionHistory.RetrievalReferenceNumber == key4).dicts().limit(100)
                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('The search Retrieval Reference Number (RRN) item {} could not be found! :'.format(
                            key4), 'error')
                        result = TransactionHistory.select().dicts()
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Search using Settelment Date [MMDD]
                elif key3 != 0 and key2 == 0 and key4 == 0 and key1 == 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where(
                        TransactionHistory.LocalTransactionDate == date_).dicts().limit(100)
                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('The search date item {} could not be found! :'.format(
                            key3), 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key2 & Key3 & Key4
                elif key1 != 0 and key2 != 0 and key3 != 0 and key4 != 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2) & (
                        TransactionHistory.MessageType == key1) & (TransactionHistory.LocalTransactionDate == date_)
                        & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts()
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key2 & Key3
                elif key1 != 0 and key2 != 0 and key3 != 0 and key4 == 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2) & (
                        TransactionHistory.MessageType == key1) & (TransactionHistory.LocalTransactionDate == date_)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key2 & Key4
                elif key1 != 0 and key2 != 0 and key3 == 0 and key4 != 0:
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2) & (
                        TransactionHistory.MessageType == key1) & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key3 & Key4
                elif key1 != 0 and key2 == 0 and key3 != 0 and key4 != 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.MessageType == key1)
                                                               & (TransactionHistory.LocalTransactionDate == date_)
                                                               & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key2 & Key3 & Key4
                elif key1 == 0 and key2 != 0 and key3 != 0 and key4 != 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2)
                                                               & (TransactionHistory.LocalTransactionDate == date_)
                                                               & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key2
                elif key1 != 0 and key2 != 0 and key3 == 0 and key4 == 0:
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2) & (
                        TransactionHistory.MessageType == key1)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash('Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key3 & Key4
                elif key1 == 0 and key2 == 0 and key3 != 0 and key4 != 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.LocalTransactionDate == date_)
                                                               & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash(
                            'Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts()
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key4
                elif key1 != 0 and key2 == 0 and key3 == 0 and key4 != 0:
                    result = TransactionHistory.select().where((TransactionHistory.MessageType == key1)
                                                               & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash(
                            'Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key2 & Key3
                elif key1 == 0 and key2 != 0 and key3 != 0 and key4 == 0:
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2)
                                                               & (TransactionHistory.LocalTransactionDate == date_)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash(
                            'Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key1 & Key3
                elif (key1 != 0) and (key2 == 0) and (key3 != 0) and (key4 == 0):
                    date_ = str(key3.split("-")[1])+str(key3.split("-")[2])
                    result = TransactionHistory.select().where((TransactionHistory.MessageType == key1)
                                                               & (TransactionHistory.LocalTransactionDate == date_)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash(
                            'Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                # Key2 & Key4
                elif key1 == 0 and key2 != 0 and key3 == 0 and key4 != 0:
                    result = TransactionHistory.select().where((TransactionHistory.CardAcceptorIdentification == key2)
                                                               & (TransactionHistory.RetrievalReferenceNumber == key4)).dicts().limit(100)

                    if result:
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)
                    else:
                        flash(
                            'Base On Give Inputs - No Record Was Found ...!', 'error')
                        result = TransactionHistory.select().dicts().limit(100)
                        return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

                else:
                    flash('The search item {} {} {} {} could not be found...!'.format(
                        key1, key2, key3, key4), 'error')
                    result = TransactionHistory.select().dicts().limit(100)
                    return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)

            except Exception as e:
                flash('Error in Search,{}'.format(e), 'error')

            return redirect(url_for('transaction_history'))

        else:
            a = request.form.to_dict()
            dict_add = {}
            dict_you = {key: a[key] for key in a.keys() if a[key] != ""}
            for key in dict_you.keys():
                if(key != "id"):
                    dict_add[key] = dict_you[key]
            try:
                dict_add["TimeStamp"] = TransactionHistory.select().where(TransactionHistory.MessageType == dict_add["MessageType"], TransactionHistory.SystemsTraceAuditNumber == dict_add["SystemsTraceAuditNumber"],TransactionHistory.SettlementDate == dict_add["SettlementDate"], TransactionHistory.PrimaryAccountNumberPAN == dict_add["PrimaryAccountNumberPAN"]).dicts()[0]["TimeStamp"]
                ManualAdjustmentsExtractFile.create(**dict_add)
                flash('Reversal Created Sucessfully', 'sucess')
            except Exception as e:
                flash('Error in Create Reversal:{}'.format(e), 'error')

            return redirect(url_for('transaction_history'))
    return render_template('transaction_history.html', result=result, extract_file_cols=extract_file_cols)


@app.get('/permissions')
@app.post('/permissions')
@login_required
def permissions():
    if request.method == 'GET':
        user = request.args.get('user', None)
        user_db = Users.get(username=user)
        try:
            permissions = ast.literal_eval(user_db.permissions)
        except:
            permissions = None
        permissions = permissions if permissions else url()  # get from user table

        return render_template('permissions.html', permissions=permissions, user=user)

    if request.method == 'POST':

        data = request.form.to_dict()
        read = data.get('read', False)
        write = data.get('write', False)
        create = data.get('create', False)
        delete = data.get('delete', False)
        user = data.get('user', False)
        user_db = Users.get(username=user)
        permission_string = ''

        url_to = [k for k in data.keys() if k not in ['read', 'write',
                                                      'create', 'delete', 'user']][0]

        permission_string += 'r' if read else ''
        permission_string += 'w' if write else ''
        permission_string += 'c' if create else ''
        permission_string += 'd' if delete else ''

        try:
            permissions = ast.literal_eval(user_db.permissions)
        except:
            permissions = None
        permissions = permissions if permissions else url()  # get from user table
        permissions[url_to] = permission_string
        user_db.permissions = permissions
        user_db.save()

        flash('Permissions updated, please log in again')
        return render_template('permissions.html', permissions=permissions, user=user)



#################################### * CCX24 + CCX30 * ####################################

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

@app.get("/search_geopagos_csv_view")
@app.post("/search_geopagos_csv_view")
@login_required
def search_geopagos_csv_view():
    endpoint = request.endpoint
    #is_allowed_to_read(endpoint, session["permissions"])

    path = './CompensationReports/DepositRetailerReports/'
    # print(f"request.args = {request.args.to_dict()}")
    # print(f"request.form = {request.form.to_dict()}")

    if request.method == 'POST':
        csv_data, searched_date = [], None
        if 'searchSingle' in request.form.to_dict().keys():
            searched_date = date = request.form.get('key1')
            retId = request.form.get('key2', 'NoRetId')
            print(f"{searched_date} | {retId}")
            prefix = date.replace('-', '')
            year, month, day = prefix[:4], prefix[4:6], prefix[6:]
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            fname = prefix+'_GPSMARTPOS_DepositDetails.csv'
            folder = f'{path}/{months[int(month)-1]}_{year}/'
            fileName = folder+fname

            try:
                with open(fileName, newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                    next(reader)  # skip header
                    for row in reader:
                        if (retId != "") and (retId == row[1]):
                            csv_data.append(row)
                        elif (retId == ""):
                            csv_data.append(row)
            except Exception as e:
                fname = prefix+'_GPSMARTPOS_DepositDetailsR1.csv'
                fileName = folder+fname
                try:
                    with open(fileName, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        for row in reader:
                            if (retId != "") and (retId == row[1]) and (retId != None):
                                csv_data.append(row)
                            elif (retId == ""):
                                csv_data.append(row)
                except Exception as e:
                    flash('Data Not Found', 'error')
            return render_template("search_geopagos.html", csv_data=csv_data, searched_date=searched_date, singleSearch=True, retID=retId)

        elif 'searchMulti_DPR' in request.form.to_dict().keys() or 'searchMulti_TD' in request.form.to_dict().keys():
            startDate, endDate, ruth = request.form.get('startDate', None), request.form.get('endDate', None), request.form.get('ruth', None)
            csv_data, allFiles = [], []
            # print(f"startDate = {startDate} | endDate = {endDate} | ruth = {ruth}")
            sd = dt(int(startDate.split('-')[0]), int(startDate.split('-')[1]), int(startDate.split('-')[2]))
            ed = dt(int(endDate.split('-')[0]), int(endDate.split('-')[1]), int(endDate.split('-')[2])+1)
            for single_date in daterange(sd, ed):
                yearMonth = single_date.strftime(r'%b_%Y')
                fileDate = single_date.strftime(r'%y%m%d')
                listFile = glob.glob(f'{path}{yearMonth}/*{fileDate}*')
                if listFile:
                    allFiles.extend(listFile)
                    del listFile

            depositFiles, trnxFiles = [], []
            for af in allFiles:
                if '_DepositDetails' in af: depositFiles.append(af)
                elif '_TransactionsDetails' in af: trnxFiles.append(af)
            
            if 'ruth' in request.form.to_dict().keys():
                ruthFromUserArray = request.form.to_dict()['ruth'].split('\r\n')
                # print(f"ruthFromUserArray = {len(ruthFromUserArray)}")
                # print(f"ruthFromUserArray = {ruthFromUserArray}")

            if 'searchMulti_DPR' in request.form.to_dict().keys():
                for eachDF in depositFiles:
                    with open(eachDF, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        if ('ruth' in request.form.to_dict().keys()) and ('' not in ruthFromUserArray):
                            for row in reader:
                                if row[2] in ruthFromUserArray:
                                    csv_data.append(row)
                        else:
                            for row in reader: csv_data.append(row)

                return render_template("search_geopagos.html", csv_data=csv_data, start_date=startDate, end_date=endDate, depositData=True, ruthData=request.form.to_dict()['ruth'])
            
            elif 'searchMulti_TD' in request.form.to_dict().keys():
                header = ['IDP', 'RUT', 'Tipo', 'Fecha', 'Codigo de comercio', 'Comercio', 'Activo', 'Sucursal', 'Region', 'TransactionID',
                        'Monto bruto', 'Monto bruto sin reversas', 'Arancel', 'IVA Arancel', 'Porcentaje Arancel', 'Monto neto', 'Monto neto sin reversas',
                        'Fecha de disponibilidad original', 'Fecha de pago', 'Estado deposito', 'ID Deposito', 'Fecha de anulacion',
                        'Usuario de la aplicacion', 'Estado', 'E-mail del cliente', 'Nombre del cliente', 'RUN', 'Marca de tarjeta', 'Numero tarjeta',
                        'Tipo tarjeta', 'Cantidad de cuotas', 'Cod banco emisor', 'Nombre banco emisor', 'N Autorizacion', 'Mensaje de respuesta',
                        'Lector', 'Tipo de Venta', 'Geolocalizacion']
                for eachTD in trnxFiles:
                    with open(eachTD, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        if ('ruth' in request.form.to_dict().keys()) and ('' not in ruthFromUserArray):
                            for row in reader:
                                if row[1] in ruthFromUserArray:
                                    csv_data.append(row)
                        else:
                            for row in reader: csv_data.append(row)
                return render_template("search_geopagos.html", csv_data=csv_data, start_date=startDate, end_date=endDate, tbHead=header, trnxData=True, ruthData=request.form.to_dict()['ruth'])

    return render_template("search_geopagos.html")

@app.get("/search_geopagos_detail")
@login_required
def search_geopagos_detail():
    endpoint = request.endpoint
    is_allowed_to_read(endpoint, session["permissions"])

    # print(request.args)
    path = "./CompensationReports/DepositRetailerReports"
    csv_data = []
    header = ['IDP', 'RUT', 'Tipo', 'Fecha', 'Codigo de comercio', 'Comercio', 'Activo', 'Sucursal', 'Region', 'TransactionID',
              'Monto bruto', 'Monto bruto sin reversas', 'Arancel', 'IVA Arancel', 'Porcentaje Arancel', 'Monto neto', 'Monto neto sin reversas',
              'Fecha de disponibilidad original', 'Fecha de pago', 'Estado deposito', 'ID Deposito', 'Fecha de anulacion',
              'Usuario de la aplicacion', 'Estado', 'E-mail del cliente', 'Nombre del cliente', 'RUN', 'Marca de tarjeta', 'Numero tarjeta',
              'Tipo tarjeta', 'Cantidad de cuotas', 'Cod banco emisor', 'Nombre banco emisor', 'N Autorizacion', 'Mensaje de respuesta',
              'Lector', 'Tipo de Venta', 'Geolocalizacion']
    IDP = request.args.get('key1')
    trnxDate = request.args.get('key2')
    prefix = trnxDate.replace('-', '')
    day, month, year = prefix[:2], prefix[2:4], prefix[4:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    folder = f'{path}/{months[int(month)-1]}_{year}/'
    fname = year+month+day+'_GPSMARTPOS_TransactionsDetails.csv'
    fileName = folder+fname
    if(os.path.exists(fileName)):
        # print(f"fileName Found = {fileName}")
        with open(fileName, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar="|")
            next(reader)  # skip header
            for row in reader:
                if (IDP != "") and (IDP == row[0]):
                    csv_data.append(row)
        # print(header)
        # print(csv_data)
    else:
        fname = year+month+day+'_GPSMARTPOS_TransactionsDetailsR2.csv'
        altFname = folder+fname
        # print(f"altFname Found = {altFname}")
        with open(altFname, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar="|")
            next(reader)  # skip header
            for row in reader:
                if (IDP != "") and (IDP == row[0]):
                    csv_data.append(row)
        # print(header)
        # print(csv_data)
    return render_template('search_geopagos_detail.html', tbHead=header, idpData=csv_data, IDP=IDP, searchDate=trnxDate)


################# * GPLINK * #################

@app.get("/search_gplink_csv_view")
@app.post("/search_gplink_csv_view")
@login_required
def search_gplink_csv_view():
    path = './GPLINK/CompensationReports/DepositRetailerReports/'
    # print(f"request.args = {request.args.to_dict()}")
    # print(f"request.form = {request.form.to_dict()}")

    if request.method == 'POST':
        csv_data, searched_date = [], None
        print("search signele",request.form.to_dict().keys())
        if 'searchSingle' in request.form.to_dict().keys():
            searched_date = date = request.form.get('key1')
            retId = request.form.get('key2', 'NoRetId')
            print(f"{searched_date} | {retId}")
            prefix = date.replace('-', '')
            year, month, day = prefix[:4], prefix[4:6], prefix[6:]
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            fname = prefix+'_GPLINK_DepositDetails.csv'
            folder = f'./GPLINK/CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
            fileName = folder+fname
            print('2310',fileName)

            try:
                with open(fileName, newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                    next(reader)  # skip header
                    for row in reader:
                        if (retId != "") and (retId == row[1]):
                            csv_data.append(row)
                        elif (retId == ""):
                            csv_data.append(row)
            except Exception as e:
                fname = prefix+'_GPLINK_DepositDetailsR1.csv'
                fileName = folder+fname
                print('filename', fileName)
                try:
                    with open(fileName, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        for row in reader:
                            if (retId != "") and (retId == row[1]) and (retId != None):
                                csv_data.append(row)
                            elif (retId == ""):
                                csv_data.append(row)
                except Exception as e:
                    flash('Data Not Found', 'error')
            return render_template("search_gplink.html", csv_data=csv_data, searched_date=searched_date, singleSearch=True, retID=retId)

        elif 'searchMulti_DPR' in request.form.to_dict().keys() or 'searchMulti_TD' in request.form.to_dict().keys():
            startDate, endDate, ruth = request.form.get('startDate', None), request.form.get('endDate', None), request.form.get('ruth', None)
            csv_data, allFiles = [], []
            # print(f"startDate = {startDate} | endDate = {endDate} | ruth = {ruth}")
            sd = dt(int(startDate.split('-')[0]), int(startDate.split('-')[1]), int(startDate.split('-')[2]))
            ed = dt(int(endDate.split('-')[0]), int(endDate.split('-')[1]), int(endDate.split('-')[2])+1)
            for single_date in daterange(sd, ed):
                yearMonth = single_date.strftime(r'%b_%Y')
                fileDate = single_date.strftime(r'%y%m%d')
                listFile = glob.glob(f'{path}{yearMonth}/*{fileDate}*')
                if listFile:
                    allFiles.extend(listFile)
                    del listFile

            depositFiles, trnxFiles = [], []
            for af in allFiles:
                if '_DepositDetails' in af: depositFiles.append(af)
                elif '_TransactionsDetails' in af: trnxFiles.append(af)
            
            if 'ruth' in request.form.to_dict().keys():
                ruthFromUserArray = request.form.to_dict()['ruth'].split('\r\n')
                # print(f"ruthFromUserArray = {len(ruthFromUserArray)}")
                # print(f"ruthFromUserArray = {ruthFromUserArray}")

            if 'searchMulti_DPR' in request.form.to_dict().keys():
                for eachDF in depositFiles:
                    with open(eachDF, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        if ('ruth' in request.form.to_dict().keys()) and ('' not in ruthFromUserArray):
                            for row in reader:
                                if row[2] in ruthFromUserArray:
                                    csv_data.append(row)
                        else:
                            for row in reader: csv_data.append(row)

                return render_template("search_gplink.html", csv_data=csv_data, start_date=startDate, end_date=endDate, depositData=True, ruthData=request.form.to_dict()['ruth'])
            
            elif 'searchMulti_TD' in request.form.to_dict().keys():
                header = ['IDP', 'RUT', 'Tipo', 'Fecha', 'Codigo de comercio', 'Comercio', 'Activo', 'Sucursal', 'Region', 'TransactionID',
                        'Monto bruto', 'Monto bruto sin reversas', 'Arancel', 'IVA Arancel', 'Porcentaje Arancel', 'Monto neto', 'Monto neto sin reversas',
                        'Fecha de disponibilidad original', 'Fecha de pago', 'Estado deposito', 'ID Deposito', 'Fecha de anulacion',
                        'Usuario de la aplicacion', 'Estado', 'E-mail del cliente', 'Nombre del cliente', 'RUN', 'Marca de tarjeta', 'Numero tarjeta',
                        'Tipo tarjeta', 'Cantidad de cuotas', 'Cod banco emisor', 'Nombre banco emisor', 'N Autorizacion', 'Mensaje de respuesta',
                        'Lector', 'Tipo de Venta', 'Geolocalizacion']
                for eachTD in trnxFiles:
                    with open(eachTD, newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=";", quotechar="|")
                        next(reader)  # skip header
                        if ('ruth' in request.form.to_dict().keys()) and ('' not in ruthFromUserArray):
                            for row in reader:
                                if row[1] in ruthFromUserArray:
                                    csv_data.append(row)
                        else:
                            for row in reader: csv_data.append(row)
                return render_template("search_gplink.html", csv_data=csv_data, start_date=startDate, end_date=endDate, tbHead=header, trnxData=True, ruthData=request.form.to_dict()['ruth'])

    return render_template("search_gplink.html")


@app.get("/search_gplink_csv_download/<path:path>")
@login_required
def search_gplink_csv_download(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_GPLINK_TransactionsDetails.csv'
    folder = f'./GPLINK/CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
    fileName = folder+fname
    if(os.path.exists(fileName)):
        return send_from_directory(folder, fname, as_attachment=True)
    print(fileName)
    altFname = prefix+'_GPLINK_TransactionsDetailsR2.csv'
    return send_from_directory(folder, altFname, as_attachment=True)


@app.get("/gplink_download_deposit/<path:path>")
@login_required
def search_gplink_download_deposit(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_GPLINK_DepositDetails.csv'
    folder = f'./GPLINK/CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
    fileName = folder+fname
    if(os.path.exists(fileName)):
        return send_from_directory(folder, fname, as_attachment=True)
    altFname = prefix+'_GPLINK_DepositDetailsR1.csv'
    print(fileName)
    return send_from_directory(folder, altFname, as_attachment=True)


@app.get('/gplink_download/<path:path>')
@login_required
def gplink_download(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_GPLINK_DepositRetailerReports.zip'
    folder = './GPLINK/CompensationReports/DepositRetailerReports/{}_{}/'.format(months[int(month)-1], year)
    return send_from_directory(folder, fname, as_attachment=True)


@app.get("/search_gplink_detail")
@login_required
def search_gplink_detail():
    print(request.args)
    csv_data = []
    header = ['IDP', 'RUT', 'Tipo', 'Fecha', 'Codigo de comercio', 'Comercio', 'Activo', 'Sucursal', 'Region', 'TransactionID',
              'Monto bruto', 'Monto bruto sin reversas', 'Arancel', 'IVA Arancel', 'Porcentaje Arancel', 'Monto neto', 'Monto neto sin reversas',
              'Fecha de disponibilidad original', 'Fecha de pago', 'Estado deposito', 'ID Deposito', 'Fecha de anulacion',
              'Usuario de la aplicacion', 'Estado', 'E-mail del cliente', 'Nombre del cliente', 'RUN', 'Marca de tarjeta', 'Numero tarjeta',
              'Tipo tarjeta', 'Cantidad de cuotas', 'Cod banco emisor', 'Nombre banco emisor', 'N Autorizacion', 'Mensaje de respuesta',
              'Lector', 'Tipo de Venta', 'Geolocalizacion']
    IDP = request.args.get('key1')
    trnxDate = request.args.get('key2')
    prefix = trnxDate.replace('-', '')
    day, month, year = prefix[:2], prefix[2:4], prefix[4:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    folder = f'./GPLINK/CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
    fname = year+month+day+'_GPLINK_TransactionsDetails.csv'
    fileName = folder+fname
    print(IDP, trnxDate, fileName, os.path.exists(fileName))
    if(os.path.exists(fileName)):
        with open(fileName, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar="|")
            next(reader)  # skip header
            for row in reader:
                if (IDP != "") and (IDP == row[0]):
                    csv_data.append(row)
    else:
        fname = year+month+day+'_GPLINK_TransactionsDetailsR2.csv'
        altFname = folder+fname
        print(f"altFname Found = {altFname}")
        with open(altFname, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar="|")
            next(reader)  # skip header
            for row in reader:
                if (IDP != "") and (IDP == row[0]):
                    csv_data.append(row)
    return render_template('search_gplink_detail.html', tbHead=header, idpData=csv_data, IDP=IDP, searchDate=trnxDate)


################## * CCX28 * ##################

#################################### * CCX28 * ####################################

@app.get('/discount_and_promotions')
@app.post('/discount_and_promotions')
@login_required
def discount_and_promotions():
    discounts = DiscountAndPromotionRules.select().dicts()
    CT = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionType")
    CST = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")
    i_id = InstitutionId.select()

    if request.method == 'POST':
        # DELETE BLOCK
        if "delete" in request.form.keys():
            a = request.form.to_dict()
            dict_you3 = {key: a[key] for key in a.keys() if a[key] != ""}
            # st = True if str(dict_you3["status"]) == "1" else False

            try:
                DiscountAndPromotionRules.delete().where(
                    (DiscountAndPromotionRules.retailer_id == str(dict_you3["retailer_id"]))&
                    (DiscountAndPromotionRules.institution_id == str(dict_you3["institution_id"]))&
                    (DiscountAndPromotionRules.channel == str(dict_you3["channel"]))&
                    (DiscountAndPromotionRules.discount_type == str(dict_you3["discount_type"])) &
                    (DiscountAndPromotionRules.discount_sub_type == str(dict_you3["discount_sub_type"])) &
                    (DiscountAndPromotionRules.card_type == str(dict_you3["card_type"])) &
                    (DiscountAndPromotionRules.mcc == str(dict_you3["mcc"])) &
                    (DiscountAndPromotionRules.bin == str(dict_you3["bin"])) &
                    (DiscountAndPromotionRules.transaction_identifier == str(dict_you3["transaction_identifier"])) &
                    (DiscountAndPromotionRules.rubro == str(dict_you3["rubro"]))&
                    (DiscountAndPromotionRules.priority == str(dict_you3["priority"]))                  
                ).execute()
                flash('Sucessfully deleted', 'success')
            except Exception as e:
                flash('Error in delete', 'error')
            CT = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionType")
            CST = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")
            # return redirect(url_for('discount_and_promotions'))
            return render_template('discount_and_promotions.html', discounts=discounts,C_T=CT, C_S_T=CST,IID=i_id)


        elif "update" in request.form.keys():
            try:
                a = request.form.to_dict()
                dict_you1 = {key: a[key] for key in a.keys() if a[key] != ""}
                st = True if str(dict_you1["status"]) == "True" else False

                if str(dict_you1["ret_id"]) != 'DEFAULT':
                    check_retailer_id = RetailerId.select().where((RetailerId.RetailerId == str(dict_you1["ret_id"]))).execute()
                    if len(check_retailer_id) < 1: raise Exception

                DiscountAndPromotionRules.update(institution_id=str(dict_you1["institution_id"]),
                                                retailer_id=str(dict_you1["ret_id"]),
                                                channel=str(dict_you1["channel"]),
                                                discount_type=str(dict_you1["discount_type"]),
                                                discount_sub_type=str(dict_you1["discount_sub_type"]),
                                                card_type=str(dict_you1["card_type"]),
                                                transaction_identifier=str(dict_you1["transaction_identifier"]),
                                                mcc=str(dict_you1["mcc"]),
                                                rubro=str(dict_you1["rubro"]),
                                                region=str(dict_you1["region"]),
                                                priority=str(dict_you1["ump2_priority"]),
                                                status=st,
                                                bin=str(dict_you1["bin"])
                                                ).where(
                                                    (DiscountAndPromotionRules.institution_id == str(dict_you1["institution_id"]))&
                                                    (DiscountAndPromotionRules.retailer_id == str(dict_you1["ret_id"])) & 
                                                    (DiscountAndPromotionRules.channel == str(dict_you1["channel"]))
                                                    ).execute()
                flash('Updated Sucessfully', 'success')

            except Exception as e:
                flash('Update Unsucessfull {}'.format(e), 'error')
                flash('Retailer ID not present in database', 'error')

            
            return redirect(url_for('discount_and_promotions'))

        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you2 = {key: a[key] for key in a.keys() if a[key] != ""}
            try:
                key = dict_you2["key1"]
                search_data = DiscountAndPromotionRules.select().where(DiscountAndPromotionRules.retailer_id == str(key) )

                if len(search_data) == 0:
                    flash('The search item {} could not be found! :'.format(key),'error')
                return render_template('discount_and_promotions.html', discounts=search_data)
            except Exception as e:
                flash('Error in Search, please put correct value','error')
            return redirect(url_for('discount_and_promotions'))
            
        #CREATE MODULE
        else:
            try:
                a = request.form.to_dict()
                dict_you2 = {key: a[key] for key in a.keys() if a[key] != ""}
                st = True if str(dict_you2["status"]) == "True" else False

                if str(dict_you2["retailer_id"]) != 'DEFAULT':
                    check_retailer_id = RetailerId.select().where((RetailerId.RetailerId == str(dict_you2["retailer_id"]))).execute()
                    if len(check_retailer_id) < 1: raise Exception

                DiscountAndPromotionRules.create(institution_id=str(dict_you2['institution_id']),
                                                retailer_id=str(dict_you2['retailer_id']),
                                                channel=str(dict_you2['channel']),
                                                discount_type=str(dict_you2["dis_type"]),
                                                discount_sub_type=str(dict_you2["dis_sub_type"]),
                                                card_type=str(dict_you2["card_type"]),
                                                transaction_identifier=str(dict_you2["transaction_identifier"]),
                                                mcc=str(dict_you2["mcc"]),
                                                bin=str(dict_you2["bin"]),
                                                rubro=str(dict_you2["rubro"]),
                                                priority=str(dict_you2['priority']),
                                                region=str(dict_you2["region"]),
                                                status=st)
                flash('Discount Profile Created Sucessfully', 'success')
            
            except Exception as e:
                flash('Error in Create Discount Profile:{}'.format(e), 'error')
                flash('Retailer ID Not Present in Database', 'error')


                

            CT = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionType")
            CST = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommisionSubType")
            return redirect(url_for('discount_and_promotions'))
            # return render_template('discount_and_promotions.html', discounts=discounts,C_T=CT, C_S_T=CST,IID=i_id)
    return render_template('discount_and_promotions.html', discounts=discounts,C_T=CT, C_S_T=CST,IID=i_id)

@app.get('/discount_and_promotions_type')
@app.post('/discount_and_promotions_type')
@login_required
def discount_and_promotions_type():
    iid_rid = RetailerId.select()
    pro_code = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsTransactionType")
    msg_type = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsMessageType")
    res_code = ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "CommissionsResponseCode")
    i_id = InstitutionId.select()
    iid_rid = RetailerId.select()
    discounts = DiscountAndPromotionValues.select().dicts()
    if request.method == 'POST':
        if "delete" in request.form.keys():
            a = request.form.to_dict()

            dict_you3 = {key: a[key] for key in a.keys() if a[key] != ""}
            try:
                DiscountAndPromotionValues.delete().where((DiscountAndPromotionValues.retailer_id == str(dict_you3["retailer_id"])) &
                (DiscountAndPromotionValues.institution_id == str(dict_you3["institution_id"])) & 
                (DiscountAndPromotionValues.channel == str(dict_you3["channel"])) &
                (DiscountAndPromotionValues.message_type == str(dict_you3["message_type"])) &
                (DiscountAndPromotionValues.processing_code == str(dict_you3["processing_code"])) &
                (DiscountAndPromotionValues.response_code == str(dict_you3["response_code"])) &
                (DiscountAndPromotionValues.debit_value == str(dict_you3["debit_value"])) &
                (DiscountAndPromotionValues.credit_value == str(dict_you3["credit_value"])) &
                (DiscountAndPromotionValues.prepaid_value == str(dict_you3["prepaid_value"])) &
                (DiscountAndPromotionValues.mcc == str(dict_you3["mcc"])) &
                (DiscountAndPromotionValues.mcc_debit_value == str(dict_you3["mcc_debit_value"])) &
                (DiscountAndPromotionValues.mcc_credit_value == str(dict_you3["mcc_credit_value"])) &
                (DiscountAndPromotionValues.mcc_prepaid_value == str(dict_you3["mcc_prepaid_value"])) &
                (DiscountAndPromotionValues.bin == str(dict_you3["bin"])) &
                (DiscountAndPromotionValues.bin_value == str(dict_you3["bin_value"])) &
                (DiscountAndPromotionValues.domestic_value == str(dict_you3["dom_val"])) &
                (DiscountAndPromotionValues.international_value == str(dict_you3["i_val"])) &
                (DiscountAndPromotionValues.rubro == str(dict_you3["rubro"])) &
                (DiscountAndPromotionValues.rubro_debit_value == str(dict_you3["rubro_debit_value"])) &
                (DiscountAndPromotionValues.rubro_credit_value == str(dict_you3["rubro_credit_value"])) &
                (DiscountAndPromotionValues.rubro_prepaid_value == str(dict_you3["rubro_prepaid_value"])) &
                (DiscountAndPromotionValues.region == str(dict_you3["region"])) &
                (DiscountAndPromotionValues.region_debit_value == str(dict_you3["region_debit_value"])) &
                (DiscountAndPromotionValues.region_credit_value == str(dict_you3["region_credit_value"])) &
                (DiscountAndPromotionValues.region_prepaid_value == str(dict_you3["region_prepaid_value"])) 
                ).execute()
                flash('Sucessfully deleted', 'success')
            except Exception as e:
                flash('Error in delete', 'error')
            return redirect(url_for('discount_and_promotions_type'))

        # *SEARCH BLOCK* 
        elif "search" in request.form.keys():
            a = request.form.to_dict()
            dict_you2 = {key: a[key] for key in a.keys() if a[key] != ""}
            try:
                key = dict_you2["key1"]
                search_data = DiscountAndPromotionValues.select().where(DiscountAndPromotionValues.retailer_id == str(key) )
                if len(search_data) == 0:
                    flash('The search item {} could not be found! :'.format(key),'error')

                return render_template('discount_and_promotions_type.html', discounts=search_data,IID=i_id, Pro_Code=pro_code, Ret_Com1=iid_rid, Msg_Type=msg_type, Res_Code=res_code, IR = iid_rid)
                
            except Exception as e:
                flash('Error in Search, please put correct value','error')
            return redirect(url_for('discount_and_promotions_type'))

        # UPDATE BLOCK
        elif "update" in request.form.keys():
            try:
                a = request.form.to_dict()
                dict_you1 = {key: a[key] for key in a.keys() if a[key] != ""}
                check_retailer_id = (DiscountAndPromotionRules.select().where((DiscountAndPromotionRules.institution_id == str(dict_you1["upm2_institution_id"])) & (DiscountAndPromotionRules.retailer_id == str(dict_you1["upm2_retailer_id"])) & (DiscountAndPromotionRules.channel == str(dict_you1["upm2_channel_H"]))).dicts().iterator())                                              
                data=[k for k in check_retailer_id]
                card_type_data=[ct['discount_type'] for ct in data]
                if((('1' in card_type_data) and ('3' in card_type_data)) or (('2' in card_type_data) and ('3' in card_type_data))):pass
                else:
                    for k in data:
                        if k['discount_type'] == '1' or k['discount_type'] == '2':
                            if ':'  not in str(dict_you1["upm2_debit_value"]) and ':'  not in str(dict_you1["upm2_credit_value"]) and ':' not in str(dict_you1["upm2_prepaid_value"]) and ':' not in str(dict_you1["upm2_mcc_debit_value"]) and ':'  not in str(dict_you1["upm2_mcc_credit_value"]) and ':' not in str(dict_you1["upm2_mcc_prepaid_value"]) and ':' not in str(dict_you1["upm2_bin_value"]) and ':'  not in str(dict_you1["upm2_rubro_debit_value"]) and ':'  not in str(dict_you1["upm2_rubro_credit_value"]) and ':' not in str(dict_you1["upm2_rubro_prepaid_value"]) and ':' not in str(dict_you1["upm2_region_debit_value"]) and ':'  not in str(dict_you1["upm2_region_credit_value"]) and ':' not in str(dict_you1["upm2_region_prepaid_value"]):result=True
                            else:raise ValueError
                        elif k['discount_type'] == '3' and k['card_type']== '1':
                            if ':'  in str(dict_you1["upm2_debit_value"]) and ':'  in str(dict_you1["upm2_credit_value"]) and ':' in str(dict_you1["upm2_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['mcc'] == '1' :
                            if ':'  in str(dict_you1["upm2_mcc_debit_value"]) and ':'  in str(dict_you1["upm2_mcc_credit_value"]) and ':' in str(dict_you1["upm2_mcc_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['bin'] == '1' :
                            if ':'  in str(dict_you1["upm2_bin_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['rubro'] == '1' :
                            if ':'  in str(dict_you1["upm2_rubro_debit_value"]) and ':'  in str(dict_you1["upm2_rubro_credit_value"]) and ':' in str(dict_you1["upm2_rubro_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['region'] == '1' :
                            if ':'  in str(dict_you1["upm2_region_debit_value"]) and ':'  in str(dict_you1["upm2_region_credit_value"]) and ':' in str(dict_you1["upm2_region_prepaid_value"]):result=True
                            else: raise AttributeError

                try:
                    DiscountAndPromotionValues.update(
                                                    channel=str(dict_you1["upm2_channel"]),
                                                    message_type=str(dict_you1["upm2_message_type"]),
                                                    processing_code=str(dict_you1["upm2_processing_code"]),
                                                    response_code=str(dict_you1["upm2_response_code"]),
                                                    debit_value=str(dict_you1["upm2_debit_value"]),
                                                    credit_value=str(dict_you1["upm2_credit_value"]),
                                                    prepaid_value=str(dict_you1["upm2_prepaid_value"]),
                                                    mcc=str(dict_you1["upm2_mcc"]),
                                                    mcc_debit_value=str(dict_you1["upm2_mcc_debit_value"]),
                                                    mcc_credit_value=str(dict_you1["upm2_mcc_credit_value"]),
                                                    mcc_prepaid_value=str(dict_you1["upm2_mcc_prepaid_value"]),
                                                    bin=str(dict_you1["upm2_bin"]),
                                                    bin_value=str(dict_you1["upm2_bin_value"]),
                                                    domestic_value=str(dict_you1["upm2_d_value"]),
                                                    international_value=str(dict_you1["upm2_i_value"]),
                                                    rubro=str(dict_you1["upm2_rubro"]),
                                                    rubro_debit_value=str(dict_you1["upm2_rubro_debit_value"]),
                                                    rubro_credit_value=str(dict_you1["upm2_rubro_credit_value"]),
                                                    rubro_prepaid_value=str(dict_you1["upm2_rubro_prepaid_value"]),
                                                    region=str(request.form.get("upm2_region",'')),
                                                    region_debit_value=str(dict_you1["upm2_region_debit_value"]),
                                                    region_credit_value=str(dict_you1["upm2_region_credit_value"]),
                                                    region_prepaid_value=str(dict_you1["upm2_region_prepaid_value"]),
                                                    ).where(
                                                        (DiscountAndPromotionValues.institution_id == str(dict_you1["upm2_institution_id"])) &
                                                        (DiscountAndPromotionValues.retailer_id == str(dict_you1["upm2_retailer_id"])) &
                                                        (DiscountAndPromotionValues.channel == str(dict_you1["upm2_channel_H"])) &
                                                        (DiscountAndPromotionValues.message_type == str(dict_you1["upm2_message_type_H"])) &
                                                        (DiscountAndPromotionValues.processing_code == str(dict_you1["upm2_processing_code_H"])) &
                                                        (DiscountAndPromotionValues.response_code == str(dict_you1["upm2_response_code_H"])) &
                                                        (DiscountAndPromotionValues.debit_value == str(dict_you1["upm2_debit_value_H"])) &
                                                        (DiscountAndPromotionValues.credit_value == str(dict_you1["upm2_credit_value_H"])) &
                                                        (DiscountAndPromotionValues.prepaid_value == str(dict_you1["upm2_prepaid_value_H"])) &
                                                        (DiscountAndPromotionValues.mcc == str(dict_you1["upm2_mcc_H"])) & 
                                                        (DiscountAndPromotionValues.mcc_debit_value == str(dict_you1["upm2_mcc_debit_value_H"])) &
                                                        (DiscountAndPromotionValues.mcc_credit_value == str(dict_you1["upm2_mcc_credit_value_H"])) &
                                                        (DiscountAndPromotionValues.mcc_prepaid_value == str(dict_you1["upm2_mcc_prepaid_value_H"])) &
                                                        (DiscountAndPromotionValues.bin == str(dict_you1["upm2_bin_H"])) &
                                                        (DiscountAndPromotionValues.bin_value == str(dict_you1["upm2_bin_value_H"])) &
                                                        (DiscountAndPromotionValues.domestic_value == str(dict_you1["upm2_d_value_H"])) &
                                                        (DiscountAndPromotionValues.international_value == str(dict_you1["upm2_i_value_H"])) &
                                                        (DiscountAndPromotionValues.rubro == str(dict_you1["upm2_rubro_H"])) & 
                                                        (DiscountAndPromotionValues.rubro_debit_value == str(dict_you1["upm2_rubro_debit_value_H"])) &
                                                        (DiscountAndPromotionValues.rubro_credit_value == str(dict_you1["upm2_rubro_credit_value_H"])) &
                                                        (DiscountAndPromotionValues.rubro_prepaid_value == str(dict_you1["upm2_rubro_prepaid_value_H"])) &
                                                        (DiscountAndPromotionValues.region_debit_value == str(dict_you1["upm2_region_debit_value_H"])) &
                                                        (DiscountAndPromotionValues.region_credit_value == str(dict_you1["upm2_region_credit_value_H"])) &
                                                        (DiscountAndPromotionValues.region_prepaid_value == str(dict_you1["upm2_region_prepaid_value_H"])) 
                                                    ).execute()
                    flash('Updated Sucessfully', 'success')

                except Exception as e:
                    flash('Error Update Unsucessfull:{}'.format(e), 'error')
            except AttributeError:
                flash('Error Update Unsucessfull', 'error')
                flash('Wrong Values for Entities, missing : ', 'error')
            except ValueError:
                flash('Wrong Values colon : Not allow in Percentage & Fixed type', 'error')
            return redirect(url_for('discount_and_promotions_type'))

        # CREATE BLOCK
        else:
            try:
                a = request.form.to_dict()
                dict_you3 = {key: a[key] for key in a.keys() if a[key] != ""}
                
                check_retailer_id = (DiscountAndPromotionRules.select().where((DiscountAndPromotionRules.institution_id == str(dict_you3["institution_id"])) & (DiscountAndPromotionRules.retailer_id == str(dict_you3["retailer_id"])) & (DiscountAndPromotionRules.channel == str(dict_you3["channel"]))).dicts().iterator())                                              
                data=[k for k in check_retailer_id]
                card_type_data=[ct['discount_type'] for ct in data]
                if((('1' in card_type_data) and ('3' in card_type_data)) or (('2' in card_type_data) and ('3' in card_type_data))):pass
                else:
                    for k in data:
                        if k['discount_type'] == '1' or k['discount_type'] == '2':
                            if ':' not in str(dict_you3["debit_value"]) and ':' not in str(dict_you3["credit_value"]) and ':' not in str(dict_you3["prepaid_value"]) and ':' not in str(dict_you3["mcc_debit_value"]) and ':' not in str(dict_you3["mcc_credit_value"]) and ':' not in str(dict_you3["mcc_prepaid_value"]) and ':' not in str(dict_you3["bin_value"]) and ':' not in str(dict_you3["rubro_debit_value"]) and ':' not in str(dict_you3["rubro_credit_value"]) and ':' not in str(dict_you3["rubro_prepaid_value"]) and ':' not in str(dict_you3["region_debit_value"]) and ':' not in str(dict_you3["region_credit_value"]) and ':' not in str(dict_you3["region_prepaid_value"]):result = True
                            else:raise ValueError
                        elif k['discount_type'] == '3' and k['card_type']== '1':
                            if ':'  in str(dict_you3["debit_value"]) and ':'  in str(dict_you3["credit_value"]) and ':' in str(dict_you3["prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['mcc'] == '1' :
                            if ':'  in str(dict_you3["mcc_debit_value"]) and ':'  in str(dict_you3["mcc_credit_value"]) and ':' in str(dict_you3["mcc_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['bin'] == '1' :
                            if ':'  in str(dict_you3["bin_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['rubro'] == '1' :
                            if ':'  in str(dict_you3["rubro_debit_value"]) and ':'  in str(dict_you3["rubro_credit_value"]) and ':' in str(dict_you3["rubro_prepaid_value"]):result=True
                            else: raise AttributeError
                        elif k['discount_type'] == '3' and k['region'] == '1' :
                            if ':'  in str(dict_you3["region_debit_value"]) and ':'  in str(dict_you3["region_credit_value"]) and ':' in str(dict_you3["region_prepaid_value"]):result=True
                            else: raise AttributeError
                try:
                    DiscountAndPromotionValues.create(
                                                    institution_id = str(dict_you3["institution_id"]),
                                                    retailer_id = str(dict_you3["retailer_id"]),
                                                    channel = str(dict_you3["channel"]),
                                                    message_type = str(dict_you3["message_type"]),
                                                    processing_code = str(dict_you3["processing_code"]) ,
                                                    response_code = str(dict_you3["response_code"]),
                                                    debit_value = str(dict_you3["debit_value"]),
                                                    credit_value = str(dict_you3["credit_value"]),
                                                    prepaid_value = str(dict_you3["prepaid_value"]),
                                                    mcc = str(dict_you3["mcc"]) ,
                                                    mcc_debit_value = str(dict_you3["mcc_debit_value"]) ,
                                                    mcc_credit_value = str(dict_you3["mcc_credit_value"]),
                                                    mcc_prepaid_value = str(dict_you3["mcc_prepaid_value"]) ,
                                                    bin = str(dict_you3["bin"]),
                                                    bin_value = str(dict_you3["bin_value"]),
                                                    domestic_value = str(dict_you3["domestic_value"]) ,
                                                    international_value = str(dict_you3["international_value"]),
                                                    rubro = str(dict_you3["rubro"]),
                                                    rubro_debit_value = str(dict_you3["rubro_debit_value"]),
                                                    rubro_credit_value = str(dict_you3["rubro_credit_value"]) ,
                                                    rubro_prepaid_value = str(dict_you3["rubro_prepaid_value"]),
                                                    region = str(request.form.get("region",'')),
                                                    region_debit_value = str(dict_you3["region_debit_value"]),
                                                    region_credit_value = str(dict_you3["region_credit_value"]) ,
                                                    region_prepaid_value = str(dict_you3["region_prepaid_value"]))
                    flash('Profile Created Sucessfully', 'success')

                except Exception as e:
                    flash('Error in Create Discount Profile:{}'.format(e), 'error')
            except AttributeError:
                flash('Wrong Values for Entities, missing : ', 'error')
            except ValueError:
                flash('Wrong Values colon : Not allow in Percentage & Fixed type', 'error')
            return redirect(url_for('discount_and_promotions_type'))

    return render_template('discount_and_promotions_type.html', discounts=discounts,IID=i_id, Pro_Code=pro_code, Ret_Com1=iid_rid, Msg_Type=msg_type, Res_Code=res_code, IR = iid_rid)


#################################### * Fetch Files Endpoints * ####################################

@app.get('/output_files/<path:path>')
@app.post('/output_files/<path:path>')
@login_required
def download(path):
    return send_from_directory('output_files/', path[2:-2], as_attachment=True)


@app.get('/output_ise/<path:path>')
@app.post('/output_ise/<path:path>')
@login_required
def ise_download(path):
    print(path)
    return send_from_directory('./CompensationReports/RetailerReports/', path[2:-2], as_attachment=True)


@app.get('/download_file/<path:file_path>')
@app.post('/download_file/<path:file_path>')
@login_required
def download_file(file_path):
    folder, filename = os.path.split(file_path)
    file_path = folder + filename
    # print(f"{filename} = {folder} = {file_path}")
    return send_from_directory(folder,filename, as_attachment=True)


@app.get("/search_geopagos_csv_download/<path:path>")
@login_required
def search_geopagos_csv_download(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_GPSMARTPOS_TransactionsDetails.csv'
    folder = f'CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
    fileName = folder+fname
    if(os.path.exists(fileName)):
        return send_from_directory(folder, fname, as_attachment=True)
    altFname = prefix+'_GPSMARTPOS_TransactionsDetailsR2.csv'
    return send_from_directory(folder, altFname, as_attachment=True)


@app.get("/geopagos_download_deposit/<path:path>")
@login_required
def search_geopagos_download_deposit(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_GPSMARTPOS_DepositDetails.csv'
    folder = f'CompensationReports/DepositRetailerReports/{months[int(month)-1]}_{year}/'
    fileName = folder+fname
    if(os.path.exists(fileName)):
        return send_from_directory(folder, fname, as_attachment=True)
    altFname = prefix+'_GPSMARTPOS_DepositDetailsR1.csv'
    return send_from_directory(folder, altFname, as_attachment=True)


@app.get('/geopagos_download/<path:path>')
@login_required
def geopagos_download(path):
    prefix = path.replace('-', '')
    year, month, day = prefix[:4], prefix[4:6], prefix[6:]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fname = prefix+'_DepositRetailerReports.zip'
    folder = 'CompensationReports/DepositRetailerReports/{}_{}/'.format(
        months[int(month)-1], year)
    return send_from_directory(folder, fname, as_attachment=True)


#################################### * Internal API * ####################################

@app.get('/_add_retailer')
@app.post('/_add_retailer')
@login_required
def _add_retailer():
    list_content = request.json
    # print(list_content)
    errors = []
    counter = 0
    for content in list_content:
        counter += 1
        try:
            validations_add_retailer(content)
            if(content["RetailerId"] == ""):
                errors.append(str(counter))
            else:
                RetailerId.create(**content)
        except Exception as e:
            errors.append(str(counter))
    if len(errors) == 0:
        return jsonify('Success in create all registers',errors)
    else:
        return jsonify('Error in create registers ', errors)


@app.get('/_add_retailer_account')
@app.post('/_add_retailer_account')
@login_required
def _add_retailer_account():
    list_content = request.json
    errors = []
    counter = 0
    for content in list_content:
        counter += 1
        try:
            validations_add_retailer_account(content)
            if(content["RetailerId"] == "" or content["TerminalId"] == "" or content["CardProductId"] == ""):
                errors.append(str(counter))
            else:
                RetailerAccount.create(**content)
        except Exception as e:
            errors.append(str(counter))
    if len(errors) == 0:
        return jsonify('Success in create all registers')
    else:
        return jsonify('Error in create registers ', errors)


@app.get('/_update_institution')
@app.post('/_update_institution')
@login_required
def _update_institution():
    list_content = request.json
    errors = []
    counter = 0
    for content_key in list_content:
        counter += 1
        content = {}
        for item_key in content_key.keys():
            if item_key not in ("institution_id_type_code", "institution_id_code"):
                content[item_key] = content_key[item_key]
        try:
            validations_update_institution(content)
            query = (InstitutionId.update(**content).where((InstitutionId.institution_id_type_code == str(content_key["institution_id_type_code"])) & (InstitutionId.institution_id_code == str(content_key["institution_id_code"]))))
            print(query.execute())
        except Exception as e:
            errors.append(str(counter))
    if len(errors) == 0:
        return jsonify('Success in update all registers')
    else:
        return jsonify('Error in update registers ', errors)


@app.get('/_update_retailer')
@app.post('/_update_retailer')
@login_required
def _update_retailer():
    list_content = request.json
    errors = []
    counter = 0
    for content_key in list_content:
        counter += 1
        content = {}
        for item_key in content_key.keys():
            if item_key not in ("RetailerId"):
                content[item_key] = content_key[item_key]
        try:
            validations_update_retailer(content)
            RetailerId.update(**content).where(RetailerId.RetailerId == content_key["RetailerId"] ).execute()
        except Exception as e:
            errors.append(str(counter))
    if len(errors) == 0:
        return jsonify('Success in update all registers')
    else:
        return jsonify('Error in update registers ', errors)


@app.get('/_update_retailer_account')
@app.post('/_update_retailer_account')
@login_required
def _update_retailer_account():
    list_content = request.json
    errors = []
    counter = 0
    for content_key in list_content:
        counter += 1
        content = {}
        for item_key in content_key.keys():
            if item_key not in ("RetailerId", "TerminalId", "CardProductId"):
                content[item_key] = content_key[item_key]
        try:
            validations_update_retailer_account(content)
            RetailerAccount.update(**content).where((RetailerAccount.RetailerId == content_key["RetailerId"]) & (RetailerAccount.TerminalId == content_key["TerminalId"]) & (RetailerAccount.CardProductId == content_key["CardProductId"]) ).execute()
        except Exception as e:
            errors.append(str(counter))
    if len(errors) == 0:
        return jsonify('Success in update all registers')
    else:
        return jsonify('Error in update registers ', errors)


# * Ankita [28 Dec 2022] :- Confusion for institution_modal.html
@app.get('/_get_instituion_id/')
@login_required
def _get_instituion_id():
    ins_type = request.args.get('type')
    if ins_type:
        data =  ConfigurationCatalogs.select().where(ConfigurationCatalogs.catalog_name == "InstitutionIdCode",ConfigurationCatalogs.related == ins_type).dicts()
        data = data.peek(data.__len__())
    return jsonify(data)


@app.get('/get_rc_ret_id')
@login_required
def get_rc_ret_id():
    search = request.args.get('Instituiton_ID')
    desc = []
    result = RetailerId.select(RetailerId.RetailerId).where(
        RetailerId.EntityId == str(search))  # .dicts()
    for r in result:
        desc.append(r.RetailerId)
    return jsonify(desc)


@app.get('/get_inst')
@login_required
def get_inst():
    search = request.args.get('fiid')
    desc = []
    result = InstitutionId.select(InstitutionId.institution_id_desc).where(InstitutionId.fiid == str(search))
    for r in result:
        desc.append([r.institution_id_desc])
    return jsonify(desc)


@app.get('/getterm')
@login_required
def getterm():
    search = request.args.get('retailer')
    terminal = []
    result = TerminalId.select(TerminalId.TerminalId).where(
        TerminalId.RetailerId == search)
    for r in result:
        terminal.append(r.TerminalId)
    return jsonify(terminal)

@app.get('/getrubro')
@login_required
def getrubro():
    retailer = request.args.get('retailer')
    inst_id = request.args.get('inst_id')
    print(retailer)
    terminal = []
    result = RetailerId.select(RetailerId.RubroCode).where(
        (RetailerId.RetailerId == retailer) & (RetailerId.EntityId == inst_id))
    for r in result:
        terminal.append(r.RubroCode)
    return jsonify(terminal)
    print(terminal)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4042, debug=True)
