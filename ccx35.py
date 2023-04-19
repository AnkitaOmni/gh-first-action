from datetime import datetime
from database import DatabaseConnections
from queries import CCX35_query1, CCX35_query2
from model import ChileIdpUpdate, EstadoIdpUpdate, FullDayTransactionHistory, FullDayTransactionRetailerHistory



# * Fetch DB Connection
db_instance = DatabaseConnections()
db_con = db_instance.peewee_connection()



def chileIdpCCX35Processing():

    retailereWithMulitpleRows = [k for k in db_con.execute_sql(CCX35_query2)]
    if len(retailereWithMulitpleRows) > 0:
        for ret_ins in retailereWithMulitpleRows:
            print(f"InsId = {ret_ins[1]} | RetId = {ret_ins[0]} | Cnt = {ret_ins[2]}")

            queryCIU = (ChileIdpUpdate.select()
                        .where(
                (ChileIdpUpdate.RetId == ret_ins[0]) &
                (ChileIdpUpdate.InsId == ret_ins[1])
            ).dicts())

            idp, finalAmt = [], []
            queryCIUOutput = [k for k in queryCIU]
            for eachRow in queryCIUOutput:
                del eachRow['id']
                idp.append(eachRow["DocNum"])
                finalAmt.append(int(eachRow['FinalAmt']))
                # print(eachRow)

            # * Fetch Greater/Old IDP + Sum(FinalAmount)
            multiIdpSet = list(set([int(k.split("NAN")[0].replace("IDP", "").strip()) for k in idp]))
            if len(multiIdpSet) == 1:
                num = int(idp[0].split("NAN")[0].replace("IDP", "")) + (int(ret_ins[2]) - 1)
                updatedSingleIDP = "IDP" + str(num).rjust(3, "0") + "NAN" + idp[0].split("NAN")[1]
                print(f"IDP = {updatedSingleIDP} | FinalAmt = {sum(finalAmt)}")
                # print(queryCIUOutput[0])

                # * Update : FullDayTransactionHistory
                (FullDayTransactionHistory.update(IDP=updatedSingleIDP)
                .where(FullDayTransactionHistory.IDP.in_(idp))
                .execute())

                # * Delete : ChileIdpUpdate + FullDayTransactionRetailerHistory
                (FullDayTransactionRetailerHistory.delete()
                .where(FullDayTransactionRetailerHistory.IDP.in_(idp))
                .execute())
                (ChileIdpUpdate.delete()
                .where(ChileIdpUpdate.DocNum.in_(idp))
                .execute())

                # * Create : ChileIdpUpdate + FullDayTransactionRetailerHistory
                queryCIUOutput[0]["DocNum"] = updatedSingleIDP
                queryCIUOutput[0]["FinalAmt"] = sum(finalAmt)
                (ChileIdpUpdate.create(**queryCIUOutput[0]))
                del queryCIUOutput[0]["DocNum"]
                queryCIUOutput[0]["IDP"] = updatedSingleIDP
                (FullDayTransactionRetailerHistory.create(**queryCIUOutput[0]))

            else:
                multiIdp = [k.strip() for k in idp]
                multiIdp.sort(reverse=True)
                num = int(multiIdp[0].split("NAN")[0].replace("IDP", "")) + (int(ret_ins[2]) - 1)
                updatedMultipleIDP = "IDP" + str(num).rjust(3, "0") + "NAN" + multiIdp[0].split("NAN")[1]
                print(f"IDP = {updatedMultipleIDP} | FinalAmt = {sum(finalAmt)}")
                # print(queryCIUOutput[0])

                # * Update : FullDayTransactionHistory
                (FullDayTransactionHistory.update(IDP=updatedMultipleIDP)
                .where(FullDayTransactionHistory.IDP.in_(idp))
                .execute())

                # * Delete : ChileIdpUpdate + FullDayTransactionRetailerHistory
                (FullDayTransactionRetailerHistory.delete()
                .where(FullDayTransactionRetailerHistory.IDP.in_(idp))
                .execute())
                (ChileIdpUpdate.delete()
                .where(ChileIdpUpdate.IDP.in_(idp))
                .execute())

                # * Create : ChileIdpUpdate + FullDayTransactionRetailerHistory
                queryCIUOutput[0]["DocNum"] = updatedMultipleIDP
                queryCIUOutput[0]["FinalAmt"] = sum(finalAmt)
                (ChileIdpUpdate.create(**queryCIUOutput[0]))
                del queryCIUOutput[0]["DocNum"]
                queryCIUOutput[0]["IDP"] = updatedSingleIDP
                (FullDayTransactionRetailerHistory.create(**queryCIUOutput[0]))
            print()
    print(f"CCX35 Chile Processing Success At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")



def estadoIdpCCX35Processing():

    retailereWithMulitpleRows = [k for k in db_con.execute_sql(CCX35_query1)]
    if len(retailereWithMulitpleRows) > 0:
        for ret_ins in retailereWithMulitpleRows:
            print(
                f"InsId = {ret_ins[1]} | RetId = {ret_ins[0]} | Cnt = {ret_ins[2]}")

            queryEIU = (EstadoIdpUpdate.select()
                        .where(
                (EstadoIdpUpdate.RetId == ret_ins[0]) &
                (EstadoIdpUpdate.InsId == ret_ins[1])
            ).dicts())

            idp, finalAmt = [], []
            queryEIUOutput = [k for k in queryEIU]
            for eachRow in queryEIUOutput:
                del eachRow['id']
                idp.append(eachRow['IDP'])
                finalAmt.append(int(eachRow['FinalAmt']))
                # print(eachRow)

            # * Fetch Greater/Old IDP + Sum(FinalAmount)
            multiIdpSet = list(set([int(k.split("NAN")[0].replace("IDP", "").strip()) for k in idp]))
            if len(multiIdpSet) == 1:
                num = int(idp[0].split("NAN")[0].replace("IDP", "")) + (int(ret_ins[2]) - 1)
                updatedSingleIDP = "IDP" + str(num).rjust(3, "0") + "NAN" + idp[0].split("NAN")[1]
                print(f"IDP = {updatedSingleIDP} | FinalAmt = {sum(finalAmt)}")
                # print(queryEIUOutput[0])

                # * Update : FullDayTransactionHistory
                (FullDayTransactionHistory.update(IDP=updatedSingleIDP)
                .where(FullDayTransactionHistory.IDP.in_(idp))
                .execute())

                # * Delete : EstadoIdpUpdate + FullDayTransactionRetailerHistory
                (FullDayTransactionRetailerHistory.delete()
                .where(FullDayTransactionRetailerHistory.IDP.in_(idp))
                .execute())
                (EstadoIdpUpdate.delete()
                .where(EstadoIdpUpdate.IDP.in_(idp))
                .execute())

                # * Create : EstadoIdpUpdate + FullDayTransactionRetailerHistory
                queryEIUOutput[0]["IDP"] = updatedSingleIDP
                queryEIUOutput[0]["FinalAmt"] = sum(finalAmt)
                (EstadoIdpUpdate.create(**queryEIUOutput[0]))
                (FullDayTransactionRetailerHistory.create(**queryEIUOutput[0]))

            else:
                multiIdp = [k.strip() for k in idp]
                multiIdp.sort(reverse=True)
                num = int(multiIdp[0].split("NAN")[0].replace("IDP", "")) + (int(ret_ins[2]) - 1)
                updatedMultipleIDP = "IDP" + str(num).rjust(3, "0") + "NAN" + multiIdp[0].split("NAN")[1]
                print(f"IDP = {updatedMultipleIDP} | FinalAmt = {sum(finalAmt)}")
                # print(queryEIUOutput[0])

                # * Update : FullDayTransactionHistory
                (FullDayTransactionHistory.update(IDP=updatedMultipleIDP)
                .where(FullDayTransactionHistory.IDP.in_(idp))
                .execute())

                # * Delete : EstadoIdpUpdate + FullDayTransactionRetailerHistory
                (FullDayTransactionRetailerHistory.delete()
                .where(FullDayTransactionRetailerHistory.IDP.in_(idp))
                .execute())
                (EstadoIdpUpdate.delete()
                .where(EstadoIdpUpdate.IDP.in_(idp))
                .execute())

                # * Create : EstadoIdpUpdate + FullDayTransactionRetailerHistory
                queryEIUOutput[0]["IDP"] = updatedMultipleIDP
                queryEIUOutput[0]["FinalAmt"] = sum(finalAmt)
                (EstadoIdpUpdate.create(**queryEIUOutput[0]))
                (FullDayTransactionRetailerHistory.create(**queryEIUOutput[0]))
            print()
    print(f"CCX35 Estado Processing Success At {datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')}")




if '__main__' == __name__:
    chileIdpCCX35Processing()
    # estadoIdpCCX35Processing()

