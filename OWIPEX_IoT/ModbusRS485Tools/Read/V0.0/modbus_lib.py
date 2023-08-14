# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Modbus Lib V0.2
# Description: Modbus Communication Module
# -----------------------------------------------------------------------------

import struct
import serial
import crcmod.predefined
from threading import Thread, Lock
from time import sleep
from collections import deque

MAX_RETRIES = 3  # Maximale Wiederholungsversuche bei Kommunikationsfehlern


def validate_response_length(response, expected_length):
    if len(response) < expected_length:
        raise Exception(f"Unerwartete Antwortlänge. Erwartet: {expected_length} Bytes, erhalten: {len(response)} Bytes.")


class ModbusClient:
    def __init__(self, device_manager, device_id, read_interval=1, buffer_size=10):
        self.device_manager = device_manager
        self.device_id = device_id
        self.buffer = deque(maxlen=buffer_size)
        self.lock = Lock()
        self.read_interval = read_interval
        self.stop_reading = False
        self.thread = Thread(target=self._read_loop)
        self.thread.start()

    def _read_loop(self):
        while not self.stop_reading:
            value = self.read_radar_sensor(0x0001)  # Für den Radarsensor
            with self.lock:
                self.buffer.append(value)
            sleep(self.read_interval)

    def get_average_value(self):
        with self.lock:
            if not self.buffer:
                return None
            return sum(self.buffer) / len(self.buffer)

    def stop_auto_read(self):
        self.stop_reading = True
        self.thread.join()

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

    def add_device(self, device_id, read_interval=1, buffer_size=10):
        self.devices[device_id] = ModbusClient(self, device_id, read_interval, buffer_size)

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def read_register(self, device_id, start_address, register_count, data_format='>f'):
        for _ in range(MAX_RETRIES):
            try:
                function_code = 0x03
                expected_response_length = 5 + 2 * register_count

                message = struct.pack('>B B H H', device_id, function_code, start_address, register_count)
                crc16 = crcmod.predefined.mkPredefinedCrcFun('modbus')(message)
                message += struct.pack('<H', crc16)

                self.ser.write(message)
                response = self.ser.read(expected_response_length)

                validate_response_length(response, expected_response_length)

                received_crc = struct.unpack('<H', response[-2:])[0]
                calculated_crc = crcmod.predefined.mkPredefinedCrcFun('modbus')(response[:-2])
                if received_crc != calculated_crc:
                    raise Exception('CRC error in response')

                data = response[3:-2]
                swapped_data = data[2:4] + data[0:2]
                return struct.unpack(data_format, swapped_data)[0]
            except Exception as e:
                print(f"Error during communication: {e}")
        raise Exception(f"Failed to read register from device {device_id} after {MAX_RETRIES} attempts.")

    def read_radar_sensor(self, device_id, register_address):
        return self.read_register(device_id, register_address, 1, data_format='>H')
