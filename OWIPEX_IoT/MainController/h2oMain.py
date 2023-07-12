import logging.handlers
import time
import os
import random
import gpsDataLib

from tb_gateway_mqtt import TBDeviceMqttClient
from modbus_lib import DeviceManager
from time import sleep

ACCESS_TOKEN = "I9Vbnng0MBpxY5UDX67l"  # Replace this with your actual access token
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883


#RS485 Comunication and Devices
# Create DeviceManager
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)
# Add devices
dev_manager.add_device(device_id=0x01)
dev_manager.add_device(device_id=0x02)

#logging.basicConfig(level=logging.DEBUG)

client = None

# Global Variables
#Machine 
length = 6,2
width = 3,1
height = 2,5
maximumFillHeight = ""
outletDiameter = ""
outletHeight = ""
totalVolume = 1,0
tankVolumeToOutlet = ""
tankVolumeToMaxAllowedFill = ""
calculatedFlowRate = ""
powerSwitch = ""
automaticSwitch = ""
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
waterLevelHeight = ""
alarmActiveMachine = ""
alarmMessage = ""
resetAlarm = ""
#GPS
callGpsSwitch = True


# Callback function that will be called when the value of our Shared Attribute changes
def attribute_callback(result, _):
    global length, width, height, maximumFillHeight, outletDiameter, outletHeight, minimumPHValue, maximumPHValue, PHValueOffset, maximumTurbidity, turbiditySensorActive, turbidityOffset, alarmActiveMachine, alarmMessageMachine, resetAlarm, powerSwitch, automaticSwitch
    print(result)
    length = result.get('length', "")
    width = result.get('width', "")
    height = result.get('height', "")
    maximumFillHeight = result.get('maximumFillHeight', "")
    outletDiameter = result.get('outletDiameter', "")
    outletHeight = result.get('outletHeight', "")
    minimumPHValue = result.get('minimumPHValue', "")
    maximumPHValue = result.get('maximumPHValue', "")
    #measuredPHValue = result.get('measuredPHValue', "")
    PHValueOffset = result.get('PHValueOffset', "")
    #measuredTurbidity = result.get('measuredTurbidity', "")
    maximumTurbidity = result.get('maximumTurbidity', "")
    turbiditySensorActive = result.get('turbiditySensorActive', "")
    turbidityOffset = result.get('turbidityOffset', "")
    #waterLevelHeight = result.get('waterLevelHeight', "")
    alarmActiveMachine = result.get('alarmActiveMachine', "")
    alarmMessageMachine = result.get('alarmMessageMachine', "")
    resetAlarm = result.get('resetAlarm', "")
    #totalVolume = result.get('totalVolume', "")
    #tankVolumeToOutlet = result.get('tankVolumeToOutlet', "")
    #tankVolumeToMaxAllowedFill = result.get('tankVolumeToMaxAllowedFill', "")
    #calculatedFlowRate = result.get('calculatedFlowRate', "")
    powerSwitch = result.get('powerSwitch', "")
    automaticSwitch = result.get('automaticSwitch', "")

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
    global temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, totalVolume
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
    totalVolume = flaot(length) * float(height) * float(width)

    #device
    calculatedFlowRate_telem = random.uniform(15, 25)
    alarmActive_telem = False
    waterLevelHeight_telem = random.uniform(180, 200)
    #measuredTurbidity_telem = random.uniform(100, 200)
    alarmOverfill_telem = False

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
        
        #device PH Sens
        'calculatedFlowRate_telem': calculatedFlowRate_telem,
        'alarmActive_telem': alarmActive_telem,
        'waterLevelHeight_telem': waterLevelHeight_telem,
        #'turbiditySensorActive_tele': turbiditySensorActive_telem,
        'measuredTurbidity_telem': measuredTurbidity_telem,
        'measuredPHValue_telem': measuredPHValue_telem,
        'alarmOverfill_telem': alarmOverfill_telem,
        'temperaturPHSens_telem': temperaturPHSens_telem

    }
    print(attributes, telemetry)
    return attributes, telemetry

def main():
    #def Global Variables for Main Funktion
    global client, temperaturPHSens_telem, measuredPHValue_telem, measuredTurbidity_telem, callGpsSwitch, powerSwitch, automaticSwitch, totalVolume
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    
    # Request shared attributes
    client.request_attributes(shared_keys=['length', 'width', 'height', 'maximumFillHeight', 'outletDiameter', 'outletHeight', 'minimumPHValue', 'maximumPHValue', 'PHValueOffset', 'maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'alarmActiveMachine', 'alarmMessageMachine', 'resetAlarm', 'powerSwitch', 'automaticSwitch'], callback=attribute_callback)
    
    # Subscribe to individual attributes
    client.subscribe_to_attribute('length', attribute_callback)
    client.subscribe_to_attribute('width', attribute_callback)
    client.subscribe_to_attribute('height', attribute_callback)
    client.subscribe_to_attribute('maximumFillHeight', attribute_callback)
    client.subscribe_to_attribute('outletDiameter', attribute_callback)
    client.subscribe_to_attribute('outletHeight', attribute_callback)
    client.subscribe_to_attribute('tankVolumeToOutlet', attribute_callback)
    client.subscribe_to_attribute('tankVolumeToMaxAllowedFill', attribute_callback)
    #client.subscribe_to_attribute('calculatedFlowRate', attribute_callback)
    client.subscribe_to_attribute('minimumPHValue', attribute_callback)
    client.subscribe_to_attribute('maximumPHValue', attribute_callback)
    #client.subscribe_to_attribute('measuredPHValue', attribute_callback)
    client.subscribe_to_attribute('PHValueOffset', attribute_callback)
    client.subscribe_to_attribute('measuredTurbidity', attribute_callback)
    client.subscribe_to_attribute('maximumTurbidity', attribute_callback)
    client.subscribe_to_attribute('turbiditySensorActive', attribute_callback)
    client.subscribe_to_attribute('turbidityOffset', attribute_callback)
    #client.subscribe_to_attribute('waterLevelHeight', attribute_callback)
    client.subscribe_to_attribute('alarmActiveMachine', attribute_callback)
    client.subscribe_to_attribute('alarmMessageMachine', attribute_callback)
    client.subscribe_to_attribute('resetAlarm', attribute_callback)
    #client.subscribe_to_attribute('totalVolume', attribute_callback)
    client.subscribe_to_attribute('powerSwitch', attribute_callback)
    client.subscribe_to_attribute('automaticSwitch', attribute_callback)
    

    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)

        #GPS DATA
        #Call GPS Data. Can be called even whitout power Switch. 
        if callGpsSwitch:
            # Abrufen und Verarbeiten der GPS-Daten (mit einem Timeout von 10 Sekunden)
            timestamp, latitude, longitude, altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)

            if timestamp is not None:
                # Ausgabe der GPS-Daten für Debugging-Zwecke
                print(f"Zeitstempel: {timestamp}")
                print(f"Breitengrad: {latitude}")
                print(f"Längengrad: {longitude}")
                print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
                callGpsSwitch = False
            else:
                print("Keine GPS-Daten verfügbar.")
        else:
            print("GPS-Aufruf ist deaktiviert.")
        #END GPS CALL    

        #Main power switch if
        if powerSwitch:

            # RS485 get devices and read their registers
            PH_Sensor = dev_manager.get_device(device_id=0x01)
            Trub_Sensor = dev_manager.get_device(device_id=0x02)
            try:
                # Start auto read
                # Read temperatures
                temperaturPHSens_telem = PH_Sensor.read_register(start_address=0x0003, register_count=2)
                tempTruebSens = Trub_Sensor.read_register(start_address=0x0003, register_count=2)
                print(f'Temperature 1: {temperaturPHSens_telem}, Temperature 2: {tempTruebSens}')

                # Read other values
                measuredPHValue_telem = PH_Sensor.read_register(start_address=0x0001, register_count=2)
                measuredTurbidity_telem = Trub_Sensor.read_register(start_address=0x0001, register_count=2)
                print(f'Other Value 1: {measuredPHValue_telem}, Other Value 2: {measuredTurbidity_telem}')
                # Stop auto read
                #PH_Sensor.stop_auto_read()
                #Trub_Sensor.stop_auto_read()                
            except Exception as e:
                print(f"An error occurred: {e}")
            #END RS485 CALL

            # Main Logic
            if automaticSwitch:
                #code
                print("automode ON")
            else:
                #code
                print("automode OFF")

        else:
            print("Power Off.")

        time.sleep(5)







if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")
