# PyMIDIGATT

MIDI BLE GATT server for linux computers including single board computers.  
This software designed as proof-of-concept, use at your own risk!  

## What is PyMIDIGATT

PyMIDIGATT is BLE MIDI server (peripheral) implementation for computers running Linux. 
You can use PyMIDIGATT to design BLE MIDI controllers, keyboards etc. 
or to convert old USB-MIDI/Serial-MIDI device to BLE-MIDI device easily.  

It heavily depends on BlueZ and DBus, there is no way to port this software to another OS. 
Designed for Raspberry Pi Zero W in mind, should work on other (single board) computers. 

## Installation

PyMIDIGATT is pure python package. You can clone and install using setup.py file.
But there is few dependencies.  

1. pip package (setuptools actually. I'm not sure setuptools is part of pip or not. But it's always good to have pip)  
2. dbus-python package. Since communication between PyMIDIGATT and BlueZ done through DBus messaging system.  
3. BLEMidiTranslator package. You can get it from [here](https://github.com/NullMember/BLEMidiTranslator). 
It's used to convert BLE-Midi<->Standart Midi messages  
4. rtmidi-python package (optional). Used for bleusbbridge example.  

I've not tried to install dbus package from pip, I'm not sure if it work. I've always used system package manager to install it. 

## Usage

First of all, copy [main.conf](configuration/main.conf) file to `/etc/bluetooth/main.conf`. 
BlueZ DBus API not allow everything we need. So this is mandatory to get things work. 
Before copying, you may want to backup old main.conf file, it's up to you.  
After that, run few lines of Python code:  

    from PyMIDIGATT import PyMIDIGATT
    import time
    
    def callback(messages):
        for message in messages:
            timestamp, midi = message
            print(timestamp, midi)
    
    midiAdvertisement = PyMIDIGATT("My BLE-MIDI Device", callback)
    midiAdvertisement.run()
    while True:
        try:
            time.sleep(0.1)
        except:
            midiAdvertisement.stop()

You can also send midi message from your peripheral to device connected it using:

    midiAdvertisement.writeMIDI([0x90, 0x7F, 0x7F])

writeMIDI function use some sort of ring buffer internally. It will write incoming MIDI messages to buffer and send them together in 10ms period. 
This will cause latency but encoding more midi messages together will reduce outgoing bytes in total. 
I don't know what is the best since i'm not much sensitive about latency. But feedbacks are always welcomed.

## Latency

I've tested latency of created peripheral using BLED112 USB module with python script (using bgapi interface) running on Windows 10 machine. 
Python script connect BLED112 to BLE-MIDI peripheral and echo every MIDI message back. 
On PyMIDIGATT side, i've connected my Launchpad to Raspberry Pi Zero W running PyMIDIGATT and send noteon/noteoff 
messages from Launchpad to connected bluetooth device (in this case, BLED112)
PyMIDIGATT records time of button presses (on launchpad) and calculates round-trip time from echoed back message. 
It's not ideal setup for precise calculation but average round-trip latency is ~60ms most of the time. 
This means one-way latency is ~30ms. Real value can be little lower since I don't know how much latency added by BLED112 script or BLED112 itself.

## Connection Drop

After waiting hour or two without sending any message between devices, i've not encountered any connection drop. 

## bleusbbridge

To be continued...
