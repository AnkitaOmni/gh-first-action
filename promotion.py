from peewee import operator
from functools import reduce
from typing import Dict, List, Tuple
from model import DiscountAndPromotionRules, DiscountAndPromotionValues, RetailerId


promotionQuery =  [com for com in DiscountAndPromotionRules.select().group_by(DiscountAndPromotionRules.institution_id,DiscountAndPromotionRules.retailer_id,DiscountAndPromotionRules.channel,DiscountAndPromotionRules.priority).dicts()]
promotion = {}
for pro in promotionQuery:
    if pro['institution_id'] + '-' + pro['retailer_id'] + '-' + pro['channel'] in promotion:
        promotion[pro['institution_id'] + '-' + pro['retailer_id'] + '-' + pro['channel']].append(pro) 
    else:               
        promotion[pro['institution_id'] + '-' + pro['retailer_id'] + '-' + pro['channel']] = [pro]


def calculation_formula(trnxAmt: str = "0", commValue: str = "0", choice: str = "0-0") -> float:
    """
    Summary:

        Formula Used For Calculation

        # * Fixed
        1-1 = Fixed - Plain
        1-2 = Fixed - Amount
        1-3 = Fixed - Count
        1-4 = Fixed - Total Count
        # * Percentage
        2-1 = Percentage - Plain
        2-2 = Percentage - Amount
        2-3 = Percentage - Count
        2-4 = Percentage - Total Count
        
        # * Both 
        # * For Both ComValue will be Fixed:Percentage(100:5%) 
        3-1 = Both - Plain 
        3-2 = Percentage - Amount
        3-3 = Percentage - Count
        3-4 = Percentage - Total Count

    Args:
        trnxAmt (str, optional): Transaction Amount. Defaults to "0".
        commValue (str, optional): Commission Value. Defaults to "0".
        choice (str, optional): Commission Choice. Defaults to "0-0".

    Returns:
        float: Calculation result
    """
    splitVal = [ i or '0' for i in commValue.split(':')]
    try:
        commValue1,commValue2 = splitVal
    except ValueError:
        commValue1,commValue2 = splitVal[0],0 
        
    #print(f' CommValur1 : {commValue1} , commValue2 : {commValue2}')
    
    if choice == "1-1": return 1 * float(commValue1) 
    if choice == "2-1": return (float(trnxAmt) * float(commValue1))  / 100
    if choice == "3-1": return ( 1 * float(commValue1)) + ((float(trnxAmt) * float(commValue2))/ 100) 
    return 0.0

def liquidation(singleTrnxDetail: Dict, activeRules: List, configValues: Dict, formula: str = "0-0") -> Tuple[str, str, str, str, str]:
    """
    Liquidation:
        process of bringing a business to an end and distributing its assets to claimants
        we distribute the amount based on commission / discount / promotions using specifed formula and multiple checks
    
    Args:
        singleTrnxDetail (Dict): Data from single transaction
        activeRules (List): All active flags
        configValues (Dict): All configure values 
        formula (str, optional): Type of formula to be used. Defaults to "0-0".

    Returns:
        Tuple[str, str, str, str, str]: CardCommission, BinCommission, MccCommission, TrnxIdentifierCommission, RubroCommission
    """    

    CardCommission, BinCommission, MccCommission, TrnxIdentifierCommission, RubroCommission, RegionCommission = 0, 0, 0, 0, 0, 0
    
    ### * All Card Based Commissions
    if singleTrnxDetail["card_type"].strip() == "C":
        # print("Credit Card Trnx") # * Credit Card
        if "card_type" in activeRules: CardCommission = calculation_formula(singleTrnxDetail['amount'], configValues['credit_value'], formula)
        if "mcc" in activeRules: MccCommission = calculation_formula(singleTrnxDetail['amount'], configValues['mcc_credit_value'], formula)
        if "rubro" in activeRules: RubroCommission = calculation_formula(singleTrnxDetail['amount'], configValues['rubro_credit_value'], formula)
        if "region" in activeRules: RegionCommission = calculation_formula(singleTrnxDetail['amount'], configValues['region_credit_value'], formula)

    elif singleTrnxDetail["card_type"].strip() == "D":
        # print("Debit Card Trnx") # * Debit Card
        if "card_type" in activeRules: CardCommission = calculation_formula(singleTrnxDetail['amount'], configValues['debit_value'], formula)
        if "mcc" in activeRules: MccCommission = calculation_formula(singleTrnxDetail['amount'], configValues['mcc_debit_value'], formula)
        if "rubro" in activeRules: RubroCommission = calculation_formula(singleTrnxDetail['amount'], configValues['rubro_debit_value'], formula)
        if "region" in activeRules: RegionCommission = calculation_formula(singleTrnxDetail['amount'], configValues['region_debit_value'], formula)
        
    elif singleTrnxDetail["card_type"].strip() == "P":
        # print("Prepaid Card Trnx") # * Prepaid Card
        if "card_type" in activeRules: CardCommission = calculation_formula(singleTrnxDetail['amount'], configValues['prepaid_value'], formula)
        if "mcc" in activeRules: MccCommission = calculation_formula(singleTrnxDetail['amount'], configValues['mcc_prepaid_value'], formula)
        if "rubro" in activeRules: RubroCommission = calculation_formula(singleTrnxDetail['amount'], configValues['rubro_prepaid_value'], formula)
        if "region" in activeRules: RegionCommission = calculation_formula(singleTrnxDetail['amount'], configValues['region_prepaid_value'], formula)
        
    ### * Independent Commissions
    if "bin" in activeRules: BinCommission = calculation_formula(singleTrnxDetail['amount'], configValues['bin_value'], formula)

    if "transaction_identifier" in activeRules: # * International / Domestic
        if singleTrnxDetail["transaction_identifier"].strip() == "D":
            TrnxIdentifierCommission = calculation_formula(singleTrnxDetail['amount'], configValues['domestic_value'], formula)
        elif singleTrnxDetail["transaction_identifier"].strip() == "I":
            TrnxIdentifierCommission = calculation_formula(singleTrnxDetail['amount'], configValues['international_value'], formula)

    # print(f"# All Card Type Based Commissions : ")
    # print(f"TrnxAmount = {float(singleTrnxDetail['amount'])} | CardCommissions = {CardCommission} | ", end="")
    # print(f"MccCommissions = {MccCommission} | RubroCommissions = {RubroCommission}")
    # print(f"# All Independent Commissions : ")
    # print(f"BinCommissions = {BinCommission} | TrnxIdentifierCommission = {TrnxIdentifierCommission}")
    # print(f"\n************** END Single Trnx Calculation **************\n\n")
    # print("\n", "#"*80, "Dishant END\n")
    del singleTrnxDetail, activeRules, configValues
    return CardCommission, BinCommission, MccCommission, TrnxIdentifierCommission, RubroCommission,RegionCommission



def get_discount(caseList,**singleTrnxDetail) -> Dict:
    """
    Summary:
        Perform all calculations here
        All data of single transaction is received here
        # https://stackoverflow.com/questions/38757543/peewee-simple-where-condition-that-is-always-true

        discount rule = 1 (Fixed) | 2 (Percentage)
        discount value = 1 (Plain) | 2 (Amount) | 3 (Count) | 4 (Total Count)

    Returns:
        Dict: All possible calculated commission
    """    

    # print("\n", "#"*80, "Dishant START\n\n")
    # print(f"singleTrnxDetail = {singleTrnxDetail}")


    ruleOptions = ["card_type", "transaction_type", "transaction_identifier", "mcc", "bin", "rubro", "region", "status"]
    flag = False
    comValue = 0, 0, 0, 0, 0, 0
    ###################### * Fetch DiscountAndPromotion Rules * ######################


    for priority in range(1,6): 
        
        filterTxnList = [txn for key,val in promotion.items() if key in caseList for txn in val if txn['priority'] == str(priority)  ]
        sortedTxnLst = sorted(filterTxnList,key=lambda x:caseList.index(x['institution_id'] + '-' + x['retailer_id'] + '-' + x['channel']))
        #print(f'Case Availabler for Discount Priorirty {priority} {sortedTxnLst}')
        for txn in filterTxnList:
            for k, j in txn.copy().items():
                if (k.strip() in ruleOptions) and str(j).strip() == "0":
                    # print(f"False | {k} = {j}")
                    del txn[k]

            # * All Active Flags / DiscountAndPromotionRules To Use During Commission Application
            activeRules = [k for k in txn if k in ruleOptions]
            conditions = [] # * All Conditions
    
            ###################### * Compulsory Conditions * ######################

            conditions.append(DiscountAndPromotionValues.institution_id == txn["institution_id"])
            conditions.append(DiscountAndPromotionValues.retailer_id == txn["retailer_id"])
            conditions.append(DiscountAndPromotionValues.channel == txn["channel"])
            conditions.append(DiscountAndPromotionValues.message_type == singleTrnxDetail["message_type"])
            conditions.append(DiscountAndPromotionValues.processing_code == singleTrnxDetail["processing_code"][:2])
            conditions.append(DiscountAndPromotionValues.response_code == singleTrnxDetail["response_code"])
            
            ###################### * Optional Conditions * ######################

            if "mcc" in activeRules: conditions.append(DiscountAndPromotionValues.mcc == singleTrnxDetail["mcc"])
            
            if "bin" in activeRules: conditions.append(DiscountAndPromotionValues.bin == singleTrnxDetail["bin"])
            
            # Added by {Dishant & Vishal) [19 Jan 2023] - bin lenghth match
            """if "bin" in activeRules:
                try:
                    queryConfigBinCode = ((DiscountAndPromotionValues.select(DiscountAndPromotionValues.bin).where(
                        (DiscountAndPromotionValues.institution_id == txn["institution_id"]) &
                        (DiscountAndPromotionValues.retailer_id == txn["retailer_id"]) &
                        (DiscountAndPromotionValues.channel == txn["channel"])
                    )).dicts().iterator())

                    configBinCode = [k for k in queryConfigBinCode][0]['bin'].strip()
                    lengthToMatch = len(configBinCode)
                    trnxBin = singleTrnxDetail['bin'][:lengthToMatch].strip()

                    # print(f"configBinCode = {configBinCode} | trnxBin = {trnxBin}")
                    if configBinCode == trnxBin: conditions.append(DiscountAndPromotionValues.bin == trnxBin)
                    else: activeRules.remove("bin")
                
                except IndexError: activeRules.remove("bin")
            """
            
            if "rubro" in activeRules:
                if txn["institution_id"] != "DEFAULT" or txn["retailer_id"] != "DEFAULT":
                    rubroQuery = (RetailerId
                                .select(RetailerId.RubroCode)
                                .where(
                                    (RetailerId.EntityId == txn["institution_id"]) &
                                    (RetailerId.RetailerId == txn["retailer_id"]) &
                                    (RetailerId.StatusCode == True)
                                ).dicts().iterator())

                    try:
                        queryConfigRubroCode = ((DiscountAndPromotionValues.select(DiscountAndPromotionValues.rubro).where(
                            (DiscountAndPromotionValues.institution_id == txn["institution_id"]) &
                            (DiscountAndPromotionValues.retailer_id == txn["retailer_id"]) &
                            (DiscountAndPromotionValues.channel == txn["channel"])
                        )).dicts().iterator())
                        configRubroCode = [k for k in queryConfigRubroCode][0]['rubro']
                        rubCode = [k for k in rubroQuery][0]["RubroCode"]
                        #print(f"rubCode = {rubCode} | configRubroCode = {configRubroCode}")
                        if rubCode == configRubroCode:
                            conditions.append(DiscountAndPromotionValues.rubro == rubCode)
                        else:
                            activeRules.remove("rubro")
                    except IndexError:
                        pass
            
            if "region" in activeRules:
                if txn["institution_id"] != "DEFAULT" or txn["retailer_id"] != "DEFAULT":
                    regionQuery = (RetailerId
                                .select(RetailerId.AcquirerRegionCode)
                                .where(
                                    (RetailerId.EntityId == txn["institution_id"]) &
                                    (RetailerId.RetailerId == txn["retailer_id"]) &
                                    (RetailerId.StatusCode == True)
                                ).dicts().iterator())

                    try:
                        queryConfigRegionCode = ((DiscountAndPromotionValues.select(DiscountAndPromotionValues.region).where(
                            (DiscountAndPromotionValues.institution_id == txn["institution_id"]) &
                            (DiscountAndPromotionValues.retailer_id == txn["retailer_id"]) &
                            (DiscountAndPromotionValues.channel == txn["channel"])
                        )).dicts().iterator())
                        configRegionCode = [k for k in queryConfigRegionCode][0]['region']
                        regCode = [k for k in regionQuery][0]["AcquirerRegionCode"]
                        #print(f"regCode = {regCode} | configRegionCode = {configRegionCode}")
                        if regCode == configRegionCode:
                            conditions.append(DiscountAndPromotionValues.region == regCode)
                        else:
                            activeRules.remove("region")
                    except IndexError:pass

            # * Make ORM Query With All Found/Default Constrains
            getConfigQuery = (DiscountAndPromotionValues.select()
                            .where(reduce(operator.and_, conditions))
                            .dicts())

            ###################### * Start Calculations * ######################
            
            queryOutput = [k for k in getConfigQuery.iterator()]
            # * Raw SQL Query
            rawSql = getConfigQuery.sql()
            # print(f"\nchecks = \n{checks}")
            # print(f"\nactiveRules = {activeRules}")
            # print(f"\nrawSql = {rawSql}")
            # print(f"\nqueryOutput = {queryOutput}")

            if len(queryOutput) > 0:
                #print(f"Case Discount : [ {txn['institution_id']} | {txn['retailer_id']} | {txn['channel']} | {txn['priority']} ] = Success")
                configValues = queryOutput[0]
                del getConfigQuery, queryOutput
                # print(f"\nconfigValues = \n{configValues}")
                comValue = liquidation(singleTrnxDetail, activeRules, configValues, f"{txn['discount_type'].strip()}-{txn['discount_sub_type'].strip()}")
                flag = True
                break 
        if flag:
            break
    return comValue

    ###################### * End Calculations * ######################



if __name__ == '__main__':
    pass
