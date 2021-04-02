#!/bin/python3
from PyMIDIGATT import PyMIDIGATT
import time
import rtmidi

def cb(message):
    timestamp, midi = message
    cmd = midi[0] & 0xF0
    chn = midi[0] & 0x0F
    print("Timestamp: ", timestamp)
    if cmd == 0x80:
        print("Note Off, Channel: {}, Note: {}, Velocity: {}".format(chn, midi[1], midi[2]))
    elif cmd == 0x90:
        print("Note On, Channel: {}, Note: {}, Velocity: {}".format(chn, midi[1], midi[2]))
    elif cmd == 0xA0:
        print("Poly Pressure, Channel: {}, Note: {}, Pressure: {}".format(chn, midi[1], midi[2]))
    elif cmd == 0xB0:
        print("Control Change, Channel: {}, Control: {}, Value: {}".format(chn, midi[1], midi[2]))
    elif cmd == 0xC0:
        print("Program Change, Channel: {}, Program: {}".format(chn, midi[1]))
    elif cmd == 0xD0:
        print("Aftertouch, Channel: {}, Pressure: {}".format(chn, midi[1]))
    elif cmd == 0xE0:
        print("Pitch Bend, Channel: {}, Value: {}".format(chn, (midi[1] << 7) | midi[2]))

if __name__ == "__main__":
    midiAdvertisement = PyMIDIGATT("Midi Test", cb)
    midiAdvertisement.run()
    while True:
        try:
            time.sleep(0.1)
        except:
            midiAdvertisement.stop()
            break