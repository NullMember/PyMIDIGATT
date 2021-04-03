#!/usr/bin/env python3
from PyMIDIGATT import PyMIDIGATT
import time
import rtmidi
import rtmidi.midiutil
import os
from argparse import ArgumentParser

DEFAULT_WHITELIST = "whitelist.txt"
midiAdvertisement = None
midiin = rtmidi.MidiIn()
midiout = rtmidi.MidiOut()
connected = False

def blmidicb(message):
    for midi in message:
        timestamp, value = midi
        print("blmidi", value)
        midiout.send_message(value)

def rtmidicb(message, _):
    midi, delta = message
    print("rtmidi", midi)
    midiAdvertisement.writeMIDI(midi)

def readWhitelist(path):
    inputNames = []
    outputNames = []
    if os.path.exists(path):
        with open(path, 'r') as f:
            lines = f.readlines()
            parse = 0
            for line in lines:
                if line[0] == '#':
                    pass
                elif line[0] == ';':
                    if "Input" in line:
                        parse = 1
                        pass
                    if "Output" in line:
                        parse = 2
                        pass
                else:
                    if parse == 1:
                        inputNames.append(line)
                    elif parse == 2:
                        outputNames.append(line)
    return inputNames, outputNames

def checkMidiPorts(inputPorts, outputPorts):
    inPorts = midiin.get_ports()
    outPorts = midiout.get_ports()
    inPort = None
    outPort = None
    for port in inputPorts:
        if port in inPorts:
            inPort = port
            break
    for port in outputPorts:
        if port in outPorts:
            outPort = port
    return inPort, outPort

def midiError(type, messsage, data):
    global connected
    midiAdvertisement.stop()
    connected = False

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="Name of Midi Input device")
    parser.add_argument("-o", "--output", help="Name of Midi Output device")
    parser.add_argument("-l", "--list", help="List available Midi input and output devices", action="store_true")
    parser.add_argument("-w", "--whitelist", help="Specify custom whitelist file")
    parser.add_argument("-n", "--name", help="Name of BLE Midi Peripheral", default="BLE-MIDI Device")
    args = parser.parse_args()
    deviceFound = False
    inputNames = []
    outputNames = []
    whitelistPath = ""

    if args.list:
        rtmidi.midiutil.list_input_ports()
        rtmidi.midiutil.list_output_ports()
        connected = False
    elif args.output or args.input:
        if args.output:
            outputNames.append(args.output)
        else:
            raise Exception("If you manually specify input name, output name is required")
        if args.input:
            inputNames.append(args.input)
        else:
            raise Exception("If you manually specify output name, input name is required")
    elif args.whitelist:
        if os.path.exists(args.whitelist):
            whitelistPath = args.whitelist
            inputNames, outputNames = readWhitelist(whitelistPath)
        else:
            raise Exception("Specified whitelist file not found")
    else:
        if os.path.exists(DEFAULT_WHITELIST):
            whitelistPath = DEFAULT_WHITELIST
            inputNames, outputNames = readWhitelist(whitelistPath)
        else:
            raise Exception("Default whitelist file not found")
    if not inputNames:
        raise Exception("Input names are empty")
    if not outputNames:
        raise Exception("Output names are empty")

    midiAdvertisement = PyMIDIGATT(args.name, blmidicb)

    while True:
        if connected:
            midiin.set_callback(rtmidicb)
            midiAdvertisement.run()
            while True:
                try:
                    time.sleep(0.1)
                except:
                    midiAdvertisement.stop()
                    midiin.close_port()
                    midiout.close_port()
                    break
            break
        else:
            try:
                inName, outName = checkMidiPorts(inputNames, outputNames)
                if inName and outName:
                    midiin = rtmidi.midiutil.open_midiinput(inName, interactive=False)
                    midiout = rtmidi.midiutil.open_midioutput(outName, interactive=False)
                    midiin.set_error_callback(midiError)
                    midiout.set_error_callback(midiError)
                    connected = True
                time.sleep(1.0)
            except:
                break