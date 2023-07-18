"""
# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: MainProgram
# Version: 1.0
# Description: Dies ist das Hauptprogramm, das die PHControl und GPIOControl Module verwendet, 
# um den pH-Wert in einem System automatisch zu regulieren und eine Pumpe zu steuern. Es bietet 
# auch eine Schnittstelle für die manuelle Steuerung des Systems.
#
# Im Hauptprogramm werden drei Werte gehandhabt:
# - `minimumPHValue`: Der minimale zulässige pH-Wert.
# - `maximumPHValue`: Der maximale zulässige pH-Wert.
# - `measuredPHValue_telem`: Der gemessene pH-Wert, der vom Telemetriesystem geliefert wird.
#
# Das Hauptprogramm stellt Schnittstellen zur Verfügung, um diese Werte zu setzen und zu erhalten, 
# und es verwendet die PHControl Klasse, um die automatische Kontrolle des Systems basierend auf 
# diesen Werten zu handhaben. Es bietet auch Schnittstellen für die manuelle Steuerung des CO2-Ventils 
# und der Pumpe.
# -----------------------------------------------------------------------------
"""

def main():
    # Erstelle ein PHControl-Objekt
    ph_controller = PHControl(min_ph=6.5, max_ph=7.5, check_timer=10, on_delay_timer=5)

    # Setze den gemessenen pH-Wert
    ph_controller.set_measured_ph(7.6)

    # Lass die Pumpe laufen
    ph_controller.set_pump_switch(True)

    # Manuelle Kontrolle des CO2-Ventils (EIN)
    ph_controller.set_co2_valve_switch(True)

    # Warte für eine Weile
    time.sleep(20)

    # Ändere den gemessenen pH-Wert
    ph_controller.set_measured_ph(7.2)

    # Manuelle Kontrolle des CO2-Ventils (AUS)
    ph_controller.set_co2_valve_switch(False)

    # Warte für eine Weile
    time.sleep(20)

    # Automatische Kontrolle des CO2-Ventils
    # Setze den CO2-Ventilschalter auf None, um automatische Kontrolle zu ermöglichen
    ph_controller.set_co2_valve_switch(None)

    # Lasse das Programm für eine Weile laufen, um den Automatisierungsprozess zu beobachten
    time.sleep(100)

if __name__ == "__main__":
    main()