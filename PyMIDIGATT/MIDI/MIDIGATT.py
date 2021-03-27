from ..bluez.GATT import *

class MidiService(Service):
    MIDI_UUID = "03B80E5A-EDE8-4B33-A751-6CE34EC4C700"

    def __init__(self, path, bus, index):
        super().__init__(path, bus, index, self.MIDI_UUID, True)

class MidiCharacteristic(Characteristic):
    MIDI_CHRC_UUID = "7772E5DB-3868-4112-A1A9-F2669D106BF3"

    def __init__(self, bus, index, service, callback = None):
        super().__init__(bus, index, self.MIDI_CHRC_UUID, ['read', 'write-without-response', 'notify'], service)
        self.notifying = False
        self.callback = callback
    
    def writeMIDI(self, value):
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': dbus.ByteArray(value)}, [])
    
    def addCallback(self, callback):
        self.callback = callback
    
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
    
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
    
    def ReadValue(self, options):
        return []
    
    def WriteValue(self, value, options):
        if self.callback == None:
            return
        else:
            self.callback(bytes(value))
            return