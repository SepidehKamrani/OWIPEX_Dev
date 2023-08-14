# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Lib V0.4
# Description: Modbus Communication Module with synchronized access and temperature readings
# -----------------------------------------------------------------------------

import struct
import serial
import crcmod.predefined
from threading import Lock
from time import sleep
from collections import deque

def validate_response_length(response, expected_length):
    if len(response) < expected_length:
        raise Exception(f"Unerwartete Antwortlänge. Erwartet: {expected_length} Bytes, erhalten: {len(response)} Bytes.")

class ModbusClient:
    def __init__(self, device_manager, device_id, read_interval=5, buffer_size=10):
        self.device_manager = device_manager
        self.device_id = device_id
        self.buffers = [deque(maxlen=buffer_size) for _ in range(2)]  # Zwei Puffer für Messwert und Temperatur
        self.lock = Lock()
        self.read_interval = read_interval
        self.stop_reading = False

    def start_auto_read(self):
        self.stop_reading = False
        while not self.stop_reading:
            value = self.read_register(0x0001, 2)
            temperature = self.read_register(0x0003, 2)  # Lesen des Temperaturwertes
            with self.lock:
                self.buffers[0].append(value)
                self.buffers[1].append(temperature)  # Temperatur in den zweiten Puffer hinzufügen
            sleep(self.read_interval)

    def get_average_value(self, index=0):
        with self.lock:
            if not self.buffers[index]:
                return None
            return sum(self.buffers[index]) / len(self.buffers[index])

    def read_register(self, start_address, register_count, data_format='>f'):
        return self.device_manager.read_register(self.device_id, start_address, register_count, data_format)

    def read_radar_sensor(self, register_address):
        return self.read_register(device_id, register_address, 1, data_format='>H')

class DeviceManager:
    def __init__(self, port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE if parity == 'N' else serial.PARITY_EVEN if parity == 'E' else serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS if bytesize == 8 else serial.SEVENBITS,
            timeout=timeout
        )
        self.devices = {}
        self.bus_lock = Lock()  # Lock to ensure synchronized access to the RS485 bus

    def add_device(self, device_id, read_interval=5, buffer_size=10):
        self.devices[device_id] = ModbusClient(self, device_id, read_interval, buffer_size)
        return self.devices[device_id]

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format='>f'):
        with self.bus_lock:
            function_code = 0x03
            message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
            crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
            message += struct.pack('<H', crc16)
            self.ser.write(message)
            sleep(0.05)  # small delay for safety
            response = self.ser.read(100)
            validate_response_length(response, 7)
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
