#!/bin/bash

# * Author          :- Sakib & Dishant
# * Created Date    :- 30/Nov/2021
# * Updated Date    :- 30/Nov/2021
# * Description     :- Upload Retailer Load To DB
# * Usage           :- sh retailer_loader.sh || ./retailer_loader.sh

set -e

CURRENT_DIR="/usr/src/app"

python3 -W ignore retailer_loader.py RetailerLoader ${CURRENT_DIR} > ./LogFiles/loader_jobs.log 2>&1
echo "Retailer load finished at $(date "+%d-%m-%Y %H:%M:%S")"
python3 -W ignore retailer_loader.py Alert ${CURRENT_DIR}