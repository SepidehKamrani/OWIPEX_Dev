import logging.handlers
import time
import os
import gpsDataLib
import json

from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep
from ph_control import PHControl
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

# Global Variables
#Machine 
calculatedFlowRate = 1.0
powerButton = False
autoSwitch = False
callGpsSwitch = False
co2RelaisSw = False
pumpRelaySw = False
co2HeatingRelaySw = False
co2RelaisSwSig = False
pumpRelaySwSig = False
co2HeatingRelaySwSig = False
#PH
minimumPHValue = ""
maximumPHValue = ""
PHValueOffset = ""
temperaturPHSens_telem = 0
measuredPHValue_telem = 0
#Trueb
measuredTurbidity = ""
maximumTurbidity = ""
turbiditySensorActive = ""
turbidityOffset = ""
measuredTurbidity_telem = 0
#Radar
waterLevelHeight = 1.0
waterLevelHeight_telem = 2.0
messuredRadar_Air_telem = 1 
radarSensorActive = False
radarSensorOffset = 0.0
#Flow
flow_rate_l_min = 20.0
flow_rate_l_h = 20.0
flow_rate_m3_min = 20.0
#GPS
gpsTimestamp = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsHeight = 1.0


# Callback function that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    global minimumPHValue, maximumPHValue, PHValueOffset, maximumTurbidity, turbiditySensorActive, turbidityOffset, radarSensorActive, radarOffset, autoSwitch, callGpsSwitch, powerButton, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw
    print(result)
    #machine
    if 'autoSwitch' in result:
        autoSwitch = result['autoSwitch']
    if 'callGpsSwitch' in result:
        callGpsSwitch = result['callGpsSwitch']
    if 'minimumPHValue' in result:
        minimumPHValue = result['minimumPHValue']
    if 'maximumPHValue' in result:
        maximumPHValue = result['maximumPHValue']
    if 'PHValueOffset' in result:
        PHValueOffset = result['PHValueOffset']
    if 'maximumTurbidity' in result:
        maximumTurbidity = result['maximumTurbidity']
    if 'turbiditySensorActive' in result:
        turbiditySensorActive = result['turbiditySensorActive']
    if 'turbidityOffset' in result:
        turbidityOffset = result['turbidityOffset']
    if 'radarSensorActive' in result:
        radarSensorActive = result['radarSensorActive']
    if 'radarOffset' in result:
        radarOffset = result['radarOffset']
    if 'powerButton' in result:
        powerButton = result['powerButton']   
    if 'co2RelaisSw' in result:
        co2RelaisSw = result['co2RelaisSw']   
    if 'pumpRelaySw' in result:
        pumpRelaySw = result['pumpRelaySw']
    if 'co2HeatingRelaySw' in result:
        co2HeatingRelaySw = result['co2HeatingRelaySw']    
        
         
    

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
    global temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSwSig 
    cpu_usage = round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline().replace('\n', '').replace(',', '.')), 2)
    ip_address = os.popen('''hostname -I''').readline().replace('\n', '').replace(',', '.')[:-1]
    mac_address = os.popen('''cat /sys/class/net/*/address''').readline().replace('\n', '').replace(',', '.')
    processes_count = os.popen('''ps -Al | grep -c bash''').readline().replace('\n', '').replace(',', '.')[:-1]
    swap_memory_usage = os.popen("free -m | grep Swap | awk '{print ($3/$2)*100}'").readline().replace('\n', '').replace(',', '.')[:-1]
    ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().replace('\n', '').replace(',', '.')[:-1])
    st = os.statvfs('/')
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    boot_time = os.popen('uptime -p').read()[:-1]
    avg_load = (cpu_usage + ram_usage) / 2
    
    #calculate tank volumes


    attributes = {
        'ip_address': ip_address,
        'macaddress': mac_address

    }
    telemetry = {
        #hardware PC
        'cpu_usage': cpu_usage,
        'processes_count': processes_count,
        'disk_usage': used,
        'RAM_usage': ram_usage,
        'swap_memory_usage': swap_memory_usage,
        'boot_time': boot_time,
        'avg_load': avg_load,
        #device 
        'calculatedFlowRate': calculatedFlowRate,
        'waterLevelHeight_telem': waterLevelHeight_telem,
        'measuredTurbidity_telem': measuredTurbidity_telem,
        'co2RelaisSwSig': co2RelaisSwSig,
        'co2HeatingRelaySwSig': co2HeatingRelaySwSig,
        'pumpRelaySwSig': pumpRelaySwSig,
  
        #PH Sens
        'measuredPHValue_telem': measuredPHValue_telem,
        'temperaturPHSens_telem': temperaturPHSens_telem,
        'gpsTimestamp': gpsTimestamp,
        'gpsLatitude': gpsLatitude,
        'gpsLongitude': gpsLongitude,
        'gpsHeight': gpsHeight,

        'messuredRadar_Air_telem': messuredRadar_Air_telem,

        'flow_rate_l_min': flow_rate_l_min,
        'flow_rate_l_h': flow_rate_l_h,
        'flow_rate_m3_min': flow_rate_m3_min


        
        
        

    }
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
    global client, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem, flow_rate_l_min, flow_rate_l_h, flow_rate_m3_min, co2RelaisSwSig, co2HeatingRelaySwSig, pumpRelaySwSig, co2RelaisSw, co2HeatingRelaySw, pumpRelaySw
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    client.request_attributes(shared_keys=['powerButton'], callback=sync_state)

    # Erstellt ein PHControl-Objekt
    ph_control = PHControl(min_ph=5.0, max_ph=8.0, check_timer=5, on_delay_timer=5)
    ph_control.set_pump_delay(1)
    
    
    # Pfad zur Kalibrierungsdatei
    calibration_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "calibration_data.json")

    # Erstelle eine Instanz der FlowCalculation-Klasse
    flow_calc = FlowCalculation(calibration_file_path)

    # Hole den 0-Referenzwert
    zero_ref = flow_calc.get_zero_reference()
    print(f"Zero Reference: {zero_ref}")



    # Request shared attributes
    client.request_attributes(shared_keys=['minimumPHValue', 'maximumPHValue', 'PHValueOffset', 'maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'radarSensorActive', 'alarmActiveMachine', 'alarmMessageMachine', 'resetAlarm', 'autoSwitch', 'callGpsSwitch', 'powerButton', 'co2RelaisSwSig'], callback=attribute_callback)
    
    # Subscribe to individual attributes
    #machine
    client.subscribe_to_attribute("", attribute_callback)
    client.subscribe_to_attribute("autoSwitch", attribute_callback)
    client.subscribe_to_attribute('powerButton', attribute_callback)
    client.subscribe_to_attribute("co2RelaisSw", attribute_callback)
    client.subscribe_to_attribute("pumpRelaySw", attribute_callback)
    client.subscribe_to_attribute("co2HeatingRelaySw", attribute_callback)
    #PH
    client.subscribe_to_attribute('minimumPHValue', attribute_callback)
    client.subscribe_to_attribute('maximumPHValue', attribute_callback)
    client.subscribe_to_attribute('PHValueOffset', attribute_callback)
    #Tuerb
    client.subscribe_to_attribute('maximumTurbidity', attribute_callback)
    client.subscribe_to_attribute('turbiditySensorActive', attribute_callback)
    client.subscribe_to_attribute('turbidityOffset', attribute_callback)
    #Radar
    client.subscribe_to_attribute('radarSensorActive', attribute_callback)
     
    'Alarm'
    client.subscribe_to_attribute('alarmActiveMachine', attribute_callback)
    client.subscribe_to_attribute('alarmMessageMachine', attribute_callback)
    client.subscribe_to_attribute('resetAlarm', attribute_callback)
    #GPS
    client.subscribe_to_attribute("callGpsSwitch", attribute_callback)
    

    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        
        waterLevelHeight_telem = zero_ref - messuredRadar_Air_telem
        ph_control.set_measured_ph(measuredPHValue_telem)
        

        # Berechne den Durchfluss für eine bestimmte Wasserhöhe
        water_level = waterLevelHeight_telem  # in mm
        flow_rate = flow_calc.calculate_flow_rate(water_level)
        print(f"Flow Rate (m3/h): {flow_rate}")

        # Konvertiere den Durchfluss in verschiedene Einheiten
        flow_rate_l_min = flow_calc.convert_to_liters_per_minute(flow_rate)
        flow_rate_l_h = flow_calc.convert_to_liters_per_hour(flow_rate)
        flow_rate_m3_min = flow_calc.convert_to_cubic_meters_per_minute(flow_rate)



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
                #callGpsSwitch = False
            else:
                print("Keine GPS-Daten verfügbar.", callGpsSwitch)
                
        else:
            print("GPS-Aufruf ist deaktiviert.", callGpsSwitch)  

        #Main power switch if
        if powerButton:

            try:
                # Start auto read
                # Read temperatures
                measuredPHValue_telem = PH_Sensor.read_register(start_address=0x0001, register_count=2)
                temperaturPHSens_telem = PH_Sensor.read_register(start_address=0x0003, register_count=2)
                print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}')

                if turbiditySensorActive:
                    # Read other values
                    measuredTurbidity_telem = Trub_Sensor.read_register(start_address=0x0001, register_count=2)
                    tempTruebSens = Trub_Sensor.read_register(start_address=0x0003, register_count=2)
                    print(f'Trueb: {measuredTurbidity_telem}, Trueb Temp Sens: {tempTruebSens}')   
                else:
                    print("TruebOFF", turbiditySensorActive)
 
                    

                if radarSensorActive:
                    # Read other values
                    messuredRadar_Air_telem = Radar_Sensor.read_radar_sensor(register_address=0x0001)
                    print(f'Radar Messuring Height: {messuredRadar_Air_telem}')
                else:
                    print("RadarOFF", radarSensorActive)

            except Exception as e:
                print(f"An error occurred: {e}")
            #END RS485 CALL
            
            # Main Logic
            if autoSwitch:
                pumpRelaySwSig = pumpRelaySw
                co2RelaisSwSig = co2RelaisSw
                co2HeatingRelaySwSig = co2HeatingRelaySw
                #ph_control.set_pump_switch(co2RelaisSw)
                #pumpRelaySwSig = ph_control.get_pump_switch()
                #co2RelaisSwSig = ph_control.get_co2_valve_switch()
                
                #co2RelaisSwSig = True
                #print("ph_control.set_pump_switch(True)", ph_control.set_pump_switch)
                #time.sleep(1)
                print("automode ON", autoSwitch)
            else:
                #time.sleep(1)
                print("automode OFF", autoSwitch)
        else:
            print("Power Switch OFF.", powerButton)
            #ph_control.set_pump_switch(False)
            #ph_control.set_co2_valve_switch(False)
            #co2RelaisSwSig = False
            #pumpRelaySwSig = False
            #co2HeatingRelaySwSig = False
            #autoSwitch = False
        time.sleep(2)


if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")
#Test