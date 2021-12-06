#
#        CircuitPython HID Macro Keyboary
#
#      Copyright 2021 github.com/Skyfighter64


import board
import digitalio
import usb_hid

import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

import neopixel


# define the available key types
class KeyType():
    # no action for this key
    NONE = 0
    # standard letters, numbers, and keyboard keys
    KEY = 1
    # media keys like volume or play/pause
    MEDIA = 2
    # switch makro layers
    LAYER = 3
    # change lighting
    LIGHTING = 4
# define available layer switch actions
class Layer():
    # switch to the layer while the key is pressed
    PEEK = 0
    # switch layers when key was pressed
    SWITCH = 1

# define available lighting modification actions
class Lighting():
    # turn the LEDs on/off by setting their brightness to  0.5 / 0
    TOGGLE = 0
    # increase the brightness of all leds in small steps
    INCREASE_BRIGHTNESS = 1
    # decrease the brightness of all leds
    DECREASE_BRIGHTNESS = 2


# keymap formats:
# (KeyType.NONE,)
# or
# (KeyType.KEY, (Keycode.A, Keycode.B, ...))
# or
# (KeyType.MEDIA, ConsumerControlCode.VOLUME_DECREMENT)
# or
# (KeyType.LAYER, (Layer.SWITCH, 1))
# or
# (KeyType.LIGHTING, Lighting.INCREASE_BRIGHTNESS))



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
        (KeyType.LIGHTING, Lighting.INCREASE_BRIGHTNESS), # adjust lighting brightness
        (KeyType.LIGHTING, Lighting.DECREASE_BRIGHTNESS),
        (KeyType.LIGHTING, Lighting.OFF),
        (KeyType.KEY, (Keycode.F16,)),  # more extra F keys for custom program hotkeys
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

# initialize neopixel leds
leds = neopixel.NeoPixel(board.GP28, 4, brightness=0.5, auto_write=False)

# variable for the currently active layer
activeLayer = 0
previousLayer = 0
# variable containing the previous layer if peeking or 'None' if not peeking

# initialize buttons as input with an internal Pull UP resistor
for pin in pins:
    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(pull=digitalio.Pull.UP)
    buttons.append(button)

# initialize the last states with False
last_states = [False] * len(buttons)


# function sending the pressed key event for the given key touple defined in the keymap
# @param key: a touple of the structure (KeyType.KEY, (Keycode[, Keycode, ...]))
#                       or       (KeyType.MEDIA, ConsumerControlCode)
#                       or       (KeyType.LAYER, (Layer.SWITCH | Layer.PEEK, layer index : int))
#                       or       (KeyType.LIGHTING, [Lighting Action])
#                       or       (KeyType.NONE, [...])
def PressKey(key):
    # reference global variables
    global activeLayer
    global previousLayer
    global leds

    # check for standard key actions
    if (key[0] == KeyType.KEY):
        try:
            keyboard.press(*key[1])
        except ValueError:
            # more than 6 keys were pressed
            # this is forbidden by the library
            pass
    # check for media key actions
    elif (key[0] == KeyType.MEDIA):
        consumer_control.press(key[1])
    # check for layer actions
    elif (key[0] == KeyType.LAYER):
        # switch to the layer
        previousLayer = activeLayer
        activeLayer = key[1][1]
    # check for lighting actions
    elif (key[0] == KeyType.LIGHTING):
        # check for lighting off action
        if(key[1] == Lighting.TOGGLE):
            if (leds.brightness == 0):
                leds.brightness = 0.5
            else:
                leds.brightness = 0
        elif(key[1] == Lighting.INCREASE_BRIGHTNESS):
            # increase led brightness if possible
            newBrightness = leds.brightness + 0.1
            if (newBrightness > 1.0):
                newBrightness = 1.0
            leds.brightness = newBrightness
        elif(key[1] == Lighting.DECREASE_BRIGHTNESS):
            # decrease led brightness if possible
            newBrightness = leds.brightness - 0.1
            if (newBrightness < 0):
                newBrightness = 0.0
            leds.brightness = newBrightness
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

# function defining the lighting of each layer
def UpdateLEDs():
    if(activeLayer == 0):
        leds[0] = (255, 20, 32)
        leds[1] = (125, 255, 32)
        leds[2] = (50, 32, 255)
        leds[3] = (255, 10, 255)

    else:
        leds[0] = (200, 20, 180)
        leds[1] = (40, 110, 195)
        leds[2] = (20, 120, 200)
        leds[3] = (220, 20, 160)
    leds.show()

# endless main loop
while True:
    # set the internal led on when default layer is active
    led.value = (activeLayer == 0)
    # check for key presses
    CheckKeys()
    # set the neopixels
    UpdateLEDs()
    # sleep for debouncing
    time.sleep(0.005)
