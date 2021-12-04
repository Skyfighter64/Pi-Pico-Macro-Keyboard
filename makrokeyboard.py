#
#        CircuitPython HID Macro Keyboary
#
#      Copyright 2021 github.com/Skyfighter64


import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# define the available key types
class KeyType():
    # standard letters, numbers, and keyboard keys
    KEY = 1
    # media keys like volume or play/pause
    MEDIA = 2
    # switch makro layers
    LAYER = 3
# define available layer switch modes
class Layer():
    # switch to the layer while the key is pressed
    PEEK = 0
    # switch layers when key was pressed
    SWITCH = 1

import time

# keymap formats:
# (KeyType.KEY, (Keycode.A, Keycode.B, ...))
# or
# (KeyType.MEDIA, ConsumerControlCode.VOLUME_DECREMENT)
# or
# (KeyType.LAYER, (Layer.SWITCH, 1))


# note: for one-element Keycodes, an extra comma is needed
#   Example: (KeyType.KEY, (Keycode.A,))
#                                    ^
#       See python docs of touple for more details
# For a list of all available Keycodes and ConsumerControlCodes, see:
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
# and
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-consumer-control-code-consumercontrolcode
#

# keymap containing all key layers with all key presses
# every i'th entry corresponds to the i'th button in the "pins" list
keymap = [
    # layer 0 (default):
    [
        (KeyType.MEDIA, ConsumerControlCode.VOLUME_INCREMENT), #Volume UP
        (KeyType.MEDIA, ConsumerControlCode.VOLUME_DECREMENT), # Volume Down
        (KeyType.MEDIA, ConsumerControlCode.MUTE),             # Volume Mute
        (KeyType.KEY, (Keycode.ALT, Keycode.F10)), # shadowplay
        (KeyType.MEDIA, ConsumerControlCode.SCAN_NEXT_TRACK),
        (KeyType.MEDIA, ConsumerControlCode.PLAY_PAUSE),
        (KeyType.MEDIA, ConsumerControlCode.SCAN_PREVIOUS_TRACK),
        (KeyType.KEY, (Keycode.WINDOWS, Keycode.PRINT_SCREEN)),
        (KeyType.KEY, (Keycode.F20,)),      # Extra F Keys for program Hotkeys
        (KeyType.KEY, (Keycode.F21,)),
        (KeyType.LAYER, (Layer.SWITCH, 1)), # switch to makro layer 1
        (KeyType.KEY, (Keycode.F23,))
    ],

    # layer 1:
    [
        (KeyType.KEY, (Keycode.F13,)), # more extra F keys for custom program hotkeys
        (KeyType.KEY, (Keycode.F14,)),
        (KeyType.KEY, (Keycode.F15,)),
        (KeyType.KEY, (Keycode.F16,)),
        (KeyType.KEY, (Keycode.F17,)),
        (KeyType.KEY, (Keycode.F18,)),
        (KeyType.KEY, (Keycode.F19,)),
        (KeyType.KEY, (Keycode.CONTROL, Keycode.F13)),
        (KeyType.KEY, (Keycode.CONTROL,Keycode.F14,)),
        (KeyType.KEY, (Keycode.CONTROL,Keycode.F15,)),
        (KeyType.LAYER, (Layer.SWITCH, 0)), # switch back to makro layer 0 when pressed]
        (KeyType.KEY, (Keycode.CONTROL,Keycode.F16,))
    ]
]


# initialize the internal LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

keyboard = Keyboard(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)

# the gpio pins at which each button is connected
pins = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13]
buttons = []

activeLayer = 0
previousLayer = 0

# initialize buttons as input with an internal Pull UP resistor
for pin in pins:
    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(pull=digitalio.Pull.UP)
    buttons.append(button)

# initialize the last states with False
last_states = [False] * len(buttons)


# function sending the pressed key event for the given key touple
# @param key: a touple of the structure (KeyType.KEY, (Keycode[, Keycode, ...]))
#                       or       (KeyType.MEDIA, ConsumerControlCode)
#                       or       (KeyType.LAYER, (Layer.SWITCH | Layer.PEEK, layer index : int))
def PressKey(key):
    # reference global variables
    global activeLayer
    global previousLayer

    if (key[0] == KeyType.KEY):
        try:
            keyboard.press(*key[1])
        except ValueError:
            # more than 6 keys were pressed
            # this is forbidden by the library
            pass
    elif (key[0] == KeyType.MEDIA):
        consumer_control.press(key[1])
    elif (key[0] == KeyType.LAYER):
        # switch to the layer
        previousLayer = activeLayer
        activeLayer = key[1][1]
    print("Pressed:  " + str(key[1]))

# function sending the released key event for the given key touple
# @param key: a touple of the structure (KeyType.KEY, (Keycode[, Keycode, ...]))
#                       or       (KeyType.MEDIA, ConsumerControlCode)
#                       or       (KeyType.LAYER, (Layer.SWITCH | Layer.PEEK, layer index : int))
def ReleaseKey(key):
    # reference global variables
    global activeLayer
    global previousLayer

    if (key[0] == KeyType.KEY):
        keyboard.release(*key[1])
    elif (key[0] == KeyType.MEDIA):
        consumer_control.release()
    elif (key[0] == KeyType.LAYER):
        # check if layer mode is "PEEK"
        if(key[1][0] == Layer.PEEK):
            # reset to old layer
            activeLayer = previousLayer
    print("Released: " + str(key[1]))


# function checking and executing all key presses
def CheckKeys():
    # reference global variables
    global activeLayer
    # loop through all buttons
    for i in range(len(buttons)):
        # check if the index exceeds the keymap layer's size
        if (i >= len(keymap[activeLayer])):
            # layer size exceeded, stop checking
            break
        # check if a button was pressed
        if (not buttons[i].value and last_states[i]) :
            PressKey(keymap[activeLayer][i])
        # check if button was released
        elif ( buttons[i].value and not last_states[i]):
            ReleaseKey(keymap[activeLayer][i])
        # update the last state
        last_states[i] = buttons[i].value

# endless main loop
while True:
    # set the internal led on when default layer is active 
    led.value = (activeLayer == 0)
    # check for key presses
    CheckKeys()
    # sleep for debouncing
    time.sleep(0.005)
