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
from time import sleep

# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Add devices
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)

# Get devices and read their registers
PH_Sensor = dev_manager.get_device(device_id=0x01)
Trub_Sensor = dev_manager.get_device(device_id=0x02)

try:
    # Start auto read
    PH_Sensor.auto_read_registers(start_address=0x0003, register_count=2)
    Trub_Sensor.auto_read_registers(start_address=0x0003, register_count=2)

    # Sleep for 10 seconds
    sleep(10)

    # Stop auto read
    PH_Sensor.stop_auto_read()
    Trub_Sensor.stop_auto_read()

except Exception as e:
    print(f"An error occurred: {e}")
