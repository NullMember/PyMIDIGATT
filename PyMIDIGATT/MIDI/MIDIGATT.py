from PyMIDIGATT.bluez.GATT import *

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
            self.callback(list(bytes(value)))
            return

class DeviceInformationService(Service):
    INFO_UUID = '0000180A-0000-1000-8000-00805F9B34FB'
    def __init__(self, path, bus, index):
        super().__init__(path, bus, index, self.INFO_UUID, True)

class ManufacturerCharacteristic(Characteristic):
    MANUF_UUID = '00002A29-0000-1000-8000-00805F9B34FB'
    def __init__(self, bus, index, service, manufacturer_name):
        super().__init__(bus, index, self.MANUF_UUID, ['read'], service)
        self.name = manufacturer_name

    def ReadValue(self, options):
        return dbus.ByteArray(self.name)

class ModelCharacteristic(Characteristic):
    MODEL_UUID = '00002A24-0000-1000-8000-00805F9B34FB'
    def __init__(self, bus, index, service, model_name):
        super().__init__(bus, index, self.MODEL_UUID, ['read'], service)
        self.name = model_name

    def ReadValue(self, options):
        return dbus.ByteArray(self.name)
