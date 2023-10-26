# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: GPS Data Library V0.1
# Description: Library to fetch and process GPS data
# +41799671502
# -----------------------------------------------------------------------------

import gpsd
import time

# Verbindet mit dem lokalen gpsd
gpsd.connect()

def get_gps_data(timeout=10):
    start_time = time.time()
    while time.time() - start_time <= timeout:
        packet = gpsd.get_current()
        if packet.mode >= 2:  # Mode 2 bedeutet 2D-Fix, was mindestens Längen- und Breitengrad bedeutet.
            return packet
    return None