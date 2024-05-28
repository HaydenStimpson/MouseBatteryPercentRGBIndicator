# Possibly requires this to be installed, depending on how libusb was installed: https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/
# Also requires Razer Synapse to be installed
import json
import time
import usb.core
import usb.util
from usb.backend import libusb1
import requests

# Initialize id variables - change these to use with different Razer mice
vid = 0x1532
pid = 0x007b
transaction_id = b"\xff"

# Code to get battery percentage (get_battery_percent(), battery_msg(), get_mouse()) adapted from
# https://github.com/hsutungyu/razer-mouse-battery-windows/blob/main/mamba.pyw

def get_battery_percent():
    """"Send message to mouse, wait some time, then record the returned answer
    Returns int from 0 to 100"""
    try:
        mouse = get_mouse()
        mouse.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x300, data_or_wLength=battery_msg(), wIndex=0x00)
        time.sleep(0.5)
        result = mouse.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01, wValue=0x300, data_or_wLength=90, wIndex=0x00)

        # Convert battery percent to int
        return int(result[9] / 255 * 100)
    except:
        print("Could not connect to mouse.")
        return 0

def battery_msg():
    """Generate and return message to send to the mouse via USB - message asks for current battery percent"""
    msg = b"\x00" + transaction_id + b"\x00\x00\x00\x02\x07\x80" + bytes(80) + b"\x85\x00"
    return msg

def get_mouse():
    """Find and return wireless mouse based on its various ids"""
    try:
        backend = libusb1.get_backend()
        mouse = usb.core.find(idVendor = vid, idProduct = pid, backend = backend)
        return mouse
    except:
        print("Something is wrong with the 'pid' or 'vid' settings, or libusb is not installed correctly.")
        return 0

def find_device_uri():
    """Check the local Razer API server to find the uri of the specific device. I only have one."""
    try:
        initialize_json = {
            "title": "Razer Battery Indicator",
            "description": "Razer mouse RGB battery indicator",
            "author": {
                "name": "Hayden Stimpson",
                "contact": "https://haydenstimpson.github.io/"
            },
            "device_supported": [
                "mouse",
            ],
            "category": "application"
        }

        returned_uri = requests.post("http://localhost:54235/razer/chromasdk", json=initialize_json)
        print(returned_uri.text)
        uri = json.loads(returned_uri.text)['uri']
        return uri
    except:
        print("Could not connect to Razer Chroma server.")
        return 0

def convert_battery_percent_to_color(battery_percent):
    """Generate RGB values scaling smoothly from green to red based on battery percent."""
    try:
        blue = 0
        green = int((battery_percent * 255 / 100))
        red = int(255 - green)
        return '%02x%02x%02x' % (blue, green, red)
    except:
        print("Battery percent is invalid.")

uri = find_device_uri()
if uri == 0:
    # Try again
    uri = find_device_uri()
if uri != 0:
    while True:
        # Update battery percent every 15 minutes
        battery = get_battery_percent()
        if battery == 0:
            # Try again if return 0 - this seems to be the default if the device can't return the correct number.
            # Trying again tends to fix the connection and get the correct percent.
            battery = get_battery_percent()
        print(battery)
        # Need to update API every 10 seconds to maintain connection
        for x in range(90):
            color = int(convert_battery_percent_to_color(battery), 16)
            rgb_json = {
                "effect": "CHROMA_STATIC",
                "param": {
                    "color": color
                }
            }
            color_post_return = requests.put(uri + "/mouse", json=rgb_json)
            print(color_post_return.text)
            time.sleep(10)
