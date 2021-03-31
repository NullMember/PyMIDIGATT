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

    def __init__(self, name):
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
        self.inputBuffer = RingBuffer(256)
        self.outputBuffer = RingBuffer(256)
        self.sysexBuffer = RingBuffer(256)
        self.midiHeader = 0
        self.midiTimestamp = 0
        self.midiStatus = 0
        self.midiHeaderCounter = 0

    def run(self):
        if not self.running:
            self.running = True
            self.register()
            self.thread = threading.Thread(target = self.mainloop.run)
            self.thread.start()
            print("Advertisement started")
    
    def stop(self):
        if self.running:
            self.running = False
            self.unregister()
            print("Advertisement ended")
            self.mainloop.quit()
    
    def addCallback(self, callback):
        self.characteristic.addCallback(callback)
    
    def writeMIDI(self, value):
        self.characteristic.writeMIDI(value)

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
    
    def decodeMidi(self, values):
        self.inputBuffer.write(values)
        for index, val in enumerate(values):
            if val & 0x80:
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
                else:
                    pass