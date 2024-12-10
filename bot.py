import ir_rx
import machine
import time
from machine import PWM, Pin
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error
import seesaw
from ir_tx.nec import NEC

ir_pin = Pin(17, Pin.IN, Pin.PULL_UP)

RFA = Pin(4, Pin.IN, Pin.PULL_UP)  # RF Go
RFB = Pin(5, Pin.IN, Pin.PULL_UP)  # RF Reverse
RFC = Pin(6, Pin.IN, Pin.PULL_UP)  # RF Turn Right
RFD = Pin(7, Pin.IN, Pin.PULL_UP)  # RF Turn Left

pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq=pwm_rate, duty_u16=0) 
bin1_ph = Pin(9, Pin.OUT)
bin2_en = PWM(Pin(8), freq=pwm_rate, duty_u16=0)
pwm = 32000

i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16))
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)
tx_pin = Pin(18, Pin.OUT, value=0)
device_addr = 0x01
transmitter = NEC(tx_pin)

BUTTON_SELECT = 0
BUTTONS_MASK = 1 << BUTTON_SELECT

commands = {
    0x10: "Motor CounterClockwise",
    0x20: "Stop Motors",
    0x30: "Motor Clockwise",
    0x40: "Turn Left",
    0x50: "Turn Right",
}

RF_COMMANDS = {
    RFA: 0x10,
    RFB: 0x20,
    RFC: 0x40,
    RFD: 0x30,
}

def ir_callback(data, addr, _):
    print(f"Received IR command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    control_motors(data)

def control_motors(command):
    if command == 0x10:  # motor CounterClockwise
        print("Motor CounterClockwise")
        ain1_ph.low()
        ain2_en.duty_u16(pwm)
        bin1_ph.high()
        bin2_en.duty_u16(pwm)
    elif command == 0x20:  # stop motors
        print("Motor OFF")
        ain1_ph.low()
        ain2_en.duty_u16(0)
        bin1_ph.low()
        bin2_en.duty_u16(0)
    elif command == 0x30:  # motor Clockwise
        print("Motor Clockwise")
        ain1_ph.high()
        bin1_ph.low()
        ain2_en.duty_u16(pwm)
        bin2_en.duty_u16(pwm)
    elif command == 0x40: # Turn Left
        print ("Turning Left")
        ain1_ph.high()
        bin1_ph.high()
        ain2_en.duty_u16(pwm)
        bin2_en.duty_u16(pwm)
    elif command == 0x50: # Turn Right
        print ("Turning Right")
        ain1_ph.low()
        bin1_ph.low()
        ain2_en.duty_u16(pwm)
        bin2_en.duty_u16(pwm)
    else:
        print("Unknown command")

ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

def setup_buttons():
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

RF_ON = False
setup_buttons()

while True:
    # Check SELECT button to toggle between RF and IR
    current_buttons = read_buttons()
    if not current_buttons & (1 << BUTTON_SELECT):
        RF_ON = not RF_ON
        print("RF MODE:", "ON" if RF_ON else "OFF")
        time.sleep(0.3)

    if RF_ON:
        for pin, command in RF_COMMANDS.items():
            if not pin.value():
                print(f"RF COMMAND {commands[command]} EXECUTED")
                control_motors(command)
                time.sleep(0.3)
    else:
        pass

    time.sleep(0.1)
