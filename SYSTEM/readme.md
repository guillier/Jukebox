
# Installation

## Creating image (Linux)

* Download a [Raspbian Stretch Lite image](https://www.raspberrypi.org/downloads/raspbian/). The script was developped using the version 2017-09-07 (which can be found here [http://downloads.raspberrypi.org/raspbian/images/](http://downloads.raspberrypi.org/raspbian/images/)) but should work with subsequent ones.
* Unzip the image
* Edit the image name in ```jukebox_create_img.sh``` (IMG=2017-09-07-raspbian-stretch-lite.img)
* Run ```jukebox_create_img.sh```
* Copy the image to the SD-card (the exact command is displayed at the end of the execution of ```jukebox_create_img.sh```)

* If using a separate USB Flash stick, copy the content of MUSIC on it (root directory) to get started
* If using the SD-card, copy the content of MUSIC on the /MUSIC directory of the 2nd partition

Note that currently the player is located on the /MUSIC

## First boot

**DO NOT PLUG THE RFID Card Reader as it interferes with the console before configuration**

* Log onto the Raspberry

```bash
sudo -s
cd /root/INSTALL
sh jukebox.sh
```

The System will update itself, install the jukebox and should reboot in read-only mode.


# Maintenance

In order to boot with Wifi, the Hall effect sensor needs to be activated with a strong magnet (or the line ```rfkill block phy0``` removed from ```/etc/rc.local``` if the system is not used).


* To switch to RW mode:
```
mount -o rw,remount /
```

* And with the music directory (if a separate USB stick is used):

```
mount -o rw,remount /MUSIC
```

Once in Read-Write mode, all traditional commands can be used normally. But a proper *halt* or a return to Read-Only is required before unplugging the power!!!


