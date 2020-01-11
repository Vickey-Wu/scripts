#!/bin/bash

# e.g
:<<!
1. add execute right first with `chmod +x clean_log.sh`
2. run: sh clean_log.sh {PATH} {SIZE}
root@vickey:/home/ubuntu/scripts/shell# sh clean_log.sh /var/log/ 10
-rw-r----- 1 syslog adm 13310643 Jan 11 10:43 /var/log/auth.log
-rw-r----- 1 syslog adm 43379216 Jan  6 06:25 /var/log/auth.log-202001061578263101
!

# script content
PATH=$1
SIZE=$2
FIND_LOG=`/usr/bin/sudo /usr/bin/find ${PATH} -name "*.log*" -size +${SIZE}M`
for log in ${FIND_LOG}
do
    /bin/ls -l ${log}
    > ${log}
done
