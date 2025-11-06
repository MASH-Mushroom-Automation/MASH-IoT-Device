/*
 * MASH IoT Device - Arduino Uno R3 Controller
 * 
 * Reads sensors and controls actuators (relays)
 * Communicates with Raspberry Pi via Serial
 * 
 * Commands from RPi:
 * - "s" = Set Spawning mode
 * - "f" = Set Fruiting mode
 * - "R1:1" = Turn Relay 1 ON
 * - "R1:0" = Turn Relay 1 OFF
 * - "R2:1" = Turn Relay 2 ON
 * - "R2:0" = Turn Relay 2 OFF
 * - "R3:1" = Turn Relay 3 ON
 * - "R3:0" = Turn Relay 3 OFF
 */

#include <DHT.h>

// ========== Pin Definitions ==========
#define DHT_PIN 2          // DHT22 sensor pin
#define CO2_PIN A0         // MQ-135 CO2 sensor pin
#define RELAY_1_PIN 7      // Relay 1 - Humidifier
#define RELAY_2_PIN 8      // Relay 2 - Exhaust Fan
#define RELAY_3_PIN 9      // Relay 3 - Blower Fan

// ========== Sensor Configuration ==========
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

// ========== Global Variables ==========
char currentMode = 's';  // 's' = Spawning, 'f' = Fruiting

// Relay states
bool relay1State = false;  // Humidifier
bool relay2State = false;  // Exhaust Fan
bool relay3State = false;  // Blower Fan

// Sensor reading interval
unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 2000;  // Read every 2 seconds

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize relay pins
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  pinMode(RELAY_3_PIN, OUTPUT);
  
  // Turn off all relays initially (relays are active LOW)
  digitalWrite(RELAY_1_PIN, HIGH);
  digitalWrite(RELAY_2_PIN, HIGH);
  digitalWrite(RELAY_3_PIN, HIGH);
  
  Serial.println("MASH Arduino Controller Initialized");
  Serial.println("Ready to receive commands");
}

void loop() {
  // Read and send sensor data periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= sensorInterval) {
    lastSensorRead = currentMillis;
    readAndSendSensorData();
  }
  
  // Check for incoming commands from RPi
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
}

void readAndSendSensorData() {
  // Read temperature and humidity from DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Read CO2 from MQ-135 (analog value, needs calibration)
  int co2Raw = analogRead(CO2_PIN);
  float co2 = map(co2Raw, 0, 1023, 400, 5000);  // Simple mapping, calibrate as needed
  
  // Check if readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("ERROR:Failed to read from DHT sensor");
    return;
  }
  
  // Send data in format: T:25.5,H:85.2,C:1200
  Serial.print("T:");
  Serial.print(temperature, 1);
  Serial.print(",H:");
  Serial.print(humidity, 1);
  Serial.print(",C:");
  Serial.println(co2, 0);
}

void processCommand(String command) {
  command.toLowerCase();
  
  // Mode commands
  if (command == "s") {
    setMode('s');
  } 
  else if (command == "f") {
    setMode('f');
  }
  // Relay commands (format: R1:1 or R1:0)
  else if (command.startsWith("r")) {
    int colonIndex = command.indexOf(':');
    if (colonIndex > 0) {
      int relayNum = command.substring(1, colonIndex).toInt();
      int state = command.substring(colonIndex + 1).toInt();
      
      controlRelay(relayNum, state == 1);
    }
  }
  else {
    Serial.print("ERROR:Unknown command: ");
    Serial.println(command);
  }
}

void setMode(char mode) {
  currentMode = mode;
  
  if (mode == 's') {
    Serial.println("MODE:Spawning");
    // Spawning mode settings
    // You can add automatic control logic here
  } 
  else if (mode == 'f') {
    Serial.println("MODE:Fruiting");
    // Fruiting mode settings
    // You can add automatic control logic here
  }
}

void controlRelay(int relayNum, bool state) {
  int relayPin;
  bool* relayStatePtr;
  String relayName;
  
  // Select relay
  switch (relayNum) {
    case 1:
      relayPin = RELAY_1_PIN;
      relayStatePtr = &relay1State;
      relayName = "Humidifier";
      break;
    case 2:
      relayPin = RELAY_2_PIN;
      relayStatePtr = &relay2State;
      relayName = "Exhaust Fan";
      break;
    case 3:
      relayPin = RELAY_3_PIN;
      relayStatePtr = &relay3State;
      relayName = "Blower Fan";
      break;
    default:
      Serial.print("ERROR:Invalid relay number: ");
      Serial.println(relayNum);
      return;
  }
  
  // Update relay state (relays are active LOW)
  *relayStatePtr = state;
  digitalWrite(relayPin, state ? LOW : HIGH);
  
  // Send confirmation
  Serial.print("RELAY:");
  Serial.print(relayName);
  Serial.print(":");
  Serial.println(state ? "ON" : "OFF");
}
