# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: GPS Test V0.1
# Description: Test script that uses gpsDataLib to fetch and process GPS data
# -----------------------------------------------------------------------------

import gpsDataLib

# Steuervariable
callGpsSwitch = True

if callGpsSwitch:
    # Abrufen und Verarbeiten der GPS-Daten (mit einem Timeout von 10 Sekunden)
    timestamp, latitude, longitude, altitude = gpsDataLib.fetch_and_process_gps_data(timeout=10)

    if timestamp is not None:
        # Ausgabe der GPS-Daten für Debugging-Zwecke
        print(f"Zeitstempel: {timestamp}")
        print(f"Breitengrad: {latitude}")
        print(f"Längengrad: {longitude}")
        print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
    else:
        print("Keine GPS-Daten verfügbar.")
else:
    print("GPS-Aufruf ist deaktiviert.")
