# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Calibration Tool V0.1
# Description: Calibration program for water level sensor and flow rate
# -----------------------------------------------------------------------------

print("""
-----------------------------------------------------------------------------
Company: KARIM Technologies
Author: Sayed Amir Karim
Copyright: 2023 KARIM Technologies

License: All Rights Reserved

Module: Calibration Tool V0.1
Description: Calibration program for water level sensor and flow rate
-----------------------------------------------------------------------------
""")

from tqdm import tqdm
from modbus_lib import DeviceManager
import time
import json
from gpiocontrol import GPIOControl

class Calibration:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.radar_sensor = device_manager.get_device(device_id=0x01)
        self.pump = GPIOControl(7) # assuming your pump is connected to GPIO pin 7
        self.calibration_data = []
        self.pump.set_direction('out')
        self.pump.set_value('1') # Ensure pump is off at the start

    def fill_tank(self):
        print("Sind Sie bereit, den Tank zu füllen? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            self.pump.set_value('0')  # Turn on pump
            print("Bitte warten Sie, bis das Wasser aus dem Ablauf läuft, und drücken Sie dann Enter.")
            input()
            self.pump.set_value('1')  # Turn off pump
            print("Bitte warten Sie 3 Minuten, bis sich das System eingependelt hat.")
            for i in tqdm(range(180)):
                time.sleep(1)
            zero_point = self.radar_sensor.read_radar_sensor(register_address=0x0001)
            print(f'Nullpunkt: {zero_point} mm')
            self.calibration_data.append({
                'zero_point': zero_point
            })
            self.save_calibration_data()
        else:
            print("Bitte bereiten Sie sich vor und starten Sie das Programm erneut, wenn Sie bereit sind.")
            exit()

    def start_calibration(self):
        print("\nWARNUNG: Der Kalibrierungsprozess wird nun gestartet. Die Pumpe wird eingeschaltet.")
        print("Sind Sie bereit, den Kalibrierungsprozess zu starten? (yes/no)")
        answer = input().lower()
        if answer == 'yes':
            self.pump.set_value('0')  # Turn on pump
        else:
            print("Kalibrierungsprozess wurde nicht gestartet. Bitte bereiten Sie sich vor und starten Sie das Programm erneut, wenn Sie bereit sind.")
            exit()

        vessel_size = float(input("Bitte geben Sie die Größe des Kalibriergefäßes in Litern ein: "))
        
        while True:
            print("Bitte stellen Sie die Pumpe auf eine höhere Durchflussrate und bestätigen Sie mit Enter.")
            input()

            print("Bitte warten Sie 3 Minuten, bis sich das System eingependelt hat.")
            for i in tqdm(range(180)):
                time.sleep(1)

            water_height = self.radar_sensor.read_radar_sensor(register_address=0x0001)
            print(f'Wasserhöhe: {water_height} mm')

            fill_time = float(input("Bitte geben Sie die Zeit ein, die benötigt wurde, um das Kalibriergefäß zu füllen (in Sekunden): "))
            flow_rate = (vessel_size / fill_time) * 60

            self.calibration_data.append({
                'water_height': water_height,
                'flowRate': flow_rate
            })

            should_continue = input("Möchten Sie weitermachen? (yes/no): ")
            if should_continue.lower() != 'yes':
                break

        self.save_calibration_data()

    def save_calibration_data(self):
        with open('calibration_data.json', 'w') as outfile:
            json.dump(self.calibration_data, outfile)
        print("Kalibrierungsdaten erfolgreich gespeichert!")
        print(self.calibration_data)

if __name__ == "__main__":
    dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
    dev_manager.add_device(device_id=0x01)
    calibrator = Calibration(dev_manager)
    calibrator.fill_tank()
    calibrator.start_calibration()
