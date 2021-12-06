# Pi Pico Macro Keyboard
![Keyboard](media/jay-zhang-ZByWaPXD2fU-unsplash.png)

This repository contains code for DIY Macro Keyboards using the Raspberry Pi Pico and CircuitPython.

### Features:
- Support for multiple macro layers
- Supports all standard keyboard keys and media keys
- Supports lighting using neopixels
- Customizable

### Limits:
- Does not include row-scanning (yet?). All buttons have to be connected to an individual GPIO Pin.

## Install:
1. Install CircuitPython on the pi pico (guide: https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython).
The Pi Pico will now show up as a "CircuitPython" USB drive


2. Install the adafruit_hid library by downloading the library bundle as stated here (https://circuitpython.org/libraries). Unzip and copy the "lib/adafruit_hid" folder into the "lib" folder on your Pi Pico
  - If you want to use Neopixel lighting, also copy "lib/neopixel.mpy" into the "lib" folder of your pi pico


3. Copy the contents of "makrokeyboard.py" from the Repository into the existing "code.py" file on your Pi Pico
  - If you don't use Neopixels, comment everything neopixel-related in  "code.py"

## Customization:
Edit the "code.py" file on the Pi Pico by opening it in a text editor.

To add/change Keys and the pins of the keys, edit the "keymap" and "pins" list.
Note that the first entry of the "pins" list corresponds to the first entry of every layer in the "keymap" list, and so on.

More details found inside the python file.

Supported Keys:
- All standard keys and combinations of them listed here: https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
- All media keys listed here: https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-consumer-control-code-consumercontrolcode
- Keys for peeking/switching macro layers

## Credits
This project is inspired by the adafruit custom keyboard guide.
Check it out if you need a more detailed guide:
https://learn.adafruit.com/diy-pico-mechanical-keyboard-with-fritzing-circuitpython/overview

The code of the guide should be interchangeable with the code from this repo (although not tested)

Title Image:
https://unsplash.com/photos/ZByWaPXD2fU
