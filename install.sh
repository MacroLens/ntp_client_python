#!/bin/bash

NTP_DIR=/usr/local/sbin/ntp_sync

if [ "$EUID" -ne 0 ]
  then echo "$0 must be run as root."
  exit
fi

mkdir -p $NTP_DIR
cp ntpsync_delay.py adjtime_ntp.c config.ini $NTP_DIR

gcc -fPIC -shared -o $NTP_DIR/adjtime_ntp.so $NTP_DIR/adjtime_ntp.c

cp ntpsync.service ntpsync.timer /etc/systemd/system
systemctl daemon-reload
systemctl enable --now ntpsync.timer
