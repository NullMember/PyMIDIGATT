#!/usr/bin/env python3
from PyMIDIGATT import PyMIDIGATT
import time

timestamps = {}
log = []
intervals = [5, 6, 7, 8, 9, 10, 12, 15, 18, 20, 25, 30, 40, 50]
lengths = [100]
startTest = False
interactive = True

def writeMIDI(message):
    global timestamps
    midi = midiAdvertisement.midiEncoder.encode(message)
    timestamp = ((midi[0] & 0x7F) << 7)  | (midi[1] & 0x7F)
    midiAdvertisement.characteristic.writeMIDI(midi)
    timestamps[timestamp] = time.time()

def cb(messages):
    global timestamps
    receiveTime = time.time()
    for message in messages:
        timestamp, midi = message
        if midi[0] == 0x80:
            sendTime = timestamps.pop(timestamp)
            log.append(receiveTime - sendTime)
        elif midi[0] == 0x90:
            startTest = True
            print("Start Test signal received")

midiAdvertisement = PyMIDIGATT("Midi Test", cb)
midiAdvertisement.run()

if __name__ == "__main__":
    time.sleep(1)
    print("\nPress CTRL+C to exit")
    f = open("/boot/log.txt", "w")
    if interactive:
        while True:
            try:
                interval = input("Enter desired interval between messages in ms: ")
                length = input("Enter message length: ")
                try:
                    log = []
                    varint = float(interval)
                    varlen = int(length)
                    f.write("Interval: {:4.2f} ms, Length: {:4d} messages\n".format(varint, varlen))
                    for i in range(varlen):
                        writeMIDI([0x80, 0, 0])
                        time.sleep(varint / 1000)
                    time.sleep(1)
                    for i, l in enumerate(log):
                        f.write("{:3d}, {}\n".format(i, l))
                except:
                    print("Something wrong, please try again")
            except:
                midiAdvertisement.stop()
                f.close()
                break
    else:
        while True:
            if startTest:
                for length in lengths:
                    for interval in intervals:
                        log = []
                        f.write("Interval: {:4.2f} ms, Length: {:4d} messages\n".format(interval, length))
                        for i in range(length):
                            writeMIDI([0x80, 0, 0])
                            time.sleep(interval / 1000)
                        time.sleep(1)
                        for i, l in enumerate(log):
                            f.write("{:3d}, {}\n".format(i, l))
                midiAdvertisement.stop()
                f.close()
                break
            time.sleep(0.1)
