#include <Wire.h>

TwoWire Sensor1Wire = TwoWire(0);
TwoWire Sensor2Wire = TwoWire(1);

#define DEVICE_ADDRESS 0x6D
#define PRESSURE_RANGE 500.0 // kPa
#define VOLUME 10.0 // Liter, ändern Sie dies entsprechend dem Volumen Ihrer Gasflasche
#define R 8.314 // J/(mol·K)
#define M 0.04401 // kg/mol

void setup() {
  //Sensor1Wire.begin(19, 20);
  Sensor1Wire.begin(18, 17);
  Sensor2Wire.begin(33, 34);
  
  USBSerial.begin(115200);
}

void loop() {
  float pressure1 = readPressure(Sensor1Wire); // in kPa
  float temperature1 = readTemperature(Sensor1Wire); // in °C
  
  float pressure2 = readPressure(Sensor2Wire); // in kPa
  float temperature2 = readTemperature(Sensor2Wire); // in °C

  float pressureBar1 = pressure1 / 100.0; // Umrechnung in Bar
  float mass1 = calculateMass(pressure1, temperature1, VOLUME); // Berechnung der Masse in kg

  float pressureBar2 = pressure2 / 100.0; // Umrechnung in Bar

  USBSerial.print("Sensor 1 - Druck: ");
  USBSerial.print(pressureBar1);
  USBSerial.print(" bar, Temperatur: ");
  USBSerial.print(temperature1);
  USBSerial.println(" °C");

  USBSerial.print("CO2 Masse: ");
  USBSerial.print(mass1);
  USBSerial.println(" kg");

  USBSerial.print("Sensor 2 (Kontrollsensor) - Druck: ");
  USBSerial.print(pressureBar2);
  USBSerial.print(" bar, Temperatur: ");
  USBSerial.print(temperature2);
  USBSerial.println(" °C");

  delay(1000);
}

float readPressure(TwoWire &wire) {
  wire.beginTransmission(DEVICE_ADDRESS);
  wire.write(0x06);
  wire.endTransmission(false);

  wire.requestFrom(DEVICE_ADDRESS, 3);

  if (wire.available() == 3) {
    long dat = wire.read() << 16 | wire.read() << 8 | wire.read();
    if (dat & 0x800000) {
      dat = dat - 16777216;
    }
    float fadc = dat;
    float adc = 3.3 * fadc / 8388608.0;
    float pressure = PRESSURE_RANGE * (adc - 0.5) / 2.0;
    return pressure;
  }
  return NAN;
}

float readTemperature(TwoWire &wire) {
  wire.beginTransmission(DEVICE_ADDRESS);
  wire.write(0x09);
  wire.endTransmission(false);

  wire.requestFrom(DEVICE_ADDRESS, 3);

  if (wire.available() == 3) {
    long dat = wire.read() << 16 | wire.read() << 8 | wire.read();
    if (dat & 0x800000) {
      dat = dat - 16777216;
    }
    float fadc = dat;
    float temperature = 25.0 + fadc / 65536.0;
    return temperature;
  }
  return NAN;
}

float calculateMass(float pressure, float temperature, float volume) {
  float pressurePa = pressure * 1000.0; // Umrechnung in Pa
  float temperatureK = temperature + 273.15; // Umrechnung in Kelvin
  float volumeM3 = volume / 1000.0; // Umrechnung von Liter in m³
  
  float mass = (pressurePa * volumeM3 * M) / (R * temperatureK);
  return mass;
}
