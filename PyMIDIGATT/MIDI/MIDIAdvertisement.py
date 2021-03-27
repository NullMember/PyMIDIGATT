from ..bluez.Advertisement import *

class MidiAdvertisement(Advertisement):
    def __init__(self, name, path, bus, index):
        super().__init__(path, bus, index, 'peripheral')
        self.add_manufacturer_data(0xFFFF, [0x00, 0x01, 0x02, 0x03])        #0xFFFF = Test ID, https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
        self.add_local_name(name)
        self.include_tx_power = True