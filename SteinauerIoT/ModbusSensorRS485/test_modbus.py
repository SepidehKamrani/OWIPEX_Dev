# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Test Modbus Lib V0.5
# Description: Modbus Communication Test Script
# -----------------------------------------------------------------------------

# This script tests the functions of the Modbus library by KARIM Technologies.
# Two sensors are connected to the same port, and their temperature values, as well as another value, are read.

from modbus_lib import DeviceManager

# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Add devices
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)

# Get devices and read their registers
sensor1 = dev_manager.get_device(device_id=0x01)
sensor2 = dev_manager.get_device(device_id=0x02)

# Read temperatures
temp1 = sensor1.read_register(start_address=0x0003, register_count=2)
temp2 = sensor2.read_register(start_address=0x0003, register_count=2)
print(f'Temperature 1: {temp1}, Temperature 2: {temp2}')

# Read other values
other_value1 = sensor1.read_register(start_address=0x0005, register_count=2)
other_value2 = sensor2.read_register(start_address=0x0005, register_count=2)
print(f'Other Value 1: {other_value1}, Other Value 2: {other_value2}')

# To stop auto read
# dev_manager.auto_read = False
