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
     KEY = 1
     MEDIA = 2

import time

# keymap format examples:
# (KeyType.KEY, (Keycode.A, Keycode.B, ...))
# or
# (KeyType.MEDIA, ConsumerControlCode.VOLUME_DECREMENT)
# has to be the size of pins list (every pin needs a keycode)

# note: for one-element Keycodes, an extra comma is needed
#   Example: (KeyType.KEY, (Keycode.A,))
#                                    ^
#       See python docs of touple for more details
# For a list of all available Keycodes and ConsumerControlCodes, see:
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
# and
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-consumer-control-code-consumercontrolcode
#
keymap = [
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
(KeyType.KEY, (Keycode.F22,)),
(KeyType.KEY, (Keycode.F23,))]




# initialize the internal LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

keyboard = Keyboard(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
pins = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13]
buttons = []

# initialize buttons as input with an internal Pull UP resistor
for pin in pins:
    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(pull=digitalio.Pull.UP)
    buttons.append(button)

# initialize the last states with False
last_states = [False] * len(buttons)


# function sending the pressed key event for the given key touple
# key: a touple of the structure (KeyType.KEY, (Keycode[, Keycode, ...]))
#                       or       (KeyType.MEDIA, ConsumerControlCode)
def PressKey(key):
    if (key[0] == KeyType.KEY):
        try:
            keyboard.press(*key[1])
        except ValueError:
            # more than 6 keys were pressed
            # this is forbidden by the library
            pass
    elif (key[0] == KeyType.MEDIA):
        consumer_control.press(key[1])
    print("Pressed:  " + str(key[1]))

# function sending the released key event for the given key touple
# key: a touple of the structure (KeyType.KEY, (Keycode[, Keycode, ...]))
#                       or       (KeyType.MEDIA, ConsumerControlCode)
def ReleaseKey(key):
    if (key[0] == KeyType.KEY):
        keyboard.release(*key[1])
    elif (key[0] == KeyType.MEDIA):
        consumer_control.release()
    print("Released: " + str(key[1]))

# assign all sent keyboard values
def CheckKeys():
    # check and execute all keypresses
    for i in range(len(buttons)):
        # check if a button was pressed
        if (not buttons[i].value and last_states[i]) :
            PressKey(keymap[i])
        # check if button was released
        elif ( buttons[i].value and not last_states[i]):
            ReleaseKey(keymap[i])
        # update the last state
        last_states[i] = buttons[i].value

# endless main loop
while True:
    # set the internal led to button 0
    led.value = buttons[0].value
    # check for key presses
    CheckKeys()
    # sleep for debouncing
    time.sleep(0.005)
