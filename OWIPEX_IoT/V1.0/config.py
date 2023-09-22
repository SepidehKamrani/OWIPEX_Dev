
# Configuration details for h2oMain.py

# Thingsboard Server Configuration
ACCESS_TOKEN = "buyj4qVjjCWd1Zvp4onK"
THINGSBOARD_SERVER = '192.168.100.26' #Standardt IP Adresse EDGE Server
THINGSBOARD_PORT = 1883

# Machine Configuration
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

# PH Configuration
minimumPHValue = 6.8
minimumPHValueStop = 6.5
maximumPHValue = 7.8
ph_low_delay_duration = 180  # in sek
ph_high_delay_duration = 600  # in sek
PHValueOffset = 0.0
temperaturPHSens_telem = 0.0
measuredPHValue_telem = 0.0
gemessener_high_wert = 10.00
gemessener_low_wert = 7.00
calibratePH = False
targetPHValue = 7.50
targetPHtolerrance = 0.40
countdownPHHigh = None
countdownPHLow = None

# Turbidity Configuration
measuredTurbidity = 0
maximumTurbidity = 0
turbiditySensorActive = False
turbidityOffset = 0
measuredTurbidity_telem = 0
tempTruebSens = 0.00

# Radar Configuration
waterLevelHeight = 1.0
waterLevelHeight_telem = 2.0
messuredRadar_Air_telem = 1 
radarSensorActive = False
radarSensorOffset = 0.0

# Flow Configuration
flow_rate_l_min = 20.0
flow_rate_l_h = 20.0
flow_rate_m3_min = 20.0

# GPS Configuration
gpsTimestamp = 1.0
gpsLatitude = 1.0
gpsLongitude = 1.0
gpsHeight = 1.0


# Telemetry and Attribute Variables
telemetry_keys = ['powerButton', 'autoSwitch', 'co2RelaisSw', 'co2HeatingRelaySw', 'pumpRelaySw', 'calculatedFlowRate', 'waterLevelHeight_telem', 'measuredTurbidity_telem', 'co2RelaisSwSig', 
                  'co2HeatingRelaySwSig', 'pumpRelaySwSig', 'measuredPHValue_telem', 'temperaturPHSens_telem', 'gpsTimestamp', 'messuredRadar_Air_telem', 
                  'countdownPHHigh', 'countdownPHLow', 'flow_rate_l_min', 'flow_rate_l_h', 'flow_rate_m3_min', 'gpsLatitude', 'gpsLongitude', 'gpsHeight', 'minimumPHValue', 'maximumPHValue']

attributes_keys = ['ip_address', 'macaddress']



# Lists for different groups of attributes
shared_attributes_keys = ['maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'radarSensorActive',  
                          'co2RelaisSwSig']

machine_attributes_keys = ['autoSwitch', 'powerButton', 'co2RelaisSw', 'pumpRelaySw', 'co2HeatingRelaySw']

ph_attributes_keys = ['ph_low_delay_start_time', 'ph_high_delay_duration', 'PHValueOffset', 'gemessener_high_wert', 'gemessener_low_wert', 'calibratePH', 'targetPHValue', 'targetPHtolerrance']

turbidity_attributes_keys = ['maximumTurbidity', 'turbiditySensorActive', 'turbidityOffset', 'tempTruebSens']

radar_attributes_keys = ['radarSensorActive']

alarm_attributes_keys = ['alarmActiveMachine', 'alarmMessageMachine', 'resetAlarm']

gps_attributes_keys = ['callGpsSwitch']


