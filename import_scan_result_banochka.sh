#!/bin/bash

FILE=$1
DATA=$(date '+%Y-%m-%d')
URL_API="https://defectdojo/api/v2/import-scan/"
Red='\033[0;31m'
Green='\033[0;32m'
TOKEN="Token $2"

echo -e "${Green}
===============================================
The SAST report is sent to the DefectDojo...
==============================================="

REQUEST=$(curl --max-time 3600 --write-out '%{http_code}\n' --silent --output /dev/null -k -X 'POST' "$URL_API" \
  -H 'accept: application/json' \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: multipart/form-data' \
  -F 'product_type_name=Prom' \
  -F 'active=true' \
  -F 'endpoint_to_add=' \
  -F 'verified=true' \
  -F 'close_old_findings=true' \
  -F 'test_title=SomeProject' \
  -F 'engagement_name=' \
  -F 'build_id=' \
  -F 'push_to_jira=false' \
  -F 'minimum_severity=Info' \
  -F 'scan_date='$DATA \
  -F 'environment=ProdEnv' \
  -F 'service=true' \
  -F 'commit_hash=' \
  -F 'group_by=' \
  -F 'version=' \
  -F 'tags=searchService' \
  -F 'api_scan_configuration=' \
  -F 'product_name= PromWeb' \
  -F 'file=@'$FILE \
  -F 'auto_create_context=' \
  -F 'lead=' \
  -F 'scan_type=GitLab SAST Report' \
  -F 'branch_tag=' \
  -F 'engagement=01')

if [[ "$REQUEST" == 200 || "$REQUEST" == 201 ]] ; then
  echo -e "${Green}
===============================================
SUCCEEDED
==============================================="
else
  echo -e "${Red}
========================================================
SAST report not sent to DefectDojo due to $REQUEST error
========================================================"
  exit 1
fi

