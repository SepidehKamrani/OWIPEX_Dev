#include "heltec.h"
#include "images.h"
#include <ThingsBoard.h>



#if defined(ESP8266)
  #include <ESP8266WiFi.h>
  #define THINGSBOARD_ENABLE_PROGMEM 0
#elif defined(ARDUINO_NANO_RP2040_CONNECT)
  #include <WiFiNINA_Generic.h>
#elif defined(ESP32) || defined(RASPBERRYPI_PICO) || defined(RASPBERRYPI_PICO_W)
  #include <WiFi.h>
  #include <WiFiClientSecure.h>
#endif

#define THINGSBOARD_ENABLE_PSRAM 0
#define THINGSBOARD_ENABLE_DYNAMIC 1

const int heatingSwitch = 2;
const int valveSwitch = 3;

constexpr char WIFI_SSID[] = "FamMorbius";
constexpr char WIFI_PASSWORD[] = "45927194145938492747";
//constexpr char WIFI_SSID[] = "owipex";
//constexpr char WIFI_PASSWORD[] = "123456789";

constexpr char TOKEN[] = "N7I40ZjN2fG3TywAwMZX";
constexpr char THINGSBOARD_SERVER[] = "192.168.178.51";
constexpr uint16_t THINGSBOARD_PORT = 1883U;
constexpr uint32_t MAX_MESSAGE_SIZE = 256U;
constexpr uint32_t SERIAL_DEBUG_BAUD = 115200U;

WiFiClient wifiClient;
ThingsBoard tb(wifiClient, MAX_MESSAGE_SIZE);

// Attribute names for attribute request and attribute updates functionality
//heating
constexpr char HEATING_INTERVAL_ATTR[] = "heatingInterval";
constexpr char HEATING_MODE_ATTR[] = "heatingMode";
constexpr char HEATING_STATE_ATTR[] = "heatingState";
//VALVE
constexpr char VALVE_MODE_ATTR[] = "valveMode";
constexpr char VALVE_STATE_ATTR[] = "valveState";


// Statuses for subscribing to rpc
bool subscribed = false;

// handle heating state and mode changes
volatile bool attributesChanged = false;

// heating modes: 0 - continious state, 1 - heatingState
volatile int heatingMode = 0;

// Current state
//heating
volatile bool heatingState = false;
//valve
volatile bool valveState = false;


// Settings for interval in heating mode
constexpr uint16_t HEATING_INTERVAL_MS_MIN = 10U;
constexpr uint16_t HEATING_INTERVAL_MS_MAX = 60000U;
volatile uint16_t heatingInterval = 1000U;


uint32_t previousStateChange;

// For telemetry
constexpr int16_t telemetrySendInterval = 2000U;
uint32_t previousDataSend;

// List of shared attributes for subscribing to their updates
constexpr std::array<const char *, 3U> SHARED_ATTRIBUTES_LIST = {
  HEATING_STATE_ATTR,
  HEATING_INTERVAL_ATTR,
  VALVE_STATE_ATTR
};

// List of client attributes for requesting them (Using to initialize device states)
constexpr std::array<const char *, 1U> CLIENT_ATTRIBUTES_LIST = {
  HEATING_MODE_ATTR,
  
};

/// @brief Initalizes WiFi connection,
// will endlessly delay until a connection has been successfully established
void InitWiFi() {
  Serial.println("Connecting to AP ...");
  // Attempting to establish a connection to the given WiFi network
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    // Delay 500ms until a connection has been succesfully established
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to AP");
}

/// @brief Reconnects the WiFi uses InitWiFi if the connection has been removed
/// @return Returns true as soon as a connection has been established again
const bool reconnect() {
  // Check to ensure we aren't connected yet
  const wl_status_t status = WiFi.status();
  if (status == WL_CONNECTED) {
    return true;
  }

  // If we aren't establish a new connection to the given WiFi network
  InitWiFi();
  return true;
}


/// @brief Processes function for RPC call "setheatingMode"
/// RPC_Data is a JSON variant, that can be queried using operator[]
/// See https://arduinojson.org/v5/api/jsonvariant/subscript/ for more details
/// @param data Data containing the rpc data that was called and its current value
/// @return Response that should be sent to the cloud. Useful for getMethods
RPC_Response processSetheatingMode(const RPC_Data &data) {
  Serial.println("Received the set led state RPC method");

  // Process data
  int new_mode = data;

  Serial.print("Mode to change: ");
  Serial.println(new_mode);

  if (new_mode != 0 && new_mode != 1) {
    return RPC_Response("error", "Unknown mode!");
  }

  heatingMode = new_mode;

  attributesChanged = true;

  // Returning current mode
  return RPC_Response("newMode", (int)heatingMode);
}


// Optional, keep subscribed shared attributes empty instead,
// and the callback will be called for every shared attribute changed on the device,
// instead of only the one that were entered instead
const std::array<RPC_Callback, 1U> callbacks = {
  RPC_Callback{ "setheatingMode", processSetheatingMode }
};


/// @brief Update callback that will be called as soon as one of the provided shared attributes changes value,
/// if none are provided we subscribe to any shared attribute change instead
/// @param data Data containing the shared attributes that were changed and their current value
void processSharedAttributes(const Shared_Attribute_Data &data) {
  for (auto it = data.begin(); it != data.end(); ++it) {
    if (strcmp(it->key().c_str(), HEATING_INTERVAL_ATTR) == 0) {
      const uint16_t new_interval = it->value().as<uint16_t>();
      if (new_interval >= HEATING_INTERVAL_MS_MIN && new_interval <= HEATING_INTERVAL_MS_MAX) {
        heatingInterval = new_interval;
        Serial.print("Updated heatingState interval to: ");
        Serial.println(new_interval);
      }
    } else if(strcmp(it->key().c_str(), HEATING_STATE_ATTR) == 0) {
      heatingState = it->value().as<bool>();
      digitalWrite(heatingSwitch, heatingState ? HIGH : LOW);
      Serial.print("Updated state to: ");
      Serial.println(heatingState);
    }
  }
  attributesChanged = true;
}

void processClientAttributes(const Shared_Attribute_Data &data) {
  for (auto it = data.begin(); it != data.end(); ++it) {
    if (strcmp(it->key().c_str(), HEATING_MODE_ATTR) == 0) {
      const uint16_t new_mode = it->value().as<uint16_t>();
      heatingMode = new_mode;
    }
  }
}

const Shared_Attribute_Callback attributes_callback(SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend(), &processSharedAttributes);
const Attribute_Request_Callback attribute_shared_request_callback(SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend(), &processSharedAttributes);
const Attribute_Request_Callback attribute_client_request_callback(CLIENT_ATTRIBUTES_LIST.cbegin(), CLIENT_ATTRIBUTES_LIST.cend(), &processClientAttributes);
//end comunication part


//Machine Definition Part








void setup() {

  //anything that starts with HELTEC is related to the display
  //Heltec.begin(true /*DisplayEnable Enable*/, false /*LoRa Enable*/, true /*Serial Enable*/);
  //Text01
  Heltec.display->setTextAlignment(TEXT_ALIGN_LEFT);
  Heltec.display->setFont(ArialMT_Plain_10);
  Heltec.display->drawString(0, 0, "OWIPEX Remote Controller V0_1");
  delay(2000);
  Heltec.display->clear();
  //loadLogo
  Heltec.display -> drawXbm(0, 0, owipex_width, owipex_height, owipex_bits);
  Heltec.display -> display();
  delay(3000);
  Heltec.display->clear();

  //set font to 16 pt
  Heltec.display->setFont(ArialMT_Plain_16);
  //Heltec.display->drawString(0, 0, "Connecting to OWIPEX_Controller");
  Heltec.display->drawString(0, 0, "OWIPEX_ControllerV0_1");
  Heltec.display->drawString(0, 15, "OWIPEX_IoT_Server");
  Heltec.display->display();
  delay(2000);

  // Initalize serial connection for debugging
  Serial.begin(115200);
  pinMode(heatingSwitch, OUTPUT);
  pinMode(valveSwitch, OUTPUT);
  delay(1000);
  InitWiFi();
}

void loop() {
//  delay(10);
 Heltec.display -> clear();

  if (!reconnect()) {
    subscribed = false;
    return;
  }

  if (!tb.connected()) {
    subscribed = false;
    // Connect to the ThingsBoard
    Serial.print("Connecting to: ");
    Serial.print(THINGSBOARD_SERVER);
    Serial.print(" with token ");
    Serial.println(TOKEN);
    if (!tb.connect(THINGSBOARD_SERVER, TOKEN, THINGSBOARD_PORT)) {
      Serial.println("Failed to connect");
      return;
    }
    // Sending a MAC address as an attribute
    tb.sendAttributeString("macAddress", WiFi.macAddress().c_str());
  }

  if (!subscribed) {
    Serial.println("Subscribing for RPC...");
    // Perform a subscription. All consequent data processing will happen in
    // processSetheatingState() and processSetheatingMode() functions,
    // as denoted by callbacks array.
    if (!tb.RPC_Subscribe(callbacks.cbegin(), callbacks.cend())) {
      Serial.println("Failed to subscribe for RPC");
      return;
    }

    if (!tb.Shared_Attributes_Subscribe(attributes_callback)) {
      Serial.println("Failed to subscribe for shared attribute updates");
      return;
    }

    Serial.println("Subscribe done");
    subscribed = true;

    // Request current states of shared attributes
    if (!tb.Shared_Attributes_Request(attribute_shared_request_callback)) {
      Serial.println("Failed to request for shared attributes");
      return;
    }

    // Request current states of client attributes
    if (!tb.Client_Attributes_Request(attribute_client_request_callback)) {
      Serial.println("Failed to request for client attributes");
      return;
    }
  }

  if (attributesChanged) {
    attributesChanged = false;
    if (heatingMode == 0) {
      previousStateChange = millis();
    }
    tb.sendTelemetryInt(HEATING_MODE_ATTR, heatingMode);
    tb.sendTelemetryBool(HEATING_STATE_ATTR, heatingState);
    tb.sendAttributeInt(HEATING_MODE_ATTR, heatingMode);
    tb.sendAttributeBool(HEATING_STATE_ATTR, heatingState);
  }

  if (heatingMode == 1 && millis() - previousStateChange > heatingInterval) {
    previousStateChange = millis();
    heatingState = !heatingState;
    digitalWrite(heatingSwitch, heatingState);
    tb.sendTelemetryBool(HEATING_STATE_ATTR, heatingState);
    tb.sendAttributeBool(HEATING_STATE_ATTR, heatingState);
    if (heatingSwitch == 2) {
      Serial.print("LED state changed to: ");
      Serial.println(heatingState);
    }
  }

  // Sending telemetry every telemetrySendInterval time
  if (millis() - previousDataSend > telemetrySendInterval) {
    previousDataSend = millis();
    
    tb.sendAttributeInt("rssi", WiFi.RSSI());
    tb.sendAttributeInt("channel", WiFi.channel());
    tb.sendAttributeString("bssid", WiFi.BSSIDstr().c_str());
    tb.sendAttributeString("localIp", WiFi.localIP().toString().c_str());
    tb.sendAttributeString("ssid", WiFi.SSID().c_str());
    
    //pressureSens 
    tb.sendTelemetryFloat("co2Pressure", random(2, 5));
    tb.sendTelemetryFloat("co2temperature", random(-15, 20));
    
   // tb.sendTelemetryInt("co2temperature", random(-15, 20));
    


  }

  tb.loop();
}
