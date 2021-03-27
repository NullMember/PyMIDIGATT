from ..bluez.GATT import *

class MidiService(Service):
    MIDI_UUID = "03B80E5A-EDE8-4B33-A751-6CE34EC4C700"

    def __init__(self, path, bus, index):
        super().__init__(path, bus, index, self.MIDI_UUID, True)

class MidiCharacteristic(Characteristic):
    MIDI_CHRC_UUID = "7772E5DB-3868-4112-A1A9-F2669D106BF3"

    def __init__(self, bus, index, service, readCallback = None, writeCallback = None):
        super().__init__(bus, index, self.MIDI_CHRC_UUID, ['read', 'write', 'notify'], service)
        self.notifying = False
        self.readCallback = readCallback
        self.writeCallback = writeCallback
    
    def addReadCallback(self, callback):
        self.readCallback = callback
    
    def addWriteCallback(self, callback):
        self.writeCallback = callback
    
    def StartNotify(self):
        if self.notifying:
            return
        print("Midi Notify Enable")
        self.notifying = True
    
    def StopNotify(self):
        if not self.notifying:
            return
        print("Midi Notify Disable")
        self.notifying = False
    
    def ReadValue(self, options):
        print("Midi Read", options)
        if self.readCallback == None:
            return []
        else:
            return dbus.ByteArray(self.readCallback())
    
    def WriteValue(self, value, options):
        print("Midi Write", value, options)
        if self.writeCallback == None:
            return
        else:
            self.writeCallback((value, options))
            return