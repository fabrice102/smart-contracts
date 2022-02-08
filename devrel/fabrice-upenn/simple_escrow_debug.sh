#!/bin/bash

set -eu -o pipefail

$SB copyTo dryrun.msgp
$SB copyTo simple_escrow.teal
$SB tealdbg debug simple_escrow.teal -d dryrun.msgp

#rm dryrun.msgp