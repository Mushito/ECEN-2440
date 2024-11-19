# Kiran Jojare
# University of Colorado Boulder
# Graduate Student, Department of Electrical Engineering, Embedded Systems Specialization

# Simplified Seesaw library for interfacing with Gamepad QT using Raspberry Pi Pico
# Based on MicroPython Port Copyright (c) 2019 by Mihai Dinculescu
# and CircuitPython Implementation Copyright (c) 2017 by Dean Miller for Adafruit Industries


# Enhanced Seesaw library with added error checking for robust debugging

# Enhanced Seesaw library with added error checking for robust debugging
from machine import I2C, Pin
import struct
import time

STATUS_BASE = const(0x00)
_GPIO_BASE = const(0x01)
_ADC_BASE = const(0x09)
_STATUS_HW_ID = const(0x01)
_STATUS_SWRST = const(0x7F)
_GPIO_DIRSET_BULK = const(0x02)
_GPIO_DIRCLR_BULK = const(0x03)
_GPIO_BULK = const(0x04)
_GPIO_BULK_SET = const(0x05)
_GPIO_BULK_CLR = const(0x06)
_GPIO_PULLENSET = const(0x0B)
_GPIO_PULLENCLR = const(0x0C)
_ADC_CHANNEL_OFFSET = const(0x07)
_SAMD09_HW_ID_CODE = const(0x55)
_HW_ID_CODE = const(0x87)

class Seesaw:
   INPUT = const(0x00)
   OUTPUT = const(0x01)
   INPUT_PULLUP = const(0x02)
   INPUT_PULLDOWN = const(0x03)
  
   # Define the pin mappings directly within the Seesaw class
   class Pinmap:
       """Pin mappings for Adafruit ATtinyx16 Breakout with seesaw"""

       # The pins capable of analog output
       analog_pins = (0, 1, 2, 3, 4, 5, 14, 15, 16)

       # The effective bit resolution of the PWM pins
       pwm_width = 16  # we dont actually use all 16 bits but whatever

       # The pins capable of PWM output
       pwm_pins = (0, 1, 7, 11, 16)  # 8 bit PWM mode
       pwm_pins += (4, 5, 6)  # 16 bit PWM mode

       # No pins on this board are capable of touch input
       touch_pins = ()

   def __init__(self, i2c, addr=0x49):
       self.i2c = i2c
       self.addr = addr
       self.pin_mapping = self.Pinmap
       self.chip_id = None
       try:
           self.sw_reset()
       except Exception as e:
           print("Seesaw initialization failed:", e)
           raise

   def sw_reset(self):
       self._write8(STATUS_BASE, _STATUS_SWRST, 0xFF)
       time.sleep(0.5)
       self.chip_id = self._read8(STATUS_BASE, _STATUS_HW_ID)
       if self.chip_id != _HW_ID_CODE:
            error_msg = f"Hardware ID mismatch: expected 0x{_HW_ID_CODE:02x}, got 0x{self.chip_id:02x}"
            print(error_msg)
            raise ValueError(error_msg)

   def _write8(self, reg_base, reg, value):
       self._write(reg_base, reg, bytearray([value]))

   def _read8(self, reg_base, reg):
       ret = bytearray(1)
       self._read(reg_base, reg, ret)
       return ret[0]

   def _read(self, reg_base, reg, buf, delay=.005):
       self._write(reg_base, reg)
       time.sleep(delay)
       self.i2c.readfrom_into(self.addr, buf)

   def _write(self, reg_base, reg, buf=None):
       full_buffer = bytearray([reg_base, reg])
       if buf is not None:
           full_buffer += buf
       self.i2c.writeto(self.addr, full_buffer)

   def pin_mode(self, pin, mode):
       if pin >= 32:
           self.pin_mode_bulk_b(1 << (pin - 32), mode)
       else:
           self.pin_mode_bulk(1 << pin, mode)

   def pin_mode_bulk_b(self, pins, mode):
       self._pin_mode_bulk_x(8, 4, pins, mode)
          
   def _pin_mode_bulk_x(self, capacity, offset, pins, mode):
       cmd = bytearray(capacity)
       cmd[offset:offset+4] = struct.pack(">I", pins)
       if mode == self.OUTPUT:
           self._write(_GPIO_BASE, _GPIO_DIRSET_BULK, cmd)
       elif mode == self.INPUT:
           self._write(_GPIO_BASE, _GPIO_DIRCLR_BULK, cmd)
           self._write(_GPIO_BASE, _GPIO_PULLENCLR, cmd)
       elif mode == self.INPUT_PULLUP:
           self._write(_GPIO_BASE, _GPIO_DIRCLR_BULK, cmd)
           self._write(_GPIO_BASE, _GPIO_PULLENSET, cmd)
           self._write(_GPIO_BASE, _GPIO_BULK_SET, cmd)
       elif mode == self.INPUT_PULLDOWN:
           self._write(_GPIO_BASE, _GPIO_DIRCLR_BULK, cmd)
           self._write(_GPIO_BASE, _GPIO_PULLENSET, cmd)
           self._write(_GPIO_BASE, _GPIO_BULK_CLR, cmd)
       else:
           raise ValueError("Invalid pin mode")

   def pin_mode_bulk(self, pins=0x10067, mode=None):
       if mode is None:
           mode = self.INPUT_PULLUP
       self._pin_mode_bulk_x(4, 0, pins, mode)
  
   def digital_read_bulk(self, pins=0x10067, delay=0.008):
       buf = bytearray(4)
       self._read(_GPIO_BASE, _GPIO_BULK, buf, delay=delay)
       try:
           ret = struct.unpack(">I", buf)[0]
       except OverflowError:
           buf[0] = buf[0] & 0x3F
           ret = struct.unpack(">I", buf)[0]
       return ret & pins

   def analog_read(self, pin, delay=0.008):
       buf = bytearray(2)
       if pin not in self.pin_mapping.analog_pins:
           raise ValueError("Invalid ADC pin")
       if self.chip_id == _SAMD09_HW_ID_CODE:
           offset = self.pin_mapping.analog_pins.index(pin)
       else:
           offset = pin
       self._read(_ADC_BASE, _ADC_CHANNEL_OFFSET + offset, buf, delay)
       ret = struct.unpack(">H", buf)[0]
       return ret
