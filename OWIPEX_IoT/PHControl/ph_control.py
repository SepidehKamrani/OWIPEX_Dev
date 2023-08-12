# -----------------------------------------------------------------------------
# Company: KARIM Technologies
# Author: Sayed Amir Karim
# Copyright: 2023 KARIM Technologies
#
# License: All Rights Reserved
#
# Module: PHControl
# Version: 1.1
# Description: Dieses Modul stellt die PHControl-Klasse bereit, die eine
# automatisierte Kontrolle des pH-Wertes in einem System ermöglicht. Sie
# ermöglicht die automatische Regelung eines CO2-Ventils und einer Pumpe
# basierend auf dem gemessenen pH-Wert und Benutzereingaben. 
# -----------------------------------------------------------------------------

import time
import threading

class PHControl:
    def __init__(self, min_ph, max_ph, check_timer, on_delay_timer, pump_start_delay=0):
        self.min_ph = min_ph
        self.max_ph = max_ph
        self.check_timer = check_timer
        self.on_delay_timer = on_delay_timer
        self.pump_start_delay = pump_start_delay
        self.measured_ph = None
        self.pump_switch = False
        self.co2_valve_switch = None
        self.co2_valve_status = False
        self.pump_status = False

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

    def get_pump_switch(self):
        return self.pump_switch

    def get_co2_valve_switch(self):
        return self.co2_valve_switch

    def get_co2_valve_status(self):
        return self.co2_valve_status

    def get_pump_status(self):
        return self.pump_status

    def control_loop(self):
        while True:
            # Steuerung der Pumpe
            if self.pump_switch:
                time.sleep(self.pump_start_delay)
                self.pump_status = True
            else:
                self.pump_status = False

            # Manuelle Steuerung des CO2-Ventils
            if self.co2_valve_switch is not None:
                self.co2_valve_status = self.co2_valve_switch
            # Automatische Steuerung des CO2-Ventils
            elif self.measured_ph is not None and self.measured_ph > self.max_ph:
                time.sleep(self.on_delay_timer)

                # Nach der Wartezeit, überprüfen wir erneut den PH-Wert
                if self.measured_ph > self.max_ph:
                    self.co2_valve_status = True

                    # Kontinuierliche Überprüfung, ob der PH-Wert sinkt
                    while self.measured_ph > self.max_ph:
                        time.sleep(1)

                    # Sobald der PH-Wert unter dem max_ph liegt, starten wir den check_timer
                    start_time = time.time()
                    while time.time() - start_time < self.check_timer:
                        if self.measured_ph > self.max_ph:
                            break
                        time.sleep(1)
                    else:
                        self.co2_valve_status = False

            time.sleep(1)
