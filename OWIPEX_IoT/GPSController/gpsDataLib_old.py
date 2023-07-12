# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: GPS Data Library V0.1
# Description: Library to fetch GPS data using gpsd
# -----------------------------------------------------------------------------

import gpsd
import time

def get_gps_data(timeout=None):
    gpsd.connect()

    start_time = time.time()  # Speichert die Startzeit
    
    while True:
        packet = gpsd.get_current()

        # Überprüft, ob mindestens Längen- und Breitengrad verfügbar sind
        if packet.mode >= 2:
            return packet

        # Überprüft, ob das Timeout erreicht wurde
        if timeout is not None and time.time() - start_time > timeout:
            return None

        time.sleep(1)  # Wartet eine Sekunde, bevor der nächste Versuch gestartet wird
