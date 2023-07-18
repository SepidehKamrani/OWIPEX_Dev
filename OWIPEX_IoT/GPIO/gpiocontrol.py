# gpiocontrol.py
import os
import sys

class GPIOControl:
    def __init__(self, gpio_num):
        if gpio_num > 7:
            raise ValueError("GPIO number must be between 0 and 7")

        self.cnt = 496 + gpio_num
        self.cnt2 = 504 + gpio_num

        # Exportiere die GPIOs, falls noch nicht geschehen
        if not os.path.exists(f"/sys/class/gpio/gpio{self.cnt}"):
            os.system(f"echo {self.cnt} > /sys/class/gpio/export")

        if not os.path.exists(f"/sys/class/gpio/gpio{self.cnt2}"):
            os.system(f"echo {self.cnt2} > /sys/class/gpio/export")

        # Setze den aktiven Wert
        os.system(f"echo 1 > /sys/class/gpio/gpio{self.cnt}/active_low")

    def set_direction(self, direction):
        if direction not in ['in', 'out']:
            raise ValueError("Direction must be either 'in' or 'out'")
        
        os.system(f"echo in > /sys/class/gpio/gpio{self.cnt2}/direction")
        os.system(f"echo {direction} > /sys/class/gpio/gpio{self.cnt}/direction")

    def set_value(self, value):
        if value not in ['0', '1']:
            raise ValueError("Value must be either '0' or '1'")
        
        os.system(f"echo {value} > /sys/class/gpio/gpio{self.cnt}/value")

    def read_value(self):
        return os.popen(f"cat /sys/class/gpio/gpio{self.cnt2}/value").read().strip()
