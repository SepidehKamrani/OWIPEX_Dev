"""
# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: PHControl
# Version: 1.0
# Description: Dieses Modul stellt die PHControl-Klasse bereit, die eine
# automatisierte Kontrolle des pH-Wertes in einem System ermöglicht. Sie
# ermöglicht die automatische Regelung eines CO2-Ventils und einer Pumpe
# basierend auf dem gemessenen pH-Wert und Benutzereingaben. Die Klasse nutzt
# dabei die GPIOControl-Klasse, um die GPIOs zu steuern.
# -----------------------------------------------------------------------------
"""
# ph_control.py
import time
import threading
from gpiocontrol import GPIOControl

class PHControl:
    def __init__(self, min_ph, max_ph, check_timer, on_delay_timer, pump_start_delay=0):
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.check_timer = check_timer
        self.on_delay_timer = on_delay_timer
        self.pump_start_delay = pump_start_delay
        self.measured_ph = None
        self.pump_switch = False
        self.co2_valve_switch = None  # Neue Variable für die manuelle CO2-Ventilsteuerung
        self.co2_valve = GPIOControl(6)  # CO2-Ventil ist auf GPIO 6
        self.pump = GPIOControl(7)  # Pumpe ist auf GPIO 7
        self.co2_valve.set_direction('out')
        self.pump.set_direction('out')

        # Alle GPIOs zur Sicherheit auf "Aus" setzen
        self.co2_valve.set_value('1')
        self.pump.set_value('1')

        # Starte den Hintergrundthread
        threading.Thread(target=self.control_loop, daemon=True).start()

    def set_measured_ph(self, ph):
        self.measured_ph = ph

    def set_pump_switch(self, switch):
        self.pump_switch = switch

    def set_co2_valve_switch(self, switch):
        self.co2_valve_switch = switch

    def set_pump_delay(self, delay):
        self.pump_start_delay = delay

    def control_loop(self):
        while True:
            # Steuerung der Pumpe
            if self.pump_switch:
                time.sleep(self.pump_start_delay)
                self.pump.set_value('0')  # Pumpe ein
            else:
                self.pump.set_value('1')  # Pumpe aus

            # Manuelle Steuerung des CO2-Ventils
            if self.co2_valve_switch is not None:
                if self.co2_valve_switch:
                    self.co2_valve.set_value('0')  # CO2-Ventil ein
                else:
                    self.co2_valve.set_value('1')  # CO2-Ventil aus
            # Automatische Steuerung des CO2-Ventils
            elif self.measured_ph is not None and self.measured_ph > self.max_ph:
                time.sleep(self.on_delay_timer)

                # Nach der Wartezeit, überprüfen wir erneut den PH-Wert
                if self.measured_ph > self.max_ph:
                    # CO2 Ventil einschalten (0 = Ein)
                    self.co2_valve.set_value('0')

                    # Kontinuierliche Überprüfung, ob der PH-Wert sinkt
                    while self.measured_ph > self.max_ph:
                        time.sleep(1)

                    # Sobald der PH-Wert unter dem max_ph liegt, starten wir den check_timer
                    start_time = time.time()
                    while time.time() - start_time < self.check_timer:
                        # Wenn der PH-Wert während der check_timer Zeit wieder steigt, brechen wir ab und starten von vorne
                        if self.measured_ph > self.max_ph:
                            break
                        time.sleep(1)
                    else:
                        # CO2 Ventil ausschalten (1 = Aus)
                        self.co2_valve.set_value('1')

            time.sleep(1)
