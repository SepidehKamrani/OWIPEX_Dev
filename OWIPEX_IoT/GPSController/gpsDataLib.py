# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: GPS Data Fetch V0.1
# Description: Library to fetch GPS data
# -----------------------------------------------------------------------------

import gpsd

def get_gps_data():
    # Verbindet mit dem lokalen gpsd
    gpsd.connect()

    while True:
        try:
            packet = gpsd.get_current()

            if packet.mode >= 2:  # Mode 2 bedeutet 2D-Fix, was mindestens Längen- und Breitengrad bedeutet.
                print("Zeit: {}".format(packet.time))
                print("Breitengrad: {}".format(packet.position()[0]))
                print("Längengrad: {}".format(packet.position()[1]))
                if packet.mode == 3:  # Mode 3 bedeutet 3D-Fix, was zusätzlich Höhe bedeutet.
                    print("Höhe: {} m".format(packet.alt))
                return packet  # GPS-Daten erfolgreich abgerufen, verlassen der Funktion
            else:
                print("Kein GPS-Fix verfügbar, versuche es erneut...")

        except KeyError:
            pass
        except KeyboardInterrupt:
            print("Abbruch durch Benutzer.")
            break
