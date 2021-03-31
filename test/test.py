#!/bin/python3
from PyMIDIGATT import PyMIDIGATT
import signal
import time
import rtmidi

def cb(val):
    values, options = val
    print(values)

if __name__ == "__main__":
    midiAdvertisement = PyMIDIGATT.PyMIDIGATT("Midi Test")
    midiAdvertisement.addCallback(cb)
    midiAdvertisement.run()
    try:
        time.sleep(0.1)
    except:
        midiAdvertisement.stop()