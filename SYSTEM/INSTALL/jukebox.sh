#!/bin/bash

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

RW_PIN=26
HALT_PIN=22
RF_PIN=21

# START INSTALL ------------------------------------------------------------


# Given a filename, a regex pattern to match and a replacement string:
# Replace string if found, else no change.
# (# $1 = filename, $2 = pattern to match, $3 = replacement)
replace() {
	grep $2 $1 >/dev/null
	if [ $? -eq 0 ]; then
		# Pattern found; replace in file
		sed -i "s/$2/$3/g" $1 >/dev/null
	fi
}

# Given a filename, a regex pattern to match and a replacement string:
# If found, perform replacement, else append file w/replacement on new line.
replaceAppend() {
	grep $2 $1 >/dev/null
	if [ $? -eq 0 ]; then
		# Pattern found; replace in file
		sed -i "s/$2/$3/g" $1 >/dev/null
	else
		# Not found; append on new line (silently)
		echo $3 | sudo tee -a $1 >/dev/null
	fi
}

# Given a filename, a regex pattern to match and a string:
# If found, no change, else append file with string on new line.
append1() {
	grep $2 $1 >/dev/null
	if [ $? -ne 0 ]; then
		# Not found; append on new line (silently)
		echo $3 | sudo tee -a $1 >/dev/null
	fi
}

# Given a filename, a regex pattern to match and a string:
# If found, no change, else append space + string to last line --
# this is used for the single-line /boot/cmdline.txt file.
append2() {
	grep $2 $1 >/dev/null
	if [ $? -ne 0 ]; then
		# Not found; insert in file before EOF
		sed -i "s/\'/ $3/g" $1 >/dev/null
	fi
}


replace /boot/cmdline.txt "console=serial0,115200 " ""
append1 /boot/config.txt "pi3-disable-bt" "dtoverlay=pi3-disable-bt"
replace /boot/config.txt "dtparam=audio=on" "#dtparam=audio=on"

echo
echo "Starting installation..."
echo "Updating package index files..."
apt-get update

echo "Removing unwanted packages..."
apt-get remove -y --force-yes --purge triggerhappy cron logrotate dbus \
 dphys-swapfile xserver-common lightdm fake-hwclock

echo "Installing needed packages..."
apt-get -y install vlc-nox python3-yaml python3-serial rfkill wiringpi pulseaudio
apt-get -y --force-yes autoremove --purge

# Replace log management with busybox (use logread if needed)
echo "Installing busybox-syslogd..."
apt-get -y --force-yes install busybox-syslogd; dpkg --purge rsyslog

echo "Configuring system..."

GPIORF="gpio -g mode $RF_PIN up\n\
if [ \`gpio -g read $RF_PIN\` -eq 1 ] ; then\n\
\trfkill block phy0\n\
\ttvservice -o\n\
fi\n"
# Check if already present in rc.local:
grep "gpio -g read" /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
    # Already there, but make sure pin is correct:
    sed -i "s/^.*gpio\ -g\ read.*$/$GPIORF/g" /etc/rc.local >/dev/null
else
    # Not there, insert before final 'exit 0'
    sed -i "s/^exit 0/$GPIORF\\nexit 0/g" /etc/rc.local >/dev/null
fi

# Add fastboot, noswap and/or ro to end of /boot/cmdline.txt
append2 /boot/cmdline.txt fastboot fastboot
append2 /boot/cmdline.txt noswap noswap
append2 /boot/cmdline.txt ro^o^t ro

# Move /var/spool to /tmp
rm -rf /var/spool
ln -s /tmp /var/spool

# Move /var/lib/lightdm and /var/cache/lightdm to /tmp
rm -rf /var/lib/lightdm
rm -rf /var/cache/lightdm
ln -s /tmp /var/lib/lightdm
ln -s /tmp /var/cache/lightdm

# Set-up config for pulseaudio
ln -s /dev/shm/pi/config /home/pi/.config

# Make SSH work
replaceAppend /etc/ssh/sshd_config "^.*UsePrivilegeSeparation.*$" "UsePrivilegeSeparation no"
# bbro method (not working in Jessie?):
#rmdir /var/run/sshd
#ln -s /tmp /var/run/sshd

# Change spool permissions in var.conf (rondie/Margaret fix)
replace /usr/lib/tmpfiles.d/var.conf "spool\s*0755" "spool 1777"

# Move dhcpd.resolv.conf to tmpfs
touch /tmp/dhcpcd.resolv.conf
rm /etc/resolv.conf
ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf

# Make edits to fstab
# make / ro
# tmpfs /var/log tmpfs nodev,nosuid 0 0
# tmpfs /var/tmp tmpfs nodev,nosuid 0 0
# tmpfs /tmp     tmpfs nodev,nosuid 0 0
replace /etc/fstab "vfat\s*defaults\s" "vfat    defaults,ro "
replace /etc/fstab "ext4\s*defaults,noatime\s" "ext4    defaults,noatime,ro "
append1 /etc/fstab "/var/log" "tmpfs /var/log tmpfs nodev,nosuid 0 0"
append1 /etc/fstab "/var/tmp" "tmpfs /var/tmp tmpfs nodev,nosuid 0 0"
append1 /etc/fstab "\s/tmp"   "tmpfs /tmp    tmpfs nodev,nosuid 0 0"
mkdir -p /MUSIC
append1 /etc/fstab "/MUSIC"   "/dev/sda1 /MUSIC ext4 defaults,ro 0 0"

cp /root/INSTALL/jukebox.service /lib/systemd/system/jukebox.service
systemctl enable jukebox

echo << EOF > /etc/asound.conf
    pcm.!default  {
     type hw card 1
    }
    ctl.!default {
     type hw card 1
    }
EOF

# PROMPT FOR REBOOT --------------------------------------------------------

echo "Done."
echo
reboot
exit 0
