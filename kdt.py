#!/usr/bin/env python
import hashlib, sys

def getKindleModel(serial):
    return { '1':'Kindle 1',\
    '2':'Kindle 2 U.S.',\
    '3':'Kindle 2 international',\
    '8':'Kindle 3 WIFI',\
    '6':'Kindle 3 3G + WIFI U.S.',\
    'A':'Kindle 3 3G + WIFI European',\
    '4':'Kindle DX U.S.',\
    '5':'Kindle DX international',\
    '9':'Kindle DX Graphite'}.get(serial[4])

def getKindlePassword(serial):
    return "fiona%s"%hashlib.md5("%s\n"%serial).hexdigest()[7:11]

serials = []

# Trying to get devices via UDisks
if sys.platform.startswith("linux"):
    try:
        import dbus
        bus = dbus.SystemBus()
        ud_manager_obj = bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
        ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.UDisks')
        for dev in ud_manager.EnumerateDevices():
            device_obj = bus.get_object("org.freedesktop.UDisks", dev)
            device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
            if device_props.Get('org.freedesktop.UDisks.Device', "DriveVendor")=='Kindle' and\
                    device_props.Get('org.freedesktop.UDisks.Device', "DeviceIsDrive"):
                serials.append(str(device_props.Get('org.freedesktop.UDisks.Device', "DriveSerial")))
    except:
        sys.stderr.write("ERR Can't use UDisks interface\n")

# Trying to get devices via libusb
try:
    import pylibusb as usb
    usb.init()
    if not usb.get_busses():
        usb.find_busses()
        usb.find_devices()
    busses = usb.get_busses()
    for bus in busses:
        for dev in bus.devices:
            if (dev.descriptor.idVendor == 0x1949 and
                dev.descriptor.idProduct == 0x0004):
                libusb_handle = usb.open(dev)
                try:
                    s = usb.get_string_simple(libusb_handle,dev.descriptor.iSerialNumber)
                    if not s in serials:
                        serials.append(s)
                except usb.USBError, error:
                    sys.stderr.write("ERR Libusb error: %s\nERR May be you is not root?\n"%error.message)
except:
    sys.stderr.write("ERR Can't use libusb interface\n")

for serial in serials:
    print "Device: %s\nSerial: %s\nPassword: %s"%(getKindleModel(serial),serial,getKindlePassword(serial))
