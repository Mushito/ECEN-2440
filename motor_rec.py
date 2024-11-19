import machine
from machine import I2C, Pin, PWM
import seesaw
import time

# Initialize I2C. Adjust pin numbers based on your Pico's configuration
i2c = I2C(0, scl=Pin(17), sda=Pin(16))

# Initialize the Seesaw driver with the I2C interface
# Use the Gamepad QT's I2C address from the Arduino code (0x50)
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

# Define button and joystick pin numbers as per the Arduino code
BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15

# Button mask based on Arduino code
BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | \
               (1 << BUTTON_A) | (1 << BUTTON_B) | \
               (1 << BUTTON_SELECT) | (1 << BUTTON_START)

# Define motor control pins and PWM configuration
pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT)  # Initialize GP12 as an OUTPUT
ain2_en = PWM(Pin(13), freq=pwm_rate, duty_u16=0)  # PWM on Pin 13

bin1_ph = Pin(9, Pin.OUT)
bin2_en = PWM(Pin(8), freq=pwm_rate, duty_u16=0)

# Initialize joystick center position
joystick_center_x = 511
joystick_center_y = 497

def setup_buttons():
    """Configure the pin modes for buttons."""
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    """Read and return the state of each button."""
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

def set_motor_speed(left_speed, right_speed):
    """Set motor speed for left and right motors."""
    # Set left motor direction and speed
    if left_speed > 0:
        ain1_ph.value(1)
        ain2_en.duty_u16(min(int(left_speed * 65535 / 100), 65535))
    elif left_speed < 0:
        ain1_ph.value(0)
        ain2_en.duty_u16(min(int(-left_speed * 65535 / 100), 65535))
    else:
        ain2_en.duty_u16(0)

    # Set right motor direction and speed
    if right_speed > 0:
        bin1_ph.value(1)
        bin2_en.duty_u16(min(int(right_speed * 65535 / 100), 65535))
    elif right_speed < 0:
        bin1_ph.value(0)
        bin2_en.duty_u16(min(int(-right_speed * 65535 / 100), 65535))
    else:
        bin2_en.duty_u16(0)

def main():
    """Main program loop."""
    setup_buttons()

    joystick_threshold = 50  # Adjust threshold as needed

    while True:
        # Read joystick positions
        current_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
        current_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

        # Calculate motor speed based on joystick position
        # Assuming joystick_center_x and joystick_center_y are the resting values
        delta_x = current_x - joystick_center_x
        delta_y = current_y - joystick_center_y

        # Normalize joystick values to motor speed (-100 to 100)
        left_motor_speed = max(min(delta_y + delta_x, 100), -100)
        right_motor_speed = max(min(delta_y - delta_x, 100), -100)

        # Set motor speed
        set_motor_speed(left_motor_speed, right_motor_speed)

        # Read buttons (for additional features if needed)
        current_buttons = read_buttons()

        # Add delay to prevent overwhelming the output
        time.sleep(0.1)

if __name__ == "__main__":
    main()
