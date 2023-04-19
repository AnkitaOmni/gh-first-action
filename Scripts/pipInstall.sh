#!/bin/bash

# * Author          :- Dishant Raut
# * Created Date    :- 07/Jul/2022
# * Modified By     :- Dishant
# * Updated Date    :- 07/Jul/2022
# * Description     :- Install Python Modules
# * Usage           :- sh pipInstall.sh || ./pipInstall.sh
# * Permissions     :- 744
# * Job             :- Not Decided/Required

ENV="QA"
USR="compsan"
USRPATH="/home/$USR"
ENVPATH="$USRPATH/$ENV"
ACTIVATE="comp_env/bin/activate"

set -e

echo -e "\n#################################### Job has started at $(date "+%d-%m-%Y %H:%M:%S") ####################################\n"
echo "ENV = $ENV"
echo "USR = $USR"
echo "USRPATH = $USRPATH"
echo "ENVPATH = $ENVPATH"
echo "VE Activate = source $USRPATH/$ACTIVATE"
source $USRPATH/$ACTIVATE
echo -e "\nInside VE .....\n"
echo -e "\nStarting Upgrade .....\n"
python3 -m pip install -U pip setuptools wheel
pip install --upgrade -r req.txt
echo -e "\nListing All Packages .....\n"
pip list
echo -e "\nRemoving All Cache .....\n"
pip cache purge
echo -e "\n#################################### Finished job processing at $(date "+%d-%m-%Y %H:%M:%S") ####################################\n"
