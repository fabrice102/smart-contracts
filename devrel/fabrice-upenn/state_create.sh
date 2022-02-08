#!/bin/bash

set -eu -o pipefail

$SB copyTo state.teal
$SB copyTo clear.teal

GOAL="$SB goal"
$GOAL clerk compile state.teal
$GOAL clerk compile clear.teal

accts=($(python3 sandbox_accounts.py))
ADMIN=${accts[0]}
echo "Admin = $ADMIN"

echo "Creating application"
# FIXME: dirty fix for https://stackoverflow.com/questions/71029547/impossible-to-redirect-output-of-docker-compose-v2-on-macos
# sandbox is manually modified to pass dc_exec_opt argument to docker-compose exec
# -T disables pty
export dc_exec_opt="-T"
app_id=$($GOAL app create --creator $ADMIN \
    --approval-prog state.teal \
    --clear-prog clear.teal\
    --global-byteslices 0 \
    --global-ints 1 \
    --local-ints 0 \
    --local-byteslices 0  | grep 'Created app' | awk '{ print $6 }' | tr -d "\r")

echo "App ID: $app_id"

app_addr=$($GOAL app info --app-id $app_id | grep 'Application account' | awk '{ print $3 }')
echo "App Address: $app_addr"

# Write app id and address to files so we can re-use them in other scripts
echo "$app_id" > ./app.id
echo "$app_addr" > ./app.addr

