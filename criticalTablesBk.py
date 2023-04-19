from glob import glob
from datetime import datetime
from peewee import MySQLDatabase, chunked
from playhouse.pool import PooledMySQLDatabase
from sendmail_alerts import sendmail_with_html_and_attachment
from model import (ConfigurationCatalogs, InstitutionId, RetailerAccount, RetailerCommissions, RetailerCommissionsOnOff, 
RetailerId, Users, EnableValidations, myDB)



# * Temporay Prod Connection
try:
    ENV = 'PROD'
    prodDbCon = PooledMySQLDatabase(
        host="localhost",
        port=3306,
        database="OMNICOMP_BECH_"+ENV,
        user="root",
        passwd="Omni123*",
        max_connections=30,
        stale_timeout=300  # 5 minutes.
        )
    print("#"*70)
    print("* Prod Peewee Db Connection Successful")
    print(f"* Critical Table BackUp Started : {datetime.now()}")
    print("#"*70, "\n\n\n")
except Exception as err:
    print(f"Error: '{err}'")
    del err


try:
    # * ConfigurationCatalogs
    ConfigurationCatalogs.truncate_table()
    colName = [k for k in ConfigurationCatalogs._meta.fields.keys()]
    colName.remove('id')
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM configurationcatalogs; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM configurationcatalogs LIMIT 5; """
    prodCCData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodCCData, 1000):
            ConfigurationCatalogs.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodCCData = {prodCCData}")
    print(f"\n{query1}\n")
    print('#1', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodCCData


    # * InstitutionId
    InstitutionId.truncate_table()
    colName = [k for k in InstitutionId._meta.fields.keys()]
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM institutionid; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM institutionid LIMIT 5; """
    prodIIData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodIIData, 1000):
            InstitutionId.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodIIData = {prodIIData}")
    print(f"\n{query1}\n")
    print('#2', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodIIData


    # * RetailerAccount
    RetailerAccount.truncate_table()
    colName = [k for k in RetailerAccount._meta.fields.keys()]
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retaileraccount; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retaileraccount LIMIT 5; """
    prodRAData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodRAData, 1000):
            RetailerAccount.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodRAData = {prodRAData}")
    print(f"\n{query1}\n")
    print('#3', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodRAData


    # * RetailerCommissions
    RetailerCommissions.truncate_table()
    colName = [k for k in RetailerCommissions._meta.fields.keys()]
    colName.remove('id')
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailercommissions; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailercommissions LIMIT 5; """
    prodRCData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodRCData, 1000):
            RetailerCommissions.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodRCData = {prodRCData}")
    print(f"\n{query1}\n")
    print('#4', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodRCData


    # * RetailerCommissionsOnOff
    RetailerCommissionsOnOff.truncate_table()
    colName = [k for k in RetailerCommissionsOnOff._meta.fields.keys()]
    colName.remove('id')
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailercommissionsonoff; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailercommissionsonoff LIMIT 5; """
    prodRCOData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodRCOData, 1000):
            RetailerCommissionsOnOff.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodRCOData = {prodRCOData}")
    print(f"\n{query1}\n")
    print('#5', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodRCOData


    # * RetailerId
    RetailerId.truncate_table()
    colName = [k for k in RetailerId._meta.fields.keys()]
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailerid; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM retailerid LIMIT 5; """
    prodRIData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodRIData, 10000):
            RetailerId.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodRIData = {prodRIData}")
    print(f"\n{query1}\n")
    print('#6', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodRIData


    # * Users
    Users.truncate_table()
    colName = [k for k in Users._meta.fields.keys()]
    colName.remove('id')
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM users; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM users LIMIT 5; """
    prodUData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodUData, 1000):
            Users.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodUData = {prodUData}")
    print(f"\n{query1}\n")
    print('#7', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodUData


    # * EnableValidations
    EnableValidations.truncate_table()
    colName = [k for k in EnableValidations._meta.fields.keys()]
    colName.remove('id')
    query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM enablevalidations; """
    # query1 = f""" SELECT {str(colName).replace("'", "").replace("[", "").replace("]", "")} FROM enablevalidations LIMIT 5; """
    prodEVData = [k for k in prodDbCon.execute_sql(f'{query1}').fetchall()]
    with myDB.atomic():
        for batch in chunked(prodEVData, 1000):
            EnableValidations.insert_many(batch, fields=colName).execute()
    # print(f"# colName = {colName}\n")
    # print(f"# prodEVData = {prodEVData}")
    print(f"\n{query1}\n")
    print('#8', query1.split('FROM')[1].split(' ')[1].replace(";", ""), " :- Data Load Done\n\n\n")
    del colName, query1, prodEVData

    html_content = "<H3><p>Backup Of Critical Tables From Prod has been done successfully.</p></H3>"
    subject = f"Compensation Backup Of Critical Tables From Prod Done At  {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}"
    sendmail_with_html_and_attachment(html_content, subject, glob(f"./LogFiles/Prod_CriTablBkp.log*"))
    print(f"Backup Of Critical Tables From Prod Done & Mail Sent at {datetime.today().strftime(r'%Y-%m-%d %H:%M:%S')}")


except Exception as e:
    print("Error In Taking Backup Of Critical Tables From Prod", e)


# * Delete Prod Db Connection At End
del prodDbCon, myDB
