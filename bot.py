import ir_rx
import machine
import time
from machine import PWM
from machine import Pin
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging

def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    control_motors(data)

ir_pin = Pin(17, Pin.IN, Pin.PULL_UP)

ir_receiver = NEC_8(ir_pin, callback=ir_callback)

ir_receiver.error_function(print_error)

time.sleep(1)

pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq=pwm_rate, duty_u16=0) 

bin1_ph = Pin(9, Pin.OUT)
bin2_en = PWM(Pin(8), freq=pwm_rate, duty_u16=0)

pwm = 32000

def control_motors(command):
    """Control motors based on received IR command."""
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

while True:
    time.sleep(0.1)
