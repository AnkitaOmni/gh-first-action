
# Standard Instuctions For All
Backup Files To Be Renamed = fileName.extension_DDMMMYYY (eg :- Filename.py_10Jan1997)
Backup Files To Be Moved To = BackUpFiles
Test Code To Be Written In = developerName.py (eg :- dishant.sh)

# Start / Stop Server
sh ./Scripts/stop.sh
sh ./Scripts/stop.sh

# Liquidation / Compensation Run Commands
** Retailer Job - Dump Retailers To Database
sh ./Scripts/retailer_loader.sh > ./LogFiles/loader_jobs.log 2>&1

** Phase 1 Job - File Upload + Validations + P1 Report Generation + Commission Calculations
python3 base_liquidation.py CombineProcessingPhaseOne today> ./LogFiles/PhaseOne_jobs.log 2>&1

** Phase 2 Job - Report Generation / CCX24 / ZIP_FTP
sh ./Scripts/phase_two.sh

# Check Port Status [ In Case Of Env Down ]
lsof -i:4042

# Check Status Log [ In Case Of Env Down ]
tail -n 50 gunicorn.log

# Docker Compose Commands
clear; docker-compose -f docker-compose-qa.yml up -d
clear; docker-compose -f docker-compose-qa.yml down
docker ps -a | grep "qa"

# Docker Commands
docker network ls; echo -e "\n\n" ;docker volume ls
clear; docker images | grep "adminer\|mysql"; echo -e "\n\n"; docker ps | grep qa

# CCX28 Loader Commands
1) python3 -W ignore retailer_com_extract_file.py commission > ./LogFiles/CCX28Loader_jobs.log 2>&1
2) python3 -W ignore retailer_com_extract_file.py alerts

# MySQL Config Change
# * Change 001 :
    SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
    https://stackoverflow.com/questions/41887460/select-list-is-not-in-group-by-clause-and-contains-nonaggregated-column-inc
