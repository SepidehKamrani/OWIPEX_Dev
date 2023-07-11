# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: Main Program V0.1
# Description: Main program that uses gpsDataLib to fetch GPS data
# -----------------------------------------------------------------------------

import gpsDataLib

gps_packet = gpsDataLib.get_gps_data()

# Die gps_packet-Variable enthält nun ein Paket mit GPS-Daten, die aus dem Aufruf von get_gps_data zurückgegeben wurden.
# Dieses Paket kann mehrere Eigenschaften haben, je nachdem, welche Daten vom GPS-Sensor abgerufen wurden.

# gps_packet.time: Das Datum und die Uhrzeit, zu denen die GPS-Daten abgerufen wurden. 
# Dies ist ein String im ISO 8601-Format, z.B. '2023-07-11T13:18:06.000Z'.

# gps_packet.position(): Gibt ein Tuple zurück, das den Breiten- und Längengrad der aktuellen Position des GPS-Sensors enthält.

# gps_packet.alt: Die Höhe über dem Meeresspiegel, gemessen in Metern. 
# Dies ist nur verfügbar, wenn der GPS-Sensor einen 3D-Fix hat (d.h. gps_packet.mode == 3).

# Hier können Sie die Daten aus `gps_packet` verwenden, wie Sie möchten. 
# Zum Beispiel könnten Sie sie in einer Datei speichern, auf einem Bildschirm anzeigen oder an eine andere Funktion senden.
