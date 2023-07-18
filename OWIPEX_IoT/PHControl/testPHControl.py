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

# main.py
from ph_control import PHControl

# Erstellt ein PHControl-Objekt
ph_control = PHControl(min_ph=5.0, max_ph=7.0, check_timer=60, on_delay_timer=60, pump_start_delay=5)

# Aktualisieren Sie den gemessenen pH-Wert in Ihrem Hauptprogramm
# Dies sollte in Ihrem tatsächlichen Code durch eine tatsächliche pH-Messung ersetzt werden
ph_control.set_measured_ph(8.0)

# Setzen Sie den Pumpenschalter in Ihrem Hauptprogramm
# Dies sollte in Ihrem tatsächlichen Code durch eine tatsächliche Benutzereingabe oder andere Logik ersetzt werden
ph_control.set_pump_switch(True)

# Setzen Sie den CO2-Ventilschalter in Ihrem Hauptprogramm
# Dies sollte in Ihrem tatsächlichen Code durch eine tatsächliche Benutzereingabe oder andere Logik ersetzt werden
ph_control.set_co2_valve_switch(True)

# Setzen Sie die Anlaufverzögerung für die Pumpe
# Dies sollte in Ihrem tatsächlichen Code durch eine tatsächliche Benutzereingabe oder andere Logik ersetzt werden
ph_control.set_pump_delay(10)