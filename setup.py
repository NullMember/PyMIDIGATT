"""
Usage instructions:
- If you are installing: `python setup.py install`
- If you are developing: `python setup.py sdist --format=zip bdist_wheel --universal bdist_wininst && twine check dist/*`
"""
import PyMIDIGATT

from setuptools import setup
setup(
    name='PyMIDIGATT',
    version=PyMIDIGATT.version,
    author='Malik Enes Safak',
    author_email='e.maliksafak@gmail.com',
    packages=['PyMIDIGATT', 'PyMIDIGATT.MIDI', 'PyMIDIGATT.bluez', 'PyMIDIGATT.util'],
    url='https://github.com/NullMember/PyMIDIGATT',
    license='MIT',
    install_requires=[
        "BLEMidiTranslator"
    ],
    description='MIDI BLE GATT server for linux computers including single board computers',
    keywords = 'midi ble gatt server linux bluez dbus sbe raspberry pi'
)