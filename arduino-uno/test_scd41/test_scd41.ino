
#include <Wire.h>
#include <SensirionI2cScd4x.h>
#include <LiquidCrystal_I2C.h>
#include <avr/pgmspace.h>

// LCD Configuration for 2004 I2C LCD
#define LCD_ADDRESS 0x27  // Common address for 2004 I2C LCD
#define LCD_COLUMNS 20
#define LCD_ROWS 4

const uint8_t SCD41_ADDRESS = 0x62;

SensirionI2cScd4x scd4x;
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLUMNS, LCD_ROWS);

uint16_t co2;
float temperature;
float humidity;

// Serial data output control
unsigned long lastSerialOutput = 0;
const unsigned long serialOutputInterval = 2000; // Send data every 2 seconds

// LCD control
unsigned long lastDisplayUpdate = 0;
const unsigned long displayInterval = 2000; // Update LCD every 2 seconds
bool lcdAvailable = false;

// Note: Relay control moved to Raspberry Pi
// Arduino acts as sensor hub only


bool detectI2CDevice(uint8_t address);
void sendSensorData();

// Mushroom growing modes
enum GrowingMode {
  SPAWNING,
  FRUITING
};

GrowingMode currentMode = SPAWNING; // Default to spawning mode
bool alertActive = false;
unsigned long lastAlertTime = 0;
const unsigned long alertInterval = 10000; // Alert every 10 seconds
const unsigned long measurementInterval = 5000; // Sensor measurement interval
unsigned long lastMeasurementTime = 0;
bool sensorAvailable = true;

// CO2 thresholds for different modes
const int SPAWNING_MIN_CO2 = 10000; // ppm
const int FRUITING_MIN_CO2 = 500;   // ppm
const int FRUITING_MAX_CO2 = 800;   // ppm

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    delay(100);
  }

  // Initialize serial communication
  Serial.println(F("=== MASH IoT Device - Arduino Uno Sensor Hub ==="));
  Serial.println(F("Initializing I2C bus and LCD..."));

  Wire.begin();

  if (!detectI2CDevice(LCD_ADDRESS)) {
    lcdAvailable = false;
    Serial.println(F("WARNING: LCD not detected"));
  } else {
    lcdAvailable = true;
    lcd.init();
    lcd.backlight();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(F("Initializing..."));
  }

  Serial.println(F("Initializing SCD41 sensor..."));

  if (!detectI2CDevice(SCD41_ADDRESS)) {
    Serial.println(F("ERROR: SCD41 sensor not detected on I2C bus (0x62)"));
    sensorAvailable = false;
    while (true) {
      delay(10);
    }
  }

  scd4x.begin(Wire, SCD41_ADDRESS);

  uint16_t error;
  char errorMessage[128];

  error = scd4x.stopPeriodicMeasurement();
  if (error) {
    Serial.print(F("Error trying to execute stopPeriodicMeasurement(): "));
    errorToString(error, errorMessage, 128);
    Serial.println(errorMessage);
    Serial.println(F("ERROR: Failed to stop periodic measurement"));

    while (true) {
      delay(10);
    }
  }

  error = scd4x.startPeriodicMeasurement();
  if (error) {
    Serial.print(F("Error trying to execute startPeriodicMeasurement(): "));
    Serial.println(error);
    Serial.println(F("ERROR: Failed to start periodic measurement"));

    while (true) {
      delay(10);
    }
  } else {
    Serial.println(F("SUCCESS: SCD41 sensor initialized!"));
    Serial.println(F("Sensor is ready for measurements"));
  }

  Serial.println(F("Waiting for first measurement... (5-10 seconds)"));
  Serial.println(F("Commands: 's'=Spawning, 'f'=Fruiting"));
  Serial.println(F("Data Format: SENSOR,timestamp,co2,temp,humidity,mode"));
  Serial.println(F("================================================"));
}

void loop() {
  // Check for serial commands
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 's') {
      currentMode = SPAWNING;
      Serial.println(F("MODE,SPAWNING"));
      alertActive = false;
    } else if (command == 'f') {
      currentMode = FRUITING;
      Serial.println(F("MODE,FRUITING"));
      alertActive = false;
    }
  }

  // Update LCD display periodically
  if (lcdAvailable && millis() - lastDisplayUpdate >= displayInterval) {
    updateLCDDisplay();
    lastDisplayUpdate = millis();
  }

  if (millis() - lastMeasurementTime >= measurementInterval) {
    lastMeasurementTime = millis();

    uint16_t error;
    char errorMessage[128];

    error = scd4x.readMeasurement(co2, temperature, humidity);
    if (error) {
      Serial.print(F("Error trying to execute readMeasurement(): "));
      errorToString(error, errorMessage, 128);
      Serial.println(errorMessage);
      Serial.println(F("ERROR: Sensor communication failed - check connections"));
    } else if (co2 == 0) {
      Serial.println(F("Invalid sample detected, skipping."));
      Serial.println(F("Please wait for sensor stabilization..."));
    } else {
      // Check for CO2 alerts based on current mode
      checkCO2Alerts(co2);
      
      // Send structured data at controlled intervals
      if (millis() - lastSerialOutput >= serialOutputInterval) {
        sendSensorData();
        lastSerialOutput = millis();
      }
    }
  }
}

// Check CO2 levels and trigger alerts based on current mode
void checkCO2Alerts(uint16_t co2Level) {
  bool shouldAlert = false;
  
  if (currentMode == SPAWNING) {
    if (co2Level < SPAWNING_MIN_CO2) {
      shouldAlert = true;
    }
  } else if (currentMode == FRUITING) {
    if (co2Level < FRUITING_MIN_CO2 || co2Level > FRUITING_MAX_CO2) {
      shouldAlert = true;
    }
  }
  
  // Show alert if conditions are met and enough time has passed
  if (shouldAlert && (millis() - lastAlertTime >= alertInterval)) {
    // Send alert to Raspberry Pi
    Serial.print(F("ALERT,"));
    Serial.print(millis());
    Serial.print(F(","));
    Serial.print(currentMode == SPAWNING ? F("SPAWNING") : F("FRUITING"));
    Serial.print(F(","));
    Serial.println(co2Level);
    
    lastAlertTime = millis();
    alertActive = true;

    // Alert sent to Raspberry Pi
  } else if (!shouldAlert) {
    alertActive = false;
  }

}

bool detectI2CDevice(uint8_t address) {
  Wire.beginTransmission(address);
  return Wire.endTransmission() == 0;
}

void sendSensorData() {
  // Format: SENSOR,timestamp,co2,temperature,humidity,mode,alert
  Serial.print(F("SENSOR,"));
  Serial.print(millis());
  Serial.print(F(","));
  Serial.print(co2);
  Serial.print(F(","));
  Serial.print(temperature, 2);
  Serial.print(F(","));
  Serial.print(humidity, 2);
  Serial.print(F(","));
  Serial.print(currentMode == SPAWNING ? F("SPAWNING") : F("FRUITING"));
  Serial.print(F(","));
  Serial.println(alertActive ? F("1") : F("0"));
}

void updateLCDDisplay() {
  lcd.clear();
  
  // Line 1: Mode and CO2
  lcd.setCursor(0, 0);
  lcd.print(currentMode == SPAWNING ? F("SPAWN") : F("FRUIT"));
  lcd.print(F(" CO2:"));
  if (co2 > 0) {
    lcd.print(co2);
    lcd.print(F("ppm"));
  } else {
    lcd.print(F("----ppm"));
  }
  
  // Line 2: Temperature and Humidity
  lcd.setCursor(0, 1);
  lcd.print(F("T:"));
  lcd.print(temperature, 1);
  lcd.print(F("C H:"));
  lcd.print(humidity, 1);
  lcd.print(F("%"));
  
  // Line 3: Status
  lcd.setCursor(0, 2);
  if (alertActive) {
    lcd.print(F("ALERT ACTIVE"));
  } else {
    lcd.print(F("System OK"));
  }
  
  // Line 4: Timestamp
  lcd.setCursor(0, 3);
  unsigned long seconds = millis() / 1000;
  unsigned long minutes = seconds / 60;
  unsigned long hours = minutes / 60;
  if (hours > 0) {
    lcd.print(hours);
    lcd.print(F("h"));
  }
  if (minutes % 60 > 0) {
    lcd.print(minutes % 60);
    lcd.print(F("m"));
  }
  if (seconds % 60 > 0) {
    lcd.print(seconds % 60);
    lcd.print(F("s"));
  }
}
