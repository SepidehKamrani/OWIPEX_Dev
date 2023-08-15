import time
from modbus_lib import DeviceManager

# Create a Device Manager instance with default parameters
dev_manager = DeviceManager(port='/dev/ttymxc3', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=1)

# Add devices to the Device Manager
Radar_Sensor = dev_manager.add_device(device_id=0x01)
Trub_Sensor = dev_manager.add_device(device_id=0x02)
PH_Sensor = dev_manager.add_device(device_id=0x03)

# Create separate threads for automatic reading
import threading
radar_thread = threading.Thread(target=Radar_Sensor.start_auto_read)
trub_thread = threading.Thread(target=Trub_Sensor.start_auto_read)
ph_thread = threading.Thread(target=PH_Sensor.start_auto_read)

# Start the threads
radar_thread.start()
trub_thread.start()
ph_thread.start()

# For demonstration, let's read the values for 30 seconds and then stop
start_time = time.time()
while time.time() - start_time < 30:
    # Here we can add telemetry sending or logging code
    # As an example, we print the average value of the sensors and their corresponding temperatures
    print(f"Radar Average: {Radar_Sensor.get_average_value()}")
    print(f"Trub Measurement Average: {Trub_Sensor.get_average_value()}")
    print(f"Trub Temperature Average: {Trub_Sensor.get_average_value(index=1)}")
    print(f"PH Measurement Average: {PH_Sensor.get_average_value()}")
    print(f"PH Temperature Average: {PH_Sensor.get_average_value(index=1)}")
    
    time.sleep(5)  # Print every 5 seconds

# Stop the automatic reading threads
Radar_Sensor.stop_auto_read()
Trub_Sensor.stop_auto_read()
PH_Sensor.stop_auto_read()

# Join the threads to wait for their completion
radar_thread.join()
trub_thread.join()
ph_thread.join()
