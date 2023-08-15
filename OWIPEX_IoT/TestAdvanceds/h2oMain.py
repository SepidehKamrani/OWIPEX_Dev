import logging.handlers
import time
import os
import gpsDataLib
import json

from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep
from FlowCalculation import FlowCalculation

ACCESS_TOKEN = "buyj4qVjjCWd1Zvp4onK"  # Replace this with your actual access token
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)
dev_manager.add_device(device_id=0x03)
# Get devices and read their registers
Radar_Sensor = dev_manager.get_device(device_id=0x01)
Trub_Sensor = dev_manager.get_device(device_id=0x02)
PH_Sensor = dev_manager.get_device(device_id=0x03)
#logging.basicConfig(level=logging.DEBUG)
client = None

from config import *

 #that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    globals().update({key: result[key] for key in result if key in globals()})
    print(result)

# Callback function that will be called when an RPC request is received
def rpc_callback(id, request_body):
    print(request_body)
    method = request_body.get('method')
    if method == 'getTelemetry':
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
    else:
        print('Unknown method: ' + method)


def get_data():
    cpu_usage = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline().replace('', '').replace(',', '.')), 2)
    ip_address = os.popen('''hostname -I''').readline().replace('', '').replace(',', '.')[:-1]
    mac_address = os.popen('''cat /sys/class/net/*/address''').readline().replace('', '').replace(',', '.')
    processes_count = os.popen('''ps -Al | grep -c bash''').readline().replace('', '').replace(',', '.')[:-1]
    swap_memory_usage = os.popen("free -m | grep Swap | awk '{print ($3/$2)*100}'").readline().replace('', '').replace(',', '.')[:-1]
    ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().replace('', '').replace(',', '.')[:-1])
    st = os.statvfs('/')
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    boot_time = os.popen('uptime -p').read()[:-1]
    avg_load = (cpu_usage + ram_usage) / 2
    
    #calculate tank volumes

    attributes = {
        'ip_address': ip_address,
        'macaddress': mac_address
    }
    telemetry = {key: globals()[key] for key in telemetry_keys if key in globals()}

    # Adding static data
    telemetry.update({
        'cpu_usage': cpu_usage,
        'processes_count': processes_count,
        'disk_usage': used,
        'RAM_usage': ram_usage,
        'swap_memory_usage': swap_memory_usage,
        'boot_time': boot_time,
        'avg_load': avg_load
    })
    
    print(attributes, telemetry)
    return attributes, telemetry

def sync_state(result, exception=None):
    global powerButton
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        period = result.get('shared', {'powerButton': False})['powerButton']

class GPSHandler:
    def __init__(self):
        pass  # Hier können Sie Initialisierungscode hinzufügen, falls benötigt.

    def fetch_and_display_data(self, callGpsSwitch):
        if callGpsSwitch:
            timestamp, latitude, longitude, altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)
            if timestamp is not None:
                # Ausgabe der GPS-Daten für Debugging-Zwecke
                print(f"Zeitstempel: {timestamp}")
                print(f"Breitengrad: {latitude}")
                print(f"Längengrad: {longitude}")
                print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
                return timestamp, latitude, longitude, altitude
            else:
                print("Keine GPS-Daten verfügbar.", callGpsSwitch)
                return None, None, None, None
        else:
            print("GPS-Aufruf ist deaktiviert.", callGpsSwitch)
            return None, None, None, None
        
class TurbidityHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Hier übergeben Sie die Trub_Sensor-Instanz

    def fetch_and_display_data(self, turbiditySensorActive):
        if turbiditySensorActive:
            measuredTurbidity_telem = self.sensor.read_register(start_address=0x0001, register_count=2)
            tempTruebSens = self.sensor.read_register(start_address=0x0003, register_count=2)
            print(f'Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')
            return measuredTurbidity_telem, tempTruebSens
        else:
            print("TruebOFF", turbiditySensorActive)
            return None, None      

class PHHandler:
    def __init__(self, sensor):
        self.sensor = sensor  # Hier übergeben Sie die PH_Sensor-Instanz
        self.slope = 1  # Anfangswert, wird durch Kalibrierung aktualisiert
        self.intercept = 0  # Anfangswert, wird durch Kalibrierung aktualisiert

    def fetch_and_display_data(self):
        raw_ph_value = self.sensor.read_register(start_address=0x0001, register_count=2)
        measuredPHValue_telem = self.correct_ph_value(raw_ph_value)
        
        temperaturPHSens_telem = self.sensor.read_register(start_address=0x0003, register_count=2)
        
        print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}')
        return measuredPHValue_telem, temperaturPHSens_telem

    def correct_ph_value(self, raw_value):
        return self.slope * raw_value + self.intercept

    def calibrate(self, high_ph_value, low_ph_value, measured_high, measured_low):
        """
        Kalibriert den pH-Sensor mit gegebenen Hoch- und Tiefwerten.

        :param high_ph_value: Bekannter pH-Wert der High-Kalibrierlösung (z.B. 10)
        :param low_ph_value: Bekannter pH-Wert der Low-Kalibrierlösung (z.B. 7)
        :param measured_high: Gemessener Wert des Sensors in der High-Kalibrierlösung
        :param measured_low: Gemessener Wert des Sensors in der Low-Kalibrierlösung
        """
        # Berechnung der Steigung und des y-Achsenabschnitts
        self.slope = (high_ph_value - low_ph_value) / (measured_high - measured_low)
        self.intercept = high_ph_value - self.slope * measured_high

class FlowRateHandler:
    def __init__(self, radar_sensor, flow_calculator, zero_reference):
        self.radar_sensor = radar_sensor
        self.flow_calculator = flow_calculator
        self.zero_reference = zero_reference

    def fetch_and_calculate(self):
        measured_air_distance = self.radar_sensor.read_radar_sensor(register_address=0x0001)
        
        if measured_air_distance is not None:
            water_level = self.zero_reference - measured_air_distance

            # Berechne den Durchfluss für eine bestimmte Wasserhöhe
            flow_rate = self.flow_calculator.calculate_flow_rate(water_level)
            print(f"Flow Rate (m3/h): {flow_rate}")

            # Konvertiere den Durchfluss in verschiedene Einheiten
            flow_rate_l_min = self.flow_calculator.convert_to_liters_per_minute(flow_rate)
            flow_rate_l_h = self.flow_calculator.convert_to_liters_per_hour(flow_rate)
            flow_rate_m3_min = self.flow_calculator.convert_to_cubic_meters_per_minute(flow_rate)

            return {
                "water_level": water_level,
                "flow_rate": flow_rate,
                "flow_rate_l_min": flow_rate_l_min,
                "flow_rate_l_h": flow_rate_l_h,
                "flow_rate_m3_min": flow_rate_m3_min
            }
        else:
            return None
        
def main():
    #def Global Variables for Main Funktion
    global client, tempTruebSens, calibratePH, gemessener_low_wert, gemessener_high_wert, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw

    ph_high_delay_start_time = None
    ph_low_delay_start_time = None

    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['powerButton'], callback=sync_state)

    # Pfad zur Kalibrierungsdatei
    calibration_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "calibration_data.json")
    # Erstelle eine Instanz der FlowCalculation-Klasse
    flow_calc = FlowCalculation(calibration_file_path)
    # Hole den 0-Referenzwert
    zero_ref = flow_calc.get_zero_reference()
    print(f"Zero Reference: {zero_ref}")

    # Request shared attributes
    client.request_attributes(shared_keys=shared_attributes_keys, callback=attribute_callback)
    # Subscribe to individual attributes using the defined lists
    for attribute in machine_attributes_keys + ph_attributes_keys + turbidity_attributes_keys + radar_attributes_keys + alarm_attributes_keys + gps_attributes_keys:
        client.subscribe_to_attribute(attribute, attribute_callback)

    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    ph_handler = PHHandler(PH_Sensor)
    turbidity_handler = TurbidityHandler(Trub_Sensor)
    flow_handler = FlowRateHandler(Radar_Sensor, flow_calc, zero_ref)
    flow_data = flow_handler.fetch_and_calculate()

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)

        if flow_data:
            print(f"Water Level: {flow_data['water_level']} mm")
            print(f"Flow Rate: {flow_data['flow_rate']} m3/h")
            print(f"Flow Rate (Liters per Minute): {flow_data['flow_rate_l_min']} L/min")
            print(f"Flow Rate (Liters per Hour): {flow_data['flow_rate_l_h']} L/h")
            print(f"Flow Rate (Cubic Meters per Minute): {flow_data['flow_rate_m3_min']} m3/min")


        if pumpRelaySw:
            pumpRelaySwSig = False
        else:
            pumpRelaySwSig = True
        if co2RelaisSw:
            co2RelaisSwSig = False
        else: 
            co2RelaisSwSig = True
        if co2HeatingRelaySw:
            co2HeatingRelaySwSig = False
        else: 
            co2HeatingRelaySwSig = True

        #GPS DATA 
        gps_handler = GPSHandler()
        gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight = gps_handler.fetch_and_display_data(callGpsSwitch) 

        if powerButton:
            try:
                
                if calibratePH:
                    ph_handler.calibrate(high_ph_value=10, low_ph_value=7, measured_high=gemessener_high_wert, measured_low=gemessener_low_wert)
                    calibratePH = False
                else:
                    measuredPHValue_telem, temperaturPHSens_telem = ph_handler.fetch_and_display_data()  
                    measuredTurbidity_telem, tempTruebSens = turbidity_handler.fetch_and_display_data(turbiditySensorActive)
            except Exception as e:
                print(f"An error occurred: {e}")
           
# Main Logic
            if autoSwitch:
                print("automode ON", autoSwitch)
                print(f'Radar Measuring Height: {waterLevelHeight_telem}')

                # Verzögerungslogik für niedrigen pH-Wert
                if measuredPHValue_telem < minimumPHValueStop:
                    if ph_low_delay_start_time is None:
                        ph_low_delay_start_time = time.time()  # Zeitpunkt festlegen, wenn die Bedingung zum ersten Mal wahr wird
                    elif time.time() - ph_low_delay_start_time >= ph_low_delay_duration:
                        pumpRelaySw = False
                        co2RelaisSw = False
                        co2HeatingRelaySw = False
                        autoSwitch = False
                        ph_low_delay_start_time = None
                else:
                    ph_low_delay_start_time = None  # Zurücksetzen der Verzögerung, wenn die Bedingung nicht mehr wahr ist

                # Verzögerungslogik für hohen pH-Wert
                if measuredPHValue_telem > maximumPHValue:
                    if ph_high_delay_start_time is None:
                        ph_high_delay_start_time = time.time()  # Zeitpunkt festlegen, wenn die Bedingung zum ersten Mal wahr wird
                    elif time.time() - ph_high_delay_start_time >= ph_high_delay_duration:
                        pumpRelaySw = False
                        co2RelaisSw = False
                        co2HeatingRelaySw = False
                        autoSwitch = False
                        ph_high_delay_start_time = None
                else:
                    ph_high_delay_start_time = None  # Zurücksetzen der Verzögerung, wenn die Bedingung nicht mehr wahr ist

                # Standardlogik (wird nur ausgeführt, wenn der Auto-Modus noch aktiv ist)
                if autoSwitch:
                    if measuredPHValue_telem >= minimumPHValue and measuredPHValue_telem <= maximumPHValue:
                        pumpRelaySw = True
                        co2RelaisSw = False
                    elif measuredPHValue_telem > maximumPHValue:
                        pumpRelaySw = False
                        co2RelaisSw = True
                        co2HeatingRelaySw = True
                    elif measuredPHValue_telem < minimumPHValue:
                        pumpRelaySw = False
                        co2RelaisSw = False
                        co2HeatingRelaySw = False        
            else:
                messuredRadar_Air_telem = Radar_Sensor.read_radar_sensor(register_address=0x0001)
                print("automode OFF", autoSwitch)
        else:
            print("Power Switch OFF.", powerButton)

        time.sleep(2)


if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")
