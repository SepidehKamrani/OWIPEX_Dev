# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: FlowCalculation
# Version: 1.3
# Description: Dieses Modul enthält die FlowCalculation-Klasse, die verschiedene
# Methoden zur Berechnung der Durchflussrate basierend auf der Wasserhöhe, der
# Auslasshöhe und dem Durchmesser des Auslasses bereitstellt. Die Klasse unterstützt 
# nun auch die Berechnung für runde, rechteckige und dreieckige Auslässe. Es werden
# Werte in "mm" für die Eingaben akzeptiert und die Ausgabe kann in l/min, l/h, 
# m3/min und m3/h erfolgen.
# -----------------------------------------------------------------------------

import math

class FlowCalculation:
    def __init__(self):
        self.g = 9.81  # gravitational constant, m/s^2

    def calculate_flow_rate_round(self, water_level, outlet_height, outlet_diameter):
        water_level /= 1000  # convert mm to m
        outlet_height /= 1000  # convert mm to m
        outlet_diameter /= 1000  # convert mm to m

        fill_percentage = self._calculate_fill_percentage(water_level, outlet_height)
        r = outlet_diameter / 2  # radius of the outlet
        A = math.pi * r ** 2 * fill_percentage  # area of the outlet

        return self._calculate_flow_rate(water_level - outlet_height, A)

    def calculate_flow_rate_rectangular(self, water_level, outlet_height, outlet_width, outlet_height):
        water_level /= 1000  # convert mm to m
        outlet_height /= 1000  # convert mm to m
        outlet_width /= 1000  # convert mm to m
        outlet_height /= 1000  # convert mm to m

        fill_percentage = self._calculate_fill_percentage(water_level, outlet_height)
        A = outlet_width * outlet_height * fill_percentage  # area of the outlet

        return self._calculate_flow_rate(water_level - outlet_height, A)

    def calculate_flow_rate_triangular(self, water_level, outlet_height, outlet_base):
        water_level /= 1000  # convert mm to m
        outlet_height /= 1000  # convert mm to m
        outlet_base /= 1000  # convert mm to m

        fill_percentage = self._calculate_fill_percentage(water_level, outlet_height)
        A = 0.5 * outlet_base * outlet_height * fill_percentage  # area of the outlet

        return self._calculate_flow_rate(water_level - outlet_height, A)

    def _calculate_flow_rate(self, h, A):
        if h < 0:
            print("Warning: water level is below outlet height. Setting flow rate to zero.")
            return 0
        else:
            v = math.sqrt(2 * self.g * h)  # velocity
            Q = A * v * 3600 # flow rate in m3/h
            return Q

    def _calculate_fill_percentage(self, water_level, outlet_height):
        if water_level < outlet_height:
            return 0
        else:
            return min((water_level - outlet_height) / outlet_height, 1)

    # Convert flow rate to different units
    def convert_to_liters_per_minute(self, flow_rate):
        return flow_rate * 1000 / 60  # convert m3/h to l/min

    def convert_to_liters_per_hour(self, flow_rate):
        return flow_rate * 1000  # convert m3/h to l/h

    def convert_to_cubic_meters_per_minute(self, flow_rate):
        return flow_rate / 60  # convert m3/h to m3/min

    def convert_to_cubic_meters_per_hour(self, flow_rate):
        return flow_rate  # already in m3/h
