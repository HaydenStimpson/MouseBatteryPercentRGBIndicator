# Razer RGB Mouse Battery Indicator

## Introduction
Recently I bought a new mouse - the Razer Viper Ultimate wireless mouse.
This mouse comes with a charging dock that has an RGB underglow. By default this lighting indicates the battery percent, 
but only when the mouse is charging on the dock. The purpose of this project is to change this behaviour to always show the battery percentage
of the mouse via the RGB of the charging dock (as the charging dock is always plugged in and the mouse RGB is turned off).
This behaviour is not part of the Razer RGB software.
This software is written specifically for my mouse, though can be easily adapted for other Razer mice by updating the IDs (and possibly the battery message).

## Method
The solution I have come up with to solve this problem is the following steps:
1. Determine the various IDs of the mouse.
    1. The vendor ID is 1532, which can easily be found online.
    2. The product ID is 007b, which can be found in Device Manager.
    3. The transaction ID is ff, which can be determined in the 'OpenRazer' project: https://github.com/openrazer/openrazer/blob/master/driver/razermouse_driver.c
        1. Search for the razer_attr_read_charge_level function.
        2. Search for your device in the lists, and copy the corresponding transaction ID.
2. Get the battery percent information from the mouse.
    1. Most reasonable way to do this seems to be by sending a message to the mouse asking to report its battery percent.
    2. The specific message that needs to be sent was adapted from: https://github.com/hsutungyu/razer-mouse-battery-windows/tree/main
        1. For my mouse this is: b"\x00" + transaction_id + b"\x00\x00\x00\x02\x07\x80" + bytes(80) + b"\x85\x00"
            1. To adapt this to a new mouse, update the transaction id. The '\x85' section might also become incorrect as it is based on the length of the message. 
    3. Record the returned battery percentage.
3. Convert this percent into a corresponding RGB colour.
   1. Uses different colour for each stepped number. 100% is green, 0% is red.
4. Send this RGB colour to the RGB charging dock.
    1. Use the Razer REST API to send the corresponding RGB colour to the charging dock. 

## Helpful repos for this project:
1. https://github.com/hsutungyu/razer-mouse-battery-windows
2. https://github.com/openrazer
3. https://github.com/Tekk-Know/RazerBatteryTaskbar
