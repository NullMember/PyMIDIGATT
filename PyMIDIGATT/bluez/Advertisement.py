import dbus
import dbus.service
from .consts import *
from .exceptions import *

class Advertisement(dbus.service.Object):

    def __init__(self, path, bus, index, advertising_type):
        self.path = path + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = None
        self.include_tx_power = False
        self.data = None
        self.min_interval = None
        self.max_interval = None
        self.tx_power = None
        self.appearance = None
        self.discoverable = None
        super().__init__(bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qv')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='sv')
        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)
        if self.include_tx_power:
            properties['Includes'] = dbus.Array(["tx-power"], signature='s')
        if self.data is not None:
            properties['Data'] = dbus.Dictionary(
                self.data, signature='yv')
        if self.min_interval is not None:
            properties['MinInterval'] = dbus.UInt32(self.min_interval)
        if self.max_interval is not None:
            properties['MaxInterval'] = dbus.UInt32(self.max_interval)
        if self.tx_power is not None:
            properties['TxPower'] = dbus.Int16(self.tx_power)
        if self.appearance is not None:
            properties['Appearance'] = dbus.UInt16(self.appearance)
        if self.discoverable is not None:
            properties['Discoverable'] = dbus.Boolean(self.discoverable)
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    def add_local_name(self, name):
        if not self.local_name:
            self.local_name = ""
        self.local_name = dbus.String(name)

    def add_data(self, ad_type, data):
        if not self.data:
            self.data = dbus.Dictionary({}, signature='yv')
        self.data[ad_type] = dbus.Array(data, signature='y')
    
    def add_min_interval(self, interval):
        self.min_interval = 0 if interval < 0 else (10484 if interval > 10484 else interval)
    
    def add_max_interval(self, interval):
        self.max_interval = 0 if interval < 0 else (10484 if interval > 10484 else interval)
    
    def add_tx_power(self, power):
        self.tx_power = -127 if power < -127 else (20 if power > 20 else power)
    
    def add_appearance(self, category, sub):
        self.appearance = (((category << 6) & 0xFFC0) | (sub & 0x3F)) & 0xFFFF

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('%s: Released!' % self.path)