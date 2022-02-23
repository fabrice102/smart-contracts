#!/bin/bash

set -eu -o pipefail

GOAL="$SB goal"
app_id=`cat app.id`

accts=($(python3 sandbox_accounts.py))
ADMIN=${accts[0]}
echo "Admin = $ADMIN"

$GOAL app read --app-id $app_id --global