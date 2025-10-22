
#include <Wire.h>
#include <SensirionI2cScd4x.h>

SensirionI2cScd4x scd4x;

uint16_t co2;
float temperature;
float humidity;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    delay(100);
  }

  Wire.begin();
  scd4x.begin(Wire, 0x62);

  uint16_t error;
  char errorMessage[256];

  error = scd4x.stopPeriodicMeasurement();
  if (error) {
    Serial.print("Error trying to execute stopPeriodicMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  }

  error = scd4x.startPeriodicMeasurement();
  if (error) {
    Serial.print("Error trying to execute startPeriodicMeasurement(): ");
    Serial.println(error);
  }

  Serial.println("Waiting for first measurement... (5-10 seconds)");
}

void loop() {
  delay(5000);

  uint16_t error;
  char errorMessage[256];

  error = scd4x.readMeasurement(co2, temperature, humidity);
  if (error) {
    Serial.print("Error trying to execute readMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  } else if (co2 == 0) {
    Serial.println("Invalid sample detected, skipping.");
  } else {
    Serial.print("CO2: ");
    Serial.print(co2);
    Serial.print(" ppm\t");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C\t");
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  }
}
