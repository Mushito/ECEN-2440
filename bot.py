import ir_rx
import machine
import time
from machine import PWM, Pin
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

RFA = Pin(4, Pin.IN, Pin.PULL_UP)  # RF Go
RFB = Pin(5, Pin.IN, Pin.PULL_UP)  # RF Reverse
RFC = Pin(6, Pin.IN, Pin.PULL_UP)  # RF Turn Right
RFD = Pin(7, Pin.IN, Pin.PULL_UP)  # RF Turn Left

pwm = 16000
turn_pwm = 10000
ain1_ph = Pin(14, Pin.OUT)
ain2_en = PWM(Pin(15), freq=pwm, duty_u16=0)

bin1_ph = Pin(12, Pin.OUT)
bin2_en = PWM(Pin(13), freq=pwm, duty_u16=0)

led = Pin("LED", Pin.OUT)
led.toggle()

ir_pin = Pin(18, Pin.IN, Pin.PULL_UP)

RF_ON = False

def ir_callback(data, addr, _):
    global RF_ON
    print(f"Received IR command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    if data == 0x60:  # Toggle RF mode
        led.toggle()
        RF_ON = not RF_ON
        print("RF MODE:", "ON" if RF_ON else "OFF")
    elif data == 0x70:
        pwm = 32000
    elif data == 0x80:
        pwm = 8000
    else:
        control_motors(data)

def ramp_motors_straight(motor1, motor2):
    for i in range(0, pwm, 1000):
        motor1.duty_u16(i)
        motor2.duty_u16(i)
        time.sleep(0.01)

def ramp_motors_turn(motor1, motor2):
    for i in range(0, turn_pwm, 1000):
        motor1.duty_u16(i)
        motor2.duty_u16(i)
        time.sleep(0.01)

ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

commands = {
    0x10: "Right",
    0x20: "Backwards",
    0x30: "Foward",
    0x40: "Left",
    0x50: "Stop Motors",
}

RF_COMMANDS = {
    RFA: 0x10,
    RFB: 0x30,
    RFC: 0x40,
    RFD: 0x50,
}

def control_motors(command):
    if command == 0x10:  # motor CounterClockwise
        ain1_ph.low()
        bin1_ph.high()
        ramp_motors_turn(ain2_en, bin2_en)
    elif command == 0x50:  # stop motors
        print("Motor OFF")
        motors_off()
    elif command == 0x30:  # motor Clockwise
        ain1_ph.high()
        bin1_ph.low()
        ramp_motors_straight(ain2_en, bin2_en)
    elif command == 0x40:  # Turn Left
        ain1_ph.high()
        bin1_ph.high()
        ramp_motors_turn(ain2_en, bin2_en)
    elif command == 0x20:  # straight
        ain1_ph.low()
        bin1_ph.low()
        ramp_motors_straight(ain2_en, bin2_en)
    else:
        print("Unknown command")

def motors_off():
    ain1_ph.low()
    bin1_ph.low()
    ain2_en.duty_u16(0)
    bin2_en.duty_u16(0)

while True:
    if RF_ON:
        active_command = None
        if RFA.value():  # Button pressed (value = 0)
            active_command = 0x10
            control_motors(0x10)
            time.sleep(0.5)
            active_command = None
            motors_off()
        elif RFB.value():  # Reverse
            active_command = 0x30
            control_motors(0x30)
            time.sleep(0.5)
            active_command = None
            motors_off()
        elif RFC.value():  # Turn Right
            active_command = 0x40
            control_motors(0x40)
            time.sleep(0.5)
            active_command = None
            motors_off()
        elif RFD.value():  # Stop Motors
            time.sleep(0.5)
            active_command = None
            motors_off()
    else:
        pass
    time.sleep(0.05)

