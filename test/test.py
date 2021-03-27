from PyMIDIGATT import PyMIDIGATT
import signal
import time
import rtmidi

if __name__ == "__main__":
    midiAdvertisement = PyMIDIGATT("Midi Test")
    midiAdvertisement.run()
    try:
        time.sleep(0.1)
    except:
        midiAdvertisement.stop()