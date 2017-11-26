#!/bin/sh

RSYNC=/usr/bin/rsync
SSH=/usr/bin/ssh
KEY=/home/loco/edges/src/cron/rsync-key
RUSER=guest
RHOST=enterprise.sese.asu.edu
RPATH=/data5/edges/data/2014_February_Boolardy/
LPATH=/home/loco/edges/data/
LOGPATH=/home/loco/edges/src/cron/$(date +%Y_%j_%H)_rsync.log
#BWLIMIT=5000
#BWLIMIT=100000

$RSYNC -azPO -e "$SSH -i $KEY" --bwlimit=$BWLIMIT --log-file=$LOGPATH $LPATH $RUSER@$RHOST:$RPATH 
