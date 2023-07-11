import logging.handlers
import time
import os
import random

from tb_gateway_mqtt import TBDeviceMqttClient

ACCESS_TOKEN = "qpG2Ea3fjYQaVeqzB8q3"  # Replace this with your actual access token
THINGSBOARD_SERVER = 'localhost'  # Replace with your Thingsboard server address
THINGSBOARD_PORT = 1883

logging.basicConfig(level=logging.DEBUG)

client = None

class MachineAttributes:
    def __init__(self):
        self.length = ""
        self.width = ""
        self.height = ""
        self.maximumFillHeight = ""
        self.outletDiameter = ""
        self.outletHeight = ""
        self.minimumPHValue = ""
        self.maximumPHValue = ""
        self.measuredPHValue = ""
        self.PHValueOffset = ""
        self.measuredTurbidity = ""
        self.maximumTurbidity = ""
        self.turbiditySensorActive = ""
        self.turbidityOffset = ""
        self.waterLevelHeight = ""
        self.alarmActiveMachine = ""
        self.alarmMessage = ""
        self.resetAlarm = ""
        self.totalVolume = ""
        self.tankVolumeToOutlet = ""
        self.tankVolumeToMaxAllowedFill = ""
        self.calculatedFlowRate = ""
        self.powerSwitch = ""
        self.automaticSwitch = ""

machine_attrs = MachineAttributes()

def attribute_callback(result, _):
    print(result)
    for key in result.keys():
        setattr(machine_attrs, key, result.get(key, ""))

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
    calculatedFlowRate_telem = random.uniform(15, 25)
    alarmActive_telem = False
    waterLevelHeight_telem = random.uniform(180, 200)
    turbiditySensorActive_telem = True
    measuredTurbidity_telem = random.uniform(100, 200)
    measuredPHValue_telem = random.uniform(5, 7)
    alarmOverfill_telem = False
    temperaturPHSens_telem = random.uniform(-5, 20)



    

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
        'calculatedFlowRate_telem': calculatedFlowRate_telem,
        'alarmActive_telem': alarmActive_telem,
        'waterLevelHeight_telem': waterLevelHeight_telem,
        'turbiditySensorActive_tele': turbiditySensorActive_telem,
        'measuredTurbidity_telem': measuredTurbidity_telem,
        'measuredPHValue_telem': measuredPHValue_telem,
        'alarmOverfill_telem': alarmOverfill_telem,
        'temperaturPHSens_telem': temperaturPHSens_telem

    }
    print(attributes, telemetry)
    return attributes, telemetry

def main():
    global client
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, THINGSBOARD_PORT, ACCESS_TOKEN)
    client.connect()
    
    # Request shared attributes
    client.request_attributes(shared_keys=['length', 'width', 'height', 'maximumFillHeight', 'outletDiameter', 'outletHeight', 'minimumPHValue', 'maximumPHValue', 'measuredPHValue', 'PHValueOffset', 'measuredTurbidity', 'maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'waterLevelHeight', 'alarmActiveMachine', 'alarmMessageMachine', 'resetAlarm', 'totalVolume', 'tankVolumeToOutlet', 'tankVolumeToMaxAllowedFill', 'calculatedFlowRate', 'powerSwitch', 'automaticSwitch'], callback=attribute_callback)
    
    # Subscribe to individual attributes
    # Code for subscribing to individual attributes...

    # Now rpc_callback will process rpc requests from the server
    client.set_server_side_rpc_request_handler(rpc_callback)

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        time.sleep(60)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run the")
