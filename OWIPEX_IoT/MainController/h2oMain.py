import logging.handlers
import time
import os
import random
import gpsDataLib
import math

from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep

ACCESS_TOKEN = "I9Vbnng0MBpxY5UDX67l"  # Replace this with your actual access token
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
length = 4.0
width = 2.8
height = 2.5
maximumFillHeight = 2.3
outletDiameter = 0.05
outletHeight = 1.6
totalVolume = 1.0
tankVolumeToOutlet = 1.0
tankVolumeToMaxAllowedFill = 1.0
calculatedFlowRate = 1.0
powerSwitch = False
autoSwitch = False
callGpsSwitch = False
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
radarSensorEmpty = 3.0
radarSensorDrain = 0.0
#GPS
gpsTimestamp = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsHeight = 1.0
#ALARM
alarmActiveMachine = ""
alarmMessage = ""
resetAlarm = ""



#Flow Calculation
def calculate_flow_rate(water_level, outlet_height, outlet_diameter):
    g = 9.81  # gravitational constant, m/s^2
    r = outlet_diameter / 2  # radius of the outlet
    A = math.pi * r ** 2  # area of the outlet
    h = water_level - outlet_height  # height of the water above the outlet

    if h < 0:
        print("Warning: water level is below outlet height. Setting flow rate to zero.")
        return 0
    else:
        v = math.sqrt(2 * g * h)  # velocity
        Q = A * v * 3600 # flow rate
        return Q
    




# Callback function that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    global length, width, height, radarSensorEmpty, radarSensorDrain, maximumFillHeight, outletDiameter, outletHeight, minimumPHValue, maximumPHValue, PHValueOffset, maximumTurbidity, turbiditySensorActive, turbidityOffset, radarSensorActive, radarOffset, alarmActiveMachine, alarmMessageMachine, resetAlarm, powerSwitch, autoSwitch, callGpsSwitch
    print(result)
    #machine
    if 'length' in result:
        length = result['length']
    if 'width' in result:
        width = result['width']
    if 'height' in result:
        height = result['height']
    if 'maximumFillHeight' in result:
        maximumFillHeight = result['maximumFillHeight']
    if 'outletDiameter' in result:
        outletDiameter = result['outletDiameter']
    if 'outletHeight' in result:
        outletHeight = result['outletHeight']
    if 'powerSwitch' in result:
        powerSwitch = result['powerSwitch']
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
    if 'alarmActiveMachine' in result:
        alarmActiveMachine = result['alarmActiveMachine']
    if 'alarmMessageMachine' in result:
        alarmMessageMachine = result['alarmMessageMachine']
    if 'resetAlarm' in result:
        resetAlarm = result['resetAlarm']
    if 'radarSensorEmpty' in result:
        radarSensorEmpty = result['radarSensorEmpty']
    if 'radarSensorDrain' in result:
        radarSensorDrain = result['radarSensorDrain']    
         
    

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
    global temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, totalVolume, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, totalVolume, tankVolumeToOutlet, tankVolumeToMaxAllowedFill, messuredRadar_Air_telem, radarSensorDrain, radarSensorEmpty
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
    
    #device
    alarmActive_telem = False 
    alarmOverfill_telem = False

    #calculate tank volumes
    totalVolume = length * width * height
    tankVolumeToOutlet = length * width * outletHeight
    tankVolumeToMaxAllowedFill = length * width * maximumFillHeight

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
        #PH Sens
        'measuredPHValue_telem': measuredPHValue_telem,
        'temperaturPHSens_telem': temperaturPHSens_telem,
        'totalVolume': totalVolume,
        'gpsTimestamp': gpsTimestamp,
        'gpsLatitude': gpsLatitude,
        'gpsLongitude': gpsLongitude,
        'gpsHeight': gpsHeight,
        'tankVolumeToOutlet': tankVolumeToOutlet,
        'tankVolumeToMaxAllowedFill': tankVolumeToMaxAllowedFill,
        'messuredRadar_Air_telem': messuredRadar_Air_telem,
        #Alarm
        'alarmActive_telem': alarmActive_telem,
        'alarmOverfill_telem': alarmOverfill_telem
        
        
        

    }
    print(attributes, telemetry)
    return attributes, telemetry

def main():
    #def Global Variables for Main Funktion
    global client, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, gpsTimestamp, gpsLatitude, gpsLongitude, gpsHeight, waterLevelHeight_telem, calculatedFlowRate, messuredRadar_Air_telem
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    
    # Request shared attributes
    client.request_attributes(shared_keys=['length', 'width', 'height', 'maximumFillHeight', 'outletDiameter', 'outletHeight', 'minimumPHValue', 'maximumPHValue', 'PHValueOffset', 'maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'radarSensorActive', 'alarmActiveMachine', 'alarmMessageMachine', 'resetAlarm', 'powerSwitch', 'autoSwitch', 'callGpsSwitch'], callback=attribute_callback)
    
    # Subscribe to individual attributes
    #machine
    client.subscribe_to_attribute("powerSwitch", attribute_callback)
    client.subscribe_to_attribute("autoSwitch", attribute_callback)
    client.subscribe_to_attribute('length', attribute_callback)
    client.subscribe_to_attribute('width', attribute_callback)
    client.subscribe_to_attribute('height', attribute_callback)
    client.subscribe_to_attribute('maximumFillHeight', attribute_callback)
    client.subscribe_to_attribute('outletDiameter', attribute_callback)
    client.subscribe_to_attribute('outletHeight', attribute_callback)
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
    client.subscribe_to_attribute('radarSensorDrain', attribute_callback)
    client.subscribe_to_attribute('radarSensorEmpty', attribute_callback)
     
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
        
        # Berechnen der Durchflussrate anhand der Wasserhöhe, Auslaufhöhe und des Auslaufdurchmessers
        calculatedFlowRate = calculate_flow_rate(waterLevelHeight_telem, outletHeight, outletDiameter)
        print("calculatedFlowRate: ", calculatedFlowRate)
        waterLevelHeight_telem = radarSensorEmpty - (float(messuredRadar_Air_telem) / 1000)
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
        if powerSwitch:

            try:
                # Start auto read
                # Read temperatures
                measuredPHValue_telem = PH_Sensor.read_register(start_address=0x0001, register_count=2)
                temperaturPHSens_telem = PH_Sensor.read_register(start_address=0x0003, register_count=2)
                print(f'PH: {measuredPHValue_telem}, Temperature PH Sens: {temperaturPHSens_telem}', powerSwitch)

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
                    #messuredRadar_Liq_telem = Radar_Sensor.read_radar_sensor(register_address=0x0003)
                    print(f'Radar Messuring Height: {messuredRadar_Air_telem}')
                else:
                    print("RadarOFF", radarSensorActive)

            except Exception as e:
                print(f"An error occurred: {e}")
            #END RS485 CALL
            
            # Main Logic
            if autoSwitch:
                #time.sleep(1)
                print("automode ON", autoSwitch)
            else:
                #time.sleep(1)
                print("automode OFF", autoSwitch)
        else:
            print("Power Switch OFF.", powerSwitch)
        time.sleep(2)


if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")
