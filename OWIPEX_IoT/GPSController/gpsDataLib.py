# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: gpsDataLib V0.2
# Description: Library for handling GPS data fetching and processing
# -----------------------------------------------------------------------------

import gpsd
import time

def connect_to_gpsd():
    gpsd.connect()

def get_gps_data(timeout=None):
    start_time = time.time()

    while True:
        packet = gpsd.get_current()
        
        if packet.mode >= 2:  # A 2D fix at least, meaning we have latitude and longitude.
            return packet
        
        # If a timeout is set and we've passed that timeout, stop trying to get data.
        if timeout is not None and time.time() - start_time > timeout:
            return None

def process_gps_data(packet):
    if packet is not None:
        # Extract the needed data from the packet into specific variables
        timestamp = packet.time  # Timestamp of the GPS data
        latitude, longitude = packet.position()  # Latitude and longitude

        # Altitude is only available if a 3D fix is available, so we first check if that is the case.
        # If a 3D fix is not available, `altitude` is set to `None`.
        altitude = packet.alt if packet.mode == 3 else None

        # For debugging, we print the values
        print(f"Zeitstempel: {timestamp}")
        print(f"Breitengrad: {latitude}")
        print(f"Längengrad: {longitude}")
        print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
        
        # Return the values so they can be used elsewhere in the program
        return timestamp, latitude, longitude, altitude
    else:
        print("Keine GPS-Daten verfügbar.")
