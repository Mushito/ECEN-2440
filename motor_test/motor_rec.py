import machine
from machine import I2C, Pin, PWM
import seesaw
import time

i2c = I2C(0, scl=Pin(17), sda=Pin(16))

seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15

BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | \
               (1 << BUTTON_A) | (1 << BUTTON_B) | \
               (1 << BUTTON_SELECT) | (1 << BUTTON_START)

pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT) 
ain2_en = PWM(Pin(13), freq=pwm_rate, duty_u16=0)

bin1_ph = Pin(9, Pin.OUT)
bin2_en = PWM(Pin(8), freq=pwm_rate, duty_u16=0)

joystick_center_x = 511
joystick_center_y = 497

ir_led = PWM(Pin(18), freq=38000, duty_u16=0)  # Pin 18 for IR LED, 38kHz frequency

def setup_buttons():
    """Configure the pin modes for buttons."""
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    """Read and return the state of each button."""
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

def transmit_ir_command(command):
    """Transmit NEC command using IR LED."""

    ir_led.duty_u16(32768)  # 50% duty cycle to send IR pulses
    time.sleep_us(9000)
    ir_led.duty_u16(0)
    time.sleep_us(4500)

    def send_bit(bit):
        ir_led.duty_u16(32768)
        time.sleep_us(560)
        ir_led.duty_u16(0)
        if bit:
            time.sleep_us(1690)  # Logic 1
        else:
            time.sleep_us(560)   # Logic 0

    for i in range(8):
        send_bit((command >> i) & 1)

    for i in range(8):
        send_bit(((~command) >> i) & 1)

    ir_led.duty_u16(32768)
    time.sleep_us(560)
    ir_led.duty_u16(0)

def handle_joystick_and_buttons():
    """Handle joystick and button inputs to send appropriate IR commands."""
    current_buttons = read_buttons()
    if current_buttons & (1 << BUTTON_A):
        transmit_ir_command(0x10)  
    elif current_buttons & (1 << BUTTON_B):
        transmit_ir_command(0x20)
    elif current_buttons & (1 << BUTTON_X):
        transmit_ir_command(0x30)
    elif current_buttons & (1 << BUTTON_Y):
        transmit_ir_command(0x40)
    elif current_buttons & (1 << BUTTON_START):
        transmit_ir_command(0x50)
    elif current_buttons & (1 << BUTTON_SELECT):
        transmit_ir_command(0x60)

    current_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
    current_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

    delta_x = current_x - joystick_center_x
    delta_y = current_y - joystick_center_y

    if delta_y > 100:
        transmit_ir_command(0x30)  # Example command for moving joystick up
    elif delta_y < -100:
        transmit_ir_command(0x40)  # Example command for moving joystick down
    elif delta_x > 100:
        transmit_ir_command(0x50)  # Example command for moving joystick right
    elif delta_x < -100:
        transmit_ir_command(0x60)  # Example command for moving joystick left

def main():
    """Main program loop."""
    setup_buttons()

    while True:
        handle_joystick_and_buttons()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
