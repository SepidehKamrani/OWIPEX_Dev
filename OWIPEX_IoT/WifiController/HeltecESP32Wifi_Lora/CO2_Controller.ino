#include <WiFi.h>
#include <ThingsBoard.h>
#include <DallasTemperature.h>

constexpr char WIFI_SSID[] = "RUT240_AE4E";
constexpr char WIFI_PASSWORD[] = "Jj34CkNd";
constexpr char TOKEN[] = "1234567";
constexpr char THINGSBOARD_SERVER[] = "192.168.1.235";
constexpr uint16_t THINGSBOARD_PORT = 1883U;
constexpr uint32_t MAX_MESSAGE_SIZE = 256U;

//oneWireTempSensor
#define SENSOR_PIN  4
OneWire oneWire(SENSOR_PIN);
DallasTemperature DS18B20(&oneWire);
float co2temperature; // temperature in Celsius


//pressureSensor
const int analogPin = 7;
int analogValue = 0;

// Define the GPIO pins for your relays
constexpr int CO2_RELAY_PIN = 34;
constexpr int HEATING_RELAY_PIN = 35;

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

void InitWiFi() {
  Serial.println("Connecting to AP ...");
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
  Serial.begin(115200);
  pinMode(CO2_RELAY_PIN, OUTPUT);
  pinMode(HEATING_RELAY_PIN, OUTPUT);
  digitalWrite(CO2_RELAY_PIN, true);
  digitalWrite(HEATING_RELAY_PIN, true);
  

  delay(1000);
  InitWiFi();
}

void loop() {
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
      Serial.println("Failed to subscribe for shared attribute updates");
      return;
    }
    subscribed = true;
  }

  // Sending telemetry every telemetrySendInterval time
  if (millis() - previousDataSend > telemetrySendInterval) {
    previousDataSend = millis();
    tb.sendAttributeInt("rssi", WiFi.RSSI());
    tb.sendAttributeInt("channel", WiFi.channel());
    tb.sendAttributeString("bssid", WiFi.BSSIDstr().c_str());
    tb.sendAttributeString("localIp", WiFi.localIP().toString().c_str());
    tb.sendAttributeString("ssid", WiFi.SSID().c_str());
  }

  analogValue = analogRead(analogPin);
  DS18B20.requestTemperatures();       // send the command to get temperatures
  co2temperature = DS18B20.getTempCByIndex(0);  // read temperature in °C
  
  tb.loop();
}
