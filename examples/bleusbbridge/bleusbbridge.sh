#!/bin/bash
# go to current user directory
cd
# upgrade packages
sudo apt update
sudo apt upgrade -y
# install git
sudo apt install git -y
# install packages required for PyMIDIGATT
sudo apt install python3-pip python3-dbus python3-rtmidi -y
# clone BLEMidiTranslator package required for PyMIDIGATT
git clone https://github.com/NullMember/BLEMidiTranslator.git
# install BLEMidiTranslator package
sudo pip3 install --no-index BLEMidiTranslator/.
# remove BLEMidiTranslator directory
sudo rm -r BLEMidiTranslator
# clone PyMIDIGATT package
git clone https://github.com/NullMember/PyMIDIGATT.git
# copy bluetooth configuration file required for PyMIDIGATT to work
sudo cp PyMIDIGATT/configuration/main.conf /etc/bluetooth/main.conf
# copy bleusbbridge service to make it run on restart
sudo cp PyMIDIGATT/examples/bleusbbridge/bleusbbridge.service /etc/systemd/system/bleusbbridge.service
# copy bleusbbridge directory to root home
sudo cp -r PyMIDIGATT/examples/bleusbbridge /root/bleusbbridge
# install PyMIDIGATT package
sudo pip3 install --no-index PyMIDIGATT/.
# remove PyMIDIGATT directory
sudo rm -r PyMIDIGATT
# reload services
sudo systemctl daemon-reload
# enable bleusbbridge service
sudo systemctl enable bleusbbridge.services
# reboot system
sudo reboot