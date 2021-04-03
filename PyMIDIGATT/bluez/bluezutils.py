import dbus
from PyMIDIGATT.bluez.consts import *

def get_managed_objects():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"),
				DBUS_OM_IFACE)
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_in_objects(objects, pattern=None):
	bus = dbus.SystemBus()
	for path, ifaces in objects.items():
		adapter = ifaces.get(ADAPTER_IFACE)
		if adapter is None:
			continue
		if not pattern or pattern == adapter["Address"] or \
							path.endswith(pattern):
			obj = bus.get_object(BLUEZ_SERVICE_NAME, path)
			return dbus.Interface(obj, ADAPTER_IFACE)
	raise Exception("Bluetooth adapter not found")

def find_device(device_address, adapter_pattern=None):
	return find_device_in_objects(get_managed_objects(), device_address,
								adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
	bus = dbus.SystemBus()
	path_prefix = ""
	if adapter_pattern:
		adapter = find_adapter_in_objects(objects, adapter_pattern)
		path_prefix = adapter.object_path
	for path, ifaces in objects.iteritems():
		device = ifaces.get(DEVICE_IFACE)
		if device is None:
			continue
		if (device["Address"] == device_address and
						path.startswith(path_prefix)):
			obj = bus.get_object(BLUEZ_SERVICE_NAME, path)
			return dbus.Interface(obj, DEVICE_IFACE)

	raise Exception("Bluetooth device not found")

def find_adapter_path_from_iface(iface = None):
	return find_adapter_path_from_iface_in_objects(get_managed_objects(), iface)

def find_adapter_path_from_iface_in_objects(objects, iface):
	for path, ifaces in objects.items():
		if ADAPTER_IFACE in ifaces.keys():
			if iface in ifaces.keys():
				return path
	
	return None