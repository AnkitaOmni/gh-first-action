#!/bin/bash

# * Author          :- Ankita
# * Created Date    :- 07/Oct/2022
# * Updated Date    :- 07/Oct/2022
# * Description     :- To Verify QAuction env cache, Input Location Files, Cronjob and QA UI 
# * Usage           :- sh QALookUp.sh || ./QALookUp.sh

cd /home/compsan && source comp_env/bin/activate
CURRENT_DIR="/home/omni_comp/QA"
cd ${CURRENT_DIR}

echo "================================================= *** Cronjob *** ================================================="; 
crontab -l 
echo ""; 
echo "*****************************************************************************************************************"; 
echo "================================================= *** Cache *** ================================================="; 
echo "*****************************************************************************************************************"; 
echo ""; 
echo ""; 
free -mh
echo ""; 
echo ""; 
echo "*****************************************************************************************************************"; 
echo "================================================= *** Input Files Location *** ================================================="; 
echo "*****************************************************************************************************************"; 
date; 
echo ""; 
tree ./AcquirerExtract/InputExtracts/; 
tree ./IssuerExtract/InputExtracts/; 
tree ./ApiLoaders/Retailer/InputFiles/; 
tree ./AcquirerExtractFullDay/InputExtracts/; 
tree ./RRNFiles/InputFiles/; 
tree ./MastercardIPM/InputIPM/;
echo "";
echo "*****************************************************************************************************************"; 
echo "================================================= *** QA UI *** ================================================="; 
echo "*****************************************************************************************************************"; 
lsof -i:4042
echo ""; 
echo "*****************************************************************************************************************"; 
echo "*****************************************************************************************************************"; 

echo "Please find cronjob, Cache, Input Location Files and QA UI status" | mail -s "QA Look Up" -a ${CURRENT_DIR}/LogFiles/QALookUp.log -c dishant@omnipayments.com -r ColDocker-QA@omnipayments.com ankita.harad@omnipayments.com
