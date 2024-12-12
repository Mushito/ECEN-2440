import ir_tx
import seesaw
import time
import machine
from ir_tx.nec import NEC
from machine import Pin

tx_pin = Pin(18, Pin.OUT, value=0)
device_addr = 0x01
transmitter = NEC(tx_pin)

BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15

i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16))

time.sleep_ms(50)

seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

led = Pin("LED", Pin.OUT)

commands = {
    BUTTON_A: 0x10,  # Motor CounterClockwise
    BUTTON_B: 0x20,  # Turn Right
    BUTTON_X: 0x30,  # Motor Clockwise
    BUTTON_Y: 0x40,  # Turn Left
    BUTTON_START: 0x50,  # Stop Motors
    BUTTON_SELECT: 0x60 #TOGGLE RF IR
}

BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | \
               (1 << BUTTON_A) | (1 << BUTTON_B) | \
               (1 << BUTTON_SELECT) | (1 << BUTTON_START)

def setup_buttons():
    """Configure the pin modes for buttons."""
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    """Read and return the state of each button."""
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

if __name__ == "__main__":
    setup_buttons()
    while True:
        current_buttons = read_buttons()

        for button, command in commands.items():
            if not current_buttons & (1 << button):
                transmitter.transmit(device_addr, command)
                print("COMMAND", hex(command), "TRANSMITTED.")
                led.toggle()
                time.sleep(0.3)
