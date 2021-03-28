from ..bluez.Advertisement import *

class MidiAdvertisement(Advertisement):
    def __init__(self, name, path, bus, index):
        super().__init__(path, bus, index, 'peripheral')
        self.add_local_name(name)
        self.add_service_uuid("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
        # self.add_min_interval(5)
        # self.add_max_interval(15)
        # self.discoverable = True
        # self.include_tx_power = True