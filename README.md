# PyMIDIGATT

MIDI BLE GATT server for linux computers including single board computers.  
This software designed as proof-of-concept, use at your own risk!  

## What is PyMIDIGATT

PyMIDIGATT is BLE MIDI server (peripheral) implementation for computers running Linux. 
You can use PyMIDIGATT to design BLE MIDI controllers, keyboards etc. 
or to convert old USB-MIDI/Serial-MIDI devices to BLE-MIDI device easily.  

It heavily depends on BlueZ and DBus, there is no way to port this software to another OS. 
Designed for Raspberry Pi Zero W in mind, should work on other (single board) computers. 

## Installation

PyMIDIGATT is pure python package. You can clone and install using setup.py file.
But there is few dependencies.  

1. dbus-python package. Since communication between PyMIDIGATT and BlueZ done through DBus messaging system.  
2. rtmidi-python package (optional). Used for bleusbbridge example.  

## Usage

    from PyMIDIGATT import PyMIDIGATT
    import time
    
    def callback(messages):
        for message in messages:
            timestamp, midi = message
            print(timestamp, midi)
    
    midiAdvertisement = PyMIDIGATT("My BLE-MIDI Device", callback = callback)
    midiAdvertisement.run()
    while True:
        try:
            time.sleep(0.1)
        except:
            midiAdvertisement.stop()

You can also send midi message from your peripheral to device connected it using:

    midiAdvertisement.writeMIDI([0x90, 0x7F, 0x7F])
  