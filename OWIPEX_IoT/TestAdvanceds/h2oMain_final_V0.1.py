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

def main():
    #def Global Variables for Main Funktion
    global client, autoSwitch, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw

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

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        messuredRadar_Air_telem = Radar_Sensor.read_radar_sensor(register_address=0x0001)
        
        if messuredRadar_Air_telem is not None:
            waterLevelHeight_telem = zero_ref - messuredRadar_Air_telem

        
        # Berechne den Durchfluss für eine bestimmte Wasserhöhe
        water_level = waterLevelHeight_telem  # in mm
        flow_rate = flow_calc.calculate_flow_rate(water_level)
        print(f"Flow Rate (m3/h): {flow_rate}")

        # Konvertiere den Durchfluss in verschiedene Einheiten
        flow_rate_l_min = flow_calc.convert_to_liters_per_minute(flow_rate)
        flow_rate_l_h = flow_calc.convert_to_liters_per_hour(flow_rate)
        flow_rate_m3_min = flow_calc.convert_to_cubic_meters_per_minute(flow_rate)

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
        #Call GPS Data. Can be called even whitout power Switch. 
        if callGpsSwitch:
            # Abrufen und Verarbeiten der GPS-Daten (mit einem Timeout von 10 Sekunden)
            timestamp, latitude, longitude, altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)

            if timestamp is not None:
                gpsTimestamp = timestamp
                gpsLatitude = latitude
                gpsLongitude = longitude
                gpsHeight = altitude
                # Ausgabe der GPS-Daten für Debugging-Zwecke
                print(f"Zeitstempel: {timestamp}")
                print(f"Breitengrad: {latitude}")
                print(f"Längengrad: {longitude}")
                print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")

            else:
                print("Keine GPS-Daten verfügbar.", callGpsSwitch)
                
        else:
            print("GPS-Aufruf ist deaktiviert.", callGpsSwitch)  

        if powerButton:
            try:
                
                measuredPHValue_telem = PH_Sensor.read_register(start_address=0x0001, register_count=2)
                temperaturPHSens_telem = PH_Sensor.read_register(start_address=0x0003, register_count=2)
                print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}')

                if turbiditySensorActive:
                    measuredTurbidity_telem = Trub_Sensor.read_register(start_address=0x0001, register_count=2)
                    tempTruebSens = Trub_Sensor.read_register(start_address=0x0003, register_count=2)
                    print(f'Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')   
                else:
                    print("TruebOFF", turbiditySensorActive)
 
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
