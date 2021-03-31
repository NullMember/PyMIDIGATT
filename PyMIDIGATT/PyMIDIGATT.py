import dbus
import dbus.mainloop.glib

from gi.repository import GLib

import threading
import time

from PyMIDIGATT.MIDI.MIDIAdvertisement import *
from PyMIDIGATT.MIDI.MIDIGATT import *
from PyMIDIGATT.bluez.bluezutils import *
from PyMIDIGATT.bluez.consts import *
from PyMIDIGATT.util.RingBuffer import *

class PyMIDIGATT:
    AdvertiserPath = '/org/test/ble/midi/advertisement'
    ServicePath = '/org/test/ble/midi/service'

    def __init__(self, name, callback = None):
        self.running = False
        self.mainloop = GLib.MainLoop()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        # get bus from system
        self.bus = dbus.SystemBus()
        # get adapter and power it up
        self.adapter_path = find_adapter_path_from_iface(ADAPTER_IFACE)
        self.adapter_properties = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path), "org.freedesktop.DBus.Properties")
        self.adapter_properties.Set(ADAPTER_IFACE, "Powered", dbus.Boolean(1))
        self.adapter_properties.Set(ADAPTER_IFACE, "Discoverable", dbus.Boolean(1))
        self.adapter_properties.Set(ADAPTER_IFACE, "Alias", dbus.String(name))
        # get managers
        self.gatt_manager = self.findGattManager()
        self.le_advertising_manager = self.findLeAdvertisingManager()
        # initialize midi application
        self.application = Application(self.bus)
        self.service = MidiService(self.ServicePath, self.bus, 0)
        self.application.add_service(self.service)
        self.characteristic = MidiCharacteristic(self.bus, 0, self.service)
        self.service.add_characteristic(self.characteristic)
        # initialize advertiser
        self.advertisement = MidiAdvertisement(name, self.AdvertiserPath, self.bus, 0)
        # create midi related variables
        self.midiHeader = 0
        self.midiTimestamp = 0
        self.midiStatus = 0
        self.midiHeaderCounter = 0
        self.midiMessageLength = 0
        self.midiMessageBuffer = [0] * 2
        # callback for bleMidiDecoder
        self.callback = callback

    def run(self):
        if not self.running:
            self.running = True
            self.register()
            self.thread = threading.Thread(target = self.mainloop.run)
            self.thread.start()
            print("Advertisement started")
            # add our midi decoder to characteristic
            self.characteristic.addCallback(self.bleMidiDecoder)
    
    def stop(self):
        if self.running:
            self.running = False
            self.unregister()
            print("Advertisement ended")
            self.mainloop.quit()
            self.characteristic.addCallback(None)
    
    def addCallback(self, callback):
        self.callback = callback
    
    def sendNoteOff(self, channel, note, velocity): self.writeMIDI([0x80 | (channel & 0x0F), note, velocity])
    def sendNoteOn(self, channel, note, velocity): self.writeMIDI([0x90 | (channel & 0x0F), note, velocity])
    def sendPolyPressure(self, channel, note, pressure): self.writeMIDI([0xA0 | (channel & 0x0F), note, pressure])
    def sendControlChange(self, channel, control, value): self.writeMIDI([0xB0 | (channel & 0x0F), control, value])
    def sendProgramChange(self, channel, program): self.writeMIDI([0xC0 | (channel & 0x0F), program])
    def sendAftertouch(self, channel, pressure): self.writeMIDI([0xD0 | (channel & 0x0F), pressure])
    def sendPitchBend(self, channel, value): self.writeMIDI([0xE0 | (channel & 0x0F), value & 0x7F, (value >> 7) & 0x7F])
    
    def writeMIDI(self, value):
        if not isinstance(value, list):
            value = [value]
        currentTime = int(time.time() * 1000) % (0x1 << 13)
        header = 0x80 | ((currentTime >> 7) & 0x3F)
        timestamp = 0x80 | (currentTime & 0x7F)
        self.characteristic.writeMIDI([header, timestamp] + value)

    def register(self):
        self.gatt_manager.RegisterApplication(self.application, {}, reply_handler = self.gattManagerReplyHandler, error_handler = self.gattManagerErrorHandler)
        self.le_advertising_manager.RegisterAdvertisement(self.advertisement, {}, reply_handler = self.advertisementManagerReplyHandler, error_handler = self.advertisementManagerErrorHandler)

    def unregister(self):
        try:
            self.gatt_manager.UnregisterApplication(self.application.get_path())
            print("Application succesfully unregistered")
        except Exception as e:
            print(self.application.get_path(), e)
        try:
            self.le_advertising_manager.UnregisterAdvertisement(self.advertisement.get_path())
            print("Advertisement succesfully unregistered")
        except Exception as e:
            print(self.advertisement.get_path(), e)

    def findGattManager(self):
        try:
            return dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path), GATT_MANAGER_IFACE)
        except:
            raise Exception(GATT_MANAGER_IFACE + ' interface not found')

    def findLeAdvertisingManager(self):
        try:
            return dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path), LE_ADVERTISING_MANAGER_IFACE)
        except:
            raise Exception(LE_ADVERTISING_MANAGER_IFACE, + ' interface not found')
    
    def gattManagerReplyHandler(self):
        print("Application succesfully registered")
    
    def gattManagerErrorHandler(self, error):
        raise Exception(error)
    
    def advertisementManagerReplyHandler(self):
        print("Advertisement succesfully registered")
    
    def advertisementManagerErrorHandler(self, error):
        raise Exception(error)
    
    #cursed algorithm, do not use at home
    def bleMidiDecoder(self, message):
        values, options = message
        for index, val in enumerate(values):
            if val & 0x80:
                if self.midiHeaderCounter < 0:
                    self.midiHeaderCounter = 0
                self.midiHeaderCounter += 1
            else:
                if self.midiHeaderCounter == 1:
                    self.midiTimestamp = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                elif self.midiHeaderCounter == 2:
                    self.midiTimestamp = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                    self.midiStatus = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                elif self.midiHeaderCounter == 3:
                    self.midiHeader = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                    self.midiTimestamp = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                    self.midiStatus = values[index - self.midiHeaderCounter]
                    self.midiHeaderCounter -= 1
                if self.midiMessageLength == 0:
                    cmd = self.midiStatus & 0xF0
                    if cmd == 0x80: self.midiMessageLength = 2      # note off
                    elif cmd == 0x90: self.midiMessageLength = 2    # note on
                    elif cmd == 0xA0: self.midiMessageLength = 2    # poly pressure
                    elif cmd == 0xB0: self.midiMessageLength = 2    # control change
                    elif cmd == 0xC0: self.midiMessageLength = 1    # program change
                    elif cmd == 0xD0: self.midiMessageLength = 1    # aftertouch
                    elif cmd == 0xE0: self.midiMessageLength = 2    # pitch bend
                    elif cmd == 0xF0: self.midiMessageLength = 0    # system messages, variable length
                    self.midiHeaderCounter -= 1
                if self.midiHeaderCounter < 0:
                    cmd = self.midiStatus & 0xF0
                    # we currently not support system messages, otherwise this is really bad idea
                    if self.midiMessageLength > 0:
                        self.midiMessageBuffer[2 - self.midiMessageLength] = val
                        self.midiMessageLength -= 1
                    if self.midiMessageLength == 0:
                        timestamp = ((self.midiHeader & 0x3F) << 7) | (self.midiTimestamp & 0x7F)
                        if cmd == 0x80 or cmd == 0x90 or cmd == 0xA0 or cmd == 0xB0 or cmd == 0xE0:
                            if self.callback is not None:
                                self.callback((timestamp, [self.midiStatus, self.midiMessageBuffer[0], self.midiMessageBuffer[1]]))
                        elif cmd == 0xC0 or cmd == 0xD0:
                            if self.callback is not None:
                                self.callback((timestamp, [self.midiStatus, self.midiMessageBuffer[1]]))