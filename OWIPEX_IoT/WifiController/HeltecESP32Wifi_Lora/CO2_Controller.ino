#include <Wire.h>
#include <WiFi.h>
#include <ThingsBoard.h>
#include <DallasTemperature.h>


//constexpr char WIFI_SSID[] = "FamMorbius";
//constexpr char WIFI_PASSWORD[] = "45927194145938492747";
//constexpr char THINGSBOARD_SERVER[] = "192.168.178.54";
constexpr char WIFI_SSID[] = "OWIPEX_4G_0001";
constexpr char WIFI_PASSWORD[] = "12345678";
constexpr char THINGSBOARD_SERVER[] = "192.168.100.26";
constexpr char TOKEN[] = "12345678";
constexpr uint16_t THINGSBOARD_PORT = 1883U;
constexpr uint32_t MAX_MESSAGE_SIZE = 256U;

// Define the GPIO pins for your relays
constexpr int CO2_RELAY_PIN = 1;
constexpr int HEATING_RELAY_PIN = 3;

// Attribute names for attribute request and attribute updates functionality
constexpr char CO2_RELAY_ATTR[] = "co2Relay";
constexpr char HEATING_RELAY_ATTR[] = "heatingRelay";

// List of shared attributes for subscribing to their updates
constexpr std::array<const char *, 2U> SHARED_ATTRIBUTES_LIST = {
  CO2_RELAY_ATTR,
  HEATING_RELAY_ATTR
};

WiFiClient wifiClient;
ThingsBoard tb(wifiClient, MAX_MESSAGE_SIZE);

// For telemetry
constexpr int16_t telemetrySendInterval = 2000U;
uint32_t previousDataSend;

bool subscribed = false;


TwoWire Sensor1Wire = TwoWire(0);
TwoWire Sensor2Wire = TwoWire(1);

#define DEVICE_ADDRESS 0x6D
#define PRESSURE_RANGE 500.0 // kPa
#define VOLUME 10.0 // Liter, ändern Sie dies entsprechend dem Volumen Ihrer Gasflasche
#define R 8.314 // J/(mol·K)
#define M 0.04401 // kg/mol

void InitWiFi() {
  USBSerial.println("Connecting to AP ...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to AP");
}

void processSharedAttributes(const Shared_Attribute_Data &data) {
  for (auto it = data.begin(); it != data.end(); ++it) {
    if (strcmp(it->key().c_str(), CO2_RELAY_ATTR) == 0) {
      digitalWrite(CO2_RELAY_PIN, it->value().as<bool>() ? HIGH : LOW);
    } else if(strcmp(it->key().c_str(), HEATING_RELAY_ATTR) == 0) {
      digitalWrite(HEATING_RELAY_PIN, it->value().as<bool>() ? HIGH : LOW);
    }
  }
}

const Shared_Attribute_Callback attributes_callback(SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend(), &processSharedAttributes);

void setup() {
  Sensor1Wire.begin(17, 16);
  Sensor2Wire.begin(15, 7);
  USBSerial.begin(115200);
  pinMode(CO2_RELAY_PIN, OUTPUT);
  pinMode(HEATING_RELAY_PIN, OUTPUT);
  digitalWrite(CO2_RELAY_PIN, false);
  digitalWrite(HEATING_RELAY_PIN, false);
  delay(1000);
  InitWiFi();
}

void loop() {

  float pressure1 = readPressure(Sensor1Wire); // in kPa
  float temperature1 = readTemperature(Sensor1Wire); // in °C
  
  float pressure2 = readPressure(Sensor2Wire); // in kPa
  float temperature2 = readTemperature(Sensor2Wire); // in °C

  float pressureBar1 = pressure1 / 100.0; // Umrechnung in Bar
  float mass1 = calculateMass(pressure1, temperature1, VOLUME); // Berechnung der Masse in kg

  float pressureBar2 = pressure2 / 100.0; // Umrechnung in Bar

  

  if (!tb.connected()) {
    if (!tb.connect(THINGSBOARD_SERVER, TOKEN, THINGSBOARD_PORT)) {
      Serial.println("Failed to connect");
      subscribed = false;
      return;
    }
    tb.sendAttributeString("macAddress", WiFi.macAddress().c_str());
  }

  if (!subscribed) {
    if (!tb.Shared_Attributes_Subscribe(attributes_callback)) {
      USBSerial.println("Failed to subscribe for shared attribute updates");
      return;
    }
    subscribed = true;
  }

  // Sending telemetry every telemetrySendInterval time
  if (millis() - previousDataSend > telemetrySendInterval) {
    previousDataSend = millis();
    tb.sendTelemetryInt("pressureBar1", pressureBar1);
    tb.sendTelemetryInt("temperature1", temperature1);  // Replace with your temperature sensor reading
    tb.sendTelemetryInt("pressureBar2", pressure2);  // Replace with your temperature sensor reading
    tb.sendTelemetryInt("temperature2", temperature2);  // Replace with your temperature sensor reading
    tb.sendTelemetryInt("CO2_MasseKG:", mass1);  // Replace with your temperature sensor reading
    // Replace with your temperature sensor reading
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
  }

  tb.loop();
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
