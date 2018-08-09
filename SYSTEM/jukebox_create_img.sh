#!/bin/bash

pwd

IMG=2017-09-07-raspbian-stretch-lite.img

if [ `id --user` -ne 0 ]
then
    echo "Run as root"
    exit 1
fi

test -d /tmp/mnt || mkdir /tmp/mnt

LOOP_BOOT=`kpartx -v -a $IMG | awk '{print $3}' | head -1`
LOOP_ROOT=${LOOP_BOOT/p1/p2}

sleep 1

mount /dev/mapper/${LOOP_BOOT} /tmp/mnt
touch /tmp/mnt/ssh
dir /tmp/mnt
umount /tmp/mnt

mount /dev/mapper/${LOOP_ROOT} /tmp/mnt
mkdir /tmp/mnt/root/INSTALL/
cp INSTALL/jukebox.sh /tmp/mnt/root/INSTALL/
cp INSTALL/jukebox.service /tmp/mnt/root/INSTALL/
cp INSTALL/wpa_supplicant.conf /tmp/mnt/etc/wpa_supplicant/wpa_supplicant.conf
dir /tmp/mnt/root
umount /tmp/mnt


rm -rf /tmp/mnt

kpartx -d $IMG

echo $LOOP_BOOT
echo $LOOP_ROOT

echo "dd bs=4M if=${IMG} of=/dev/sdX conv=fsync"
