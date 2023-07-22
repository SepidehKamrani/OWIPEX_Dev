# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Lib V0.5
# Description: Modbus Communication Module
# -----------------------------------------------------------------------------

import struct
import serial
import crcmod.predefined
from threading import Thread
import time
import json


class ModbusClient:
    def __init__(self, device_manager, device_id):
        self.device_manager = device_manager
        self.device_id = device_id
        self.auto_read_enabled = False

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

    def read_radar_sensor(self, register_address):
        return self.device_manager.read_radar_sensor(self.device_id, register_address)


class DeviceManager:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.devices = {}

    def add_device(self, device_id):
        self.devices[device_id] = ModbusClient(self, device_id)

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format):
        function_code = 0x03

        message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)

        crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
        message += struct.pack('<H', crc16)

        self.ser.write(message)

        response = self.ser.read(100)

        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
        if received_crc != calculated_crc:
            raise Exception('CRC error in response')

        data = response[3:-2]
        swapped_data = data[2:4] + data[0:2]
        floating_point = struct.unpack(data_format, swapped_data)[0]

        if floating_point is None:
            raise Exception(f'Error reading register from device {device_id}')

        return floating_point

    def read_radar_sensor(self, device_id, register_address):
        return self.read_register(device_id, register_address, 1, data_format='>H')

    def start_auto_read(self, read_interval=1, output_file='sensor_data.json'):
        def read_loop():
            while True:
                sensor_data = {}
                for device_id, device in self.devices.items():
                    sensor_data[device_id] = {
                        'register': device.read_register(0x0000, 1),
                        'radar_sensor': device.read_radar_sensor(0x0000)
                    }
                with open(output_file, 'w') as f:
                    json.dump(sensor_data, f)
                time.sleep(read_interval)

        Thread(target=read_loop).start()
