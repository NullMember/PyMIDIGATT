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

1. pip package (setuptools actually. I'm not sure setuptools is part of pip or not. But it's always good to have pip)  
2. dbus-python package. Since communication between PyMIDIGATT and BlueZ done through DBus messaging system.  
3. BLEMidiTranslator package. You can get it from [here](https://github.com/NullMember/BLEMidiTranslator). 
It's used to convert BLE-Midi<->Standart Midi messages  
4. rtmidi-python package (optional). Used for bleusbbridge example.  

I've not tried to install dbus package from pip, I'm not sure if it work. I've always used system package manager to install it.  
If you don't know what to do, check [this](#bleusbbridge) section.

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
**Update**: You can eliminate buffer with initializer option or can change buffer period.

## Latency

I've tested latency of created peripheral using BLED112 USB module with python script (using bgapi interface) running on Windows 10 machine. 
Python script connect BLED112 to BLE-MIDI peripheral and echo every MIDI message back. 
On PyMIDIGATT side, i've connected my Launchpad to Raspberry Pi Zero W running PyMIDIGATT and send noteon/noteoff 
messages from Launchpad to connected bluetooth device (in this case, BLED112)
PyMIDIGATT records time of button presses (on launchpad) and calculates round-trip time from echoed back message. 
It's not ideal setup for precise calculation but average round-trip latency is ~50ms most of the time. 
This means one-way latency is ~25ms. Real value can be little lower since I don't know how much latency added by BLED112 script or BLED112 itself. 
Also there is room for latency improvement. For example, i'm using wifi to connect RPI terminal and print out lots of latency information on screen. 
Wifi communication could increase latency, both wifi and bluetooth using same antenna on RPZ-W. Not using wifi is one option, 
completely disabling Wifi is another option for latency improvement.

## Connection Drop

After waiting hour or two without sending any message between devices, i've not encountered any connection drop. 

## Security

None. Anyone can connect to your Bluetooth MIDI device without hassle. Be careful for nifty hackers.  

## bleusbbridge

I wrote little program and accompanying udev service, installation script for who don't want to get their hands dirty. 
You can convert your USB-MIDI devices to Bluetooth MIDI device with it. You can install it by running:  
`curl -s https://raw.githubusercontent.com/NullMember/PyMIDIGATT/master/examples/bleusbbridge/bleusbbridge.sh | bash`  
But before you run it on your computer, please check [.sh file](examples/bleusbbridge/bleusbbridge.sh) to see what it does. 
I might be trying to delete your system32 folder. 

1. After executing command above, use `sudo nano /root/bleusbbridge/whitelist.txt` to edit usb-midi device whitelist to add your device's name (don't forget to read instructions in it)
2. If you don't know your device's name, connect it to your computer (or Raspberry Pi, you know) use `sudo /root/bleusbbridge/bleusbbridge.py --list` command to get names of connected usb-midi devices (both input and output ports)
3. After adding your device's name (both input and output name) to the list restart bleusbbridge service by running `sudo systemctl restart bleusbbridge.service`
4. Voila! You should see your BLE-MIDI Device (default name, can be changed by editing service file) in your favourite app which support bluetooth midi (not Windows users, obviously).

## Notes

- This software not tested on iOS and MacOS at this time. I don't know if they will ever connect or work with your shiny ble-midi device. Update: Not working on iOS and MacOS devices.
- To connect with your Android device, I suggest using [this](https://play.google.com/store/apps/details?id=com.mobileer.example.midibtlepairing) app. It will list your ble-midi device as standart midi device to other apps, so you can use any app supports midi functionality. But it's performance is not best.
- To test your ble-midi device on Windows you can use [this](https://webmidilab.appspot.com/blesynth/) tool. I don't understand how a software running on top of an OS can do this but not OS itself. Shame to Microsoft.
- That's it. Have fun!
