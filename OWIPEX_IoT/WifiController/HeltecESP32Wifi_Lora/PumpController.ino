#include <WiFi.h>
#include <ThingsBoard.h>
#include <DallasTemperature.h>


constexpr char WIFI_SSID[] = "OWIPEX_4G_0001";
constexpr char WIFI_PASSWORD[] = "12345678";
constexpr char THINGSBOARD_SERVER[] = "192.168.100.26";
//constexpr char WIFI_SSID[] = "FamMorbius";
//constexpr char WIFI_PASSWORD[] = "45927194145938492747";
//constexpr char THINGSBOARD_SERVER[] = "192.168.178.54";
constexpr char TOKEN[] = "123456";
constexpr uint16_t THINGSBOARD_PORT = 1883U;
constexpr uint32_t MAX_MESSAGE_SIZE = 256U;

// Define the GPIO pins for your relays
constexpr int PUMP_RELAY_PIN = 1;
constexpr int SEC_RELAY_PIN = 2;

// Attribute names for attribute request and attribute updates functionality
constexpr char PUMP_RELAY_ATTR[] = "pumpRelais";
constexpr char SEC_RELAY_ATTR[] = "addRelais";

// List of shared attributes for subscribing to their updates
constexpr std::array<const char *, 2U> SHARED_ATTRIBUTES_LIST = {
  PUMP_RELAY_ATTR,
  SEC_RELAY_ATTR
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
    if (strcmp(it->key().c_str(), PUMP_RELAY_ATTR) == 0) {
      digitalWrite(PUMP_RELAY_PIN, it->value().as<bool>() ? LOW : HIGH);
    } else if(strcmp(it->key().c_str(), SEC_RELAY_ATTR) == 0) {
      digitalWrite(SEC_RELAY_PIN, it->value().as<bool>() ? LOW : HIGH);
    }
  }
}

const Shared_Attribute_Callback attributes_callback(SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend(), &processSharedAttributes);

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(SEC_RELAY_PIN, OUTPUT);
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

  tb.loop();
}
