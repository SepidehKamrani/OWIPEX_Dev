import json

class PHLogic:
    def __init__(self, ph_sensor):
        self.ph_sensor = ph_sensor
        self.low_reading = None
        self.high_reading = None
        self.m = None
        self.b = None
        self.kalibMessage = ""

    def get_ph_values_from_json(self, temperaturPHSens_telem):
        try:
            with open("ph_calibration_data.json", "r") as f:
                data = json.load(f)
                return data.get(temperaturPHSens_telem, {}).get("knownPH_Low"), data.get(temperaturPHSens_telem, {}).get("knownPH_High")
        except Exception as e:
            self.kalibMessage = f"Fehler beim Lesen der JSON-Datei: {e}"
            return None, None

    def calibrate_low(self, temperaturPHSens_telem, confirmation=False):
        if confirmation:
            self.low_reading = self.ph_sensor.read()
            knownPH_Low, _ = self.get_ph_values_from_json(temperaturPHSens_telem)
            if knownPH_Low is not None:
                self.kalibMessage = f"Kalibrierung für niedrigen pH-Wert {knownPH_Low} abgeschlossen. Gelesener Wert: {self.low_reading}."
            else:
                self.kalibMessage = "Fehler: knownPH_Low konnte nicht aus der JSON-Datei gelesen werden."
        else:
            self.kalibMessage = "Kalibrierung für niedrigen pH-Wert abgebrochen."

    def calibrate_high(self, temperaturPHSens_telem, confirmation=False):
        if confirmation:
            self.high_reading = self.ph_sensor.read()
            _, knownPH_High = self.get_ph_values_from_json(temperaturPHSens_telem)
            if knownPH_High is not None:
                self.kalibMessage = f"Kalibrierung für hohen pH-Wert {knownPH_High} abgeschlossen. Gelesener Wert: {self.high_reading}."
            else:
                self.kalibMessage = "Fehler: knownPH_High konnte nicht aus der JSON-Datei gelesen werden."
        else:
            self.kalibMessage = "Kalibrierung für hohen pH-Wert abgebrochen."

    def get_current_ph(self):
        return self.ph_sensor.read()

    def calculate_slope_and_intercept(self):
        knownPH_Low, knownPH_High = self.get_ph_values_from_json(self.temperaturPHSens_telem)
        if knownPH_Low is not None and knownPH_High is not None:
            self.m = (knownPH_High - knownPH_Low) / (self.high_reading - self.low_reading)
            self.b = knownPH_High - self.m * self.high_reading
            self.kalibMessage = f"Steigung (m): {self.m}, y-Achsenabschnitt (b): {self.b}"
        else:
            self.kalibMessage = "Fehler: knownPH_Low oder knownPH_High konnte nicht aus der JSON-Datei gelesen werden."

    def get_real_ph(self, measured_ph):
        if self.m is not None and self.b is not None:
            return self.m * measured_ph + self.b
        else:
            self.kalibMessage = "Fehler: Bitte kalibrieren Sie zuerst."
            return None

# Hier können Sie weitere Funktionen oder Methoden hinzufügen, wenn nötig.
