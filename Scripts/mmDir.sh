#!/bin/bash

# * Author          :- Dishant & Ankita
# * Created Date    :- 20/Sep/2022
# * Updated Date    :- 29/Sep/2022
# * Description     :- Upload Retailer Load To DB
# * Usage           :- sh mmDir.sh || ./mmDir.sh

CURRENT_DIR="/home/omni_comp/QA"
environment_instance_name="ColDocker-QA"
cd ${CURRENT_DIR}

mkdir -vp ./CompensationReports/AdjustmentReports/$(date +"%b_%Y")
mkdir -vp ./CompensationReports/ConciliationReports/$(date +"%b_%Y")
mkdir -vp ./CompensationReports/RetailerReports/$(date +"%b_%Y")
mkdir -vp ./CompensationReports/ZipRetailerReports/$(date +"%Y")/$(date +"%b_%Y")
mkdir -vp ./AcquirerExtract/ProcessedExtracts/$(date +"%b_%Y")
mkdir -vp ./IssuerExtract/ProcessedExtracts/$(date +"%b_%Y")
mkdir -vp ./AcquirerExtractFullDay/ProcessedExtracts/$(date +"%b_%Y")
mkdir -vp ./RRNFiles/OutputExtracts/$(date +"%b_%Y")
mkdir -vp ./RRNFiles/ProcessedFiles/$(date +"%b_%Y")
mkdir -vp ./MastercardIPM/OutputCSV/$(date +"%b_%Y")
mkdir -vp ./MastercardIPM/ProcessedInputIPM/$(date +"%b_%Y")

echo "Directories are created for $(date +"%B %Y") on the ${environment_instance_name} environment . " | mail -s "mmDir Job Run on ${environment_instance_name}" -a ${CURRENT_DIR}/LogFiles/mmDir.log -c dishant@omnipayments.com -r ColDocker-QA@omnipayments.com ankita.harad@omnipayments.com
