#!/bin/python3
from PyMIDIGATT import PyMIDIGATT
import time
import rtmidi
import rtmidi.midiutil
from argparse import ArgumentParser

midiAdvertisement = None
midiin = None
midiout = None

def blmidicb(message):
    for midi in message:
        timestamp, value = midi
        print("blmidi", value)
        midiout.send_message(value)

def rtmidicb(message, _):
    midi, delta = message
    print("rtmidi", midi)
    midiAdvertisement.writeMIDI(midi)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="Name of Midi Input device")
    parser.add_argument("-o", "--output", help="Name of Midi Output device")
    parser.add_argument("-l", "--list", help="List available Midi input and output devices", action="store_true")
    parser.add_argument("-n", "--name", help="Name of BLE Midi Peripheral", default="Midi Test")
    args = parser.parse_args()

    if args.list:
        rtmidi.midiutil.list_input_ports()
        rtmidi.midiutil.list_output_ports()
    elif not args.output or not args.input:
        print("Midi Input and Midi Output name required.")
    else:
        midiAdvertisement = PyMIDIGATT(args.name, blmidicb)
        midiin = rtmidi.midiutil.open_midiinput(args.input)[0]
        midiout = rtmidi.midiutil.open_midioutput(args.output)[0]
        midiin.set_callback(rtmidicb)
        midiAdvertisement.run()
        while True:
            try:
                time.sleep(0.1)
            except:
                midiAdvertisement.stop()
                break