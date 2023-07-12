# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Main Program V0.1
# Description: Main program that uses gpsDataLib to fetch GPS data within a given time limit
# -----------------------------------------------------------------------------

import gpsDataLib

# Ruft die GPS-Daten mit einem Timeout von 10 Sekunden ab.
# Wenn die Daten innerhalb von 10 Sekunden nicht abgerufen werden können, gibt `get_gps_data` `None` zurück.
gps_packet = gpsDataLib.get_gps_data(10)

# Überprüft, ob die GPS-Daten erfolgreich abgerufen wurden
if gps_packet is not None:
    # Extrahiere die benötigten Daten aus dem Paket in spezifische Variablen
    timestamp = gps_packet.time  # Zeitstempel der GPS-Daten
    latitude, longitude = gps_packet.position()  # Breiten- und Längengrad

    # Da die Höhe nur verfügbar ist, wenn ein 3D-Fix vorhanden ist, überprüfen wir zunächst, ob das der Fall ist.
    # Wenn kein 3D-Fix vorhanden ist, wird `altitude` auf `None` gesetzt.
    altitude = gps_packet.alt if gps_packet.mode == 3 else None

    # Zum Debugging geben wir die Werte aus
    print(f"Zeitstempel: {timestamp}")
    print(f"Breitengrad: {latitude}")
    print(f"Längengrad: {longitude}")
    print(f"Höhe: {altitude if altitude is not None else 'nicht verfügbar'}")
else:
    print("Keine GPS-Daten verfügbar.")

# Nun können Sie die Variablen `timestamp`, `latitude`, `longitude` und `altitude` in Ihrem Code verwenden.
