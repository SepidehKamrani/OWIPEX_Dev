# main.py
from gpiocontrol import GPIOControl

# Erstellt ein GPIOControl-Objekt für GPIO 4
gpio = GPIOControl(4)

# Richtung auf "out" setzen
gpio.set_direction('out')

# Wert auf "1" setzen
gpio.set_value('1')

# Wert lesen
value = gpio.read_value()
print(value)
