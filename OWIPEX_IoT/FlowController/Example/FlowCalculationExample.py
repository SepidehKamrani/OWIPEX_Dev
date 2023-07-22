# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Script: FlowCalculationExample
# Version: 1.0
# Description: Ein einfaches Beispiel für die Verwendung der FlowCalculation-Klasse.
# -----------------------------------------------------------------------------

from FlowCalculation import FlowCalculation
import os

def main():
    # Pfad zur Kalibrierungsdatei
    calibration_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "calibration_file.csv")

    # Erstelle eine Instanz der FlowCalculation-Klasse
    flow_calc = FlowCalculation(calibration_file_path)

    # Hole den 0-Referenzwert
    zero_ref = flow_calc.get_zero_reference()
    print(f"Zero Reference: {zero_ref}")

    # Berechne den Durchfluss für eine bestimmte Wasserhöhe
    water_level = 500  # in mm
    flow_rate = flow_calc.calculate_flow_rate(water_level)
    print(f"Flow Rate (m3/h): {flow_rate}")

    # Konvertiere den Durchfluss in verschiedene Einheiten
    flow_rate_l_min = flow_calc.convert_to_liters_per_minute(flow_rate)
    flow_rate_l_h = flow_calc.convert_to_liters_per_hour(flow_rate)
    flow_rate_m3_min = flow_calc.convert_to_cubic_meters_per_minute(flow_rate)
    
    print(f"Flow Rate (l/min): {flow_rate_l_min}")
    print(f"Flow Rate (l/h): {flow_rate_l_h}")
    print(f"Flow Rate (m3/min): {flow_rate_m3_min}")

if __name__ == "__main__":
    main()
