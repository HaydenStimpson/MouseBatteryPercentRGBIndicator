# Possibly requires this to be installed, depending on how libusb was installed: https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/

import time
import usb.core
import usb.util
from usb.backend import libusb1

vid = 0x1532
pid = 0x007b
wired_pid = 0x007a # Not sure if needed
transaction_id = b"\xff"

# Code to get battery percentage (next three functions) adapted from
# https://github.com/hsutungyu/razer-mouse-battery-windows/blob/main/mamba.pyw

def get_battery_percent():
    # send message to mouse, wait some time, then record the returned answer
    mouse = get_mouse()
    mouse.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x300, data_or_wLength=battery_msg(), wIndex=0x00)
    time.sleep(0.5)
    result = mouse.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01, wValue=0x300, data_or_wLength=90, wIndex=0x00)

    # Convert battery percent to int
    return int(result[9] / 255 * 100)

def battery_msg():
    # Generate message to send to the mouse via USB - message asks for current battery percent
    msg = b"\x00" + transaction_id + b"\x00\x00\x00\x02\x07\x80" + bytes(80) + b"\x85\x00"
    return msg

def get_mouse():
    # Find wireless mouse based on its various ids
    backend = libusb1.get_backend()
    mouse = usb.core.find(idVendor = vid, idProduct = pid, backend = backend)
    return mouse

battery = get_battery_percent()
print(battery)
