Gunconf
=======

Gunconf is an utility to configure [Aimtrak guns](https://www.ultimarc.com/aimtrak.html) on linux systems

It is tested on ubuntu desktop and retropie.

Written in python on top of pygame, it **does not require an x server.**


# Install
## Prerequisites

`sudo apt install apt-transport-https python-dev python-pygame`

## Get the source
`git clone <repo>/gunconf.git`

## Install python module
`cd gunconf`

`python setup.py install`

## Udev rules
Application requires access to the aimtrak usb device. It is usually necessary to configure udev to let your specific user access that device.

To let any user access the device, do:

`sudo cp utils/aimtrak.rules /etc/udev/rules.d/99-aimtrak.rules`

`sudo udevadm control --reload-rules`


## Launch
To launch application, you can execute utils/gunconf.sh

For retropie users, you can add the app to the retropie menu by simply copying that file:

`scp utils/gunconf.sh pi@<your_pi_IP>:/home/pi/RetroPie/retropiemenu/`


# Known limitations
* does not support firmware update (you need a windows host for that...)
* does not support joystick configuration