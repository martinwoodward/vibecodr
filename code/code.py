"""
VIBECODR keyboard.  Make the LED's have a nice colorwheel animation, then when 
the button is pressed, turn them all white and send a spacebar press signal to the computer.

This code is designed to run on a Raspberry Pi Pico W with CircuitPython.
It uses the following additional libraries that need to be installed in the lib folder:
* Adafruit CircuitPython HID (https://github.com/adafruit/Adafruit_CircuitPython_HID)

REQUIRED HARDWARE:
* RGB NeoPixel LEDs connected to pin GP15.
* Button connected to GP4
"""
import time
import board
import math
from rainbowio import colorwheel
import neopixel
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 12

pixels = neopixel.NeoPixel(board.GP15, num_pixels, auto_write=False)
pixels.brightness = 0.8

# The button is connected to GP4 (IC2 SDA)
keys = keypad.Keys((board.GP4,), value_when_pressed=True, pull=True)

# Initialize USB HID keyboard
keyboard = Keyboard(usb_hid.devices)

# Function to set all pixels to white with a brightness percentage.
def set_all_white(brightness_factor=1.0):
    # Apply brightness factor (0.0 to 1.0) to white
    value = int(255 * brightness_factor)
    pixels.fill((value, value, value))
    pixels.show()

white_mode = False
white_mode_start = 0  # Time when white mode started
white_throb_position = 0  # Position in the throb cycle (0-255)
j = 0  # Keep track of rainbow animation position

while True:
    event = keys.events.get()
    current_time = time.monotonic()
    
    if event:
        if event.pressed:
            # Enter white mode
            white_mode = True
            white_mode_start = current_time
            set_all_white()
            keyboard.press(Keycode.SPACE)
        else:
            # Button released
            keyboard.release(Keycode.SPACE)
    
    # Check if white mode should end (after 5 seconds)
    if white_mode and (current_time - white_mode_start >= 5.0):
        white_mode = False
        
    # Animation logic
    if white_mode:
        # Create throbbing effect for white mode using a sine wave
        brightness = 0.5 + 0.5 * math.sin(white_throb_position * math.pi / 128)
        set_all_white(brightness)
        white_throb_position = (white_throb_position + 2) % 256
    else:
        # Perform one step of the rainbow animation
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = colorwheel(pixel_index & 255)
        pixels.show()
        j = (j + 1) % 255  # Increment and wrap around
    
    time.sleep(0.01)  # Small delay for smooth animation
