#!/bin/bash

# * Author          :-  Sakib & Dishant
# * Created Date    :-  01/Mar/2021
# * Updated Date    :-  17/Oct/2022
# * Description     :-  Run Phase Two (Report Generation & History Insert/Update)
# * Usage           :-  sh phase_two.sh || ./phase_two.sh

CURRENT_DIR="/usr/src/app"
HOL_FILE_LIST="holidays"
TODAY=$(date "+%m%d")
DATE=${1:-${TODAY}}
DATE_TIME=$(date "+%d-%m-%Y %H:%M:%S")
environment_instance_name="ColDocker-QA"

# If it's sunday ...
#if [ "$(date +%u)" = "7" ]; then

# cd /home/compsan && source comp_env/bin/activate
cd ${CURRENT_DIR}

if [ ! -s $HOL_FILE_LIST ]; then
    echo "$0: Error: $HOL_FILE_LIST file not found!"
elif [ "$(grep "^$DATE" $HOL_FILE_LIST)" != "" ]; then
    echo "Scheduled job didn't start, It's holiday - $(date "+%d-%m-%Y %H:%M:%S")"
else
    python3 -W ignore base_liquidation.py CombineProcessingPhaseTwo > ./LogFiles/PhaseTwo_jobs.log 2>&1
    # python3 -W ignore cc30x24.py CCX24 > ./LogFiles/CCX24.log 2>&1
    # python3 -W ignore cc30x24.py trnxDetailReport > ./LogFiles/trnxDetailReport.log 2>&1
    # python3 -W ignore cc30x24.py ZIPFTP > ./LogFiles/ZIP_FTP.log 2>&1
    # echo "CCX24 / trnxDetailReport / ZIP&FTP Job Log" | mail -s "${environment_instance_name} CCX24 / trnxDetailReport / ZIP&FTP Job Log" -a ${CURRENT_DIR}/LogFiles/CCX24.log -a ${CURRENT_DIR}/LogFiles/trnxDetailReport.log -a ${CURRENT_DIR}/LogFiles/ZIP_FTP.log -c dishant@omnipayments.com -r ColDocker-QA@omnipayments.com ankita.harad@omnipayments.com
fi
