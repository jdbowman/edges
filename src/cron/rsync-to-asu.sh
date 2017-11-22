#!/bin/sh

RSYNC=/usr/bin/rsync
SSH=/usr/bin/ssh
KEY=/home/loco/edges/cron/rsync-key
RUSER=guest
RHOST=enterprise.sese.asu.edu
RPATH=/data1/edges/data/2014_February_Boolardy/
LPATH=/home/loco/edges/data/
LOGPATH=/media/DATA/cron/$(date +%Y_%j_%H)_rsync.log
#BWLIMIT=5000
BWLIMIT=100000

$RSYNC -azPO -e "$SSH -i $KEY" --bwlimit=$BWLIMIT --log-file=$LOGPATH $LPATH $RUSER@$RHOST:$RPATH 
