#include "Wire.h"
#include "Adafruit_INA219.h"

Adafruit_INA219 ina219(0x40);

#define READING_TIME 90000

long reads = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial) {delay(10);}
  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) {
      delay(10);
    }
  }

  printMeasurement();
}

void loop() {
  if (millis() <= READING_TIME) {
    printMeasurement();
  }

  reads++;
  delay(1);
}

void printMeasurement()
{
  Serial.print(String(millis()) + " " + String(ina219.getCurrent_mA()) + " " + String(ina219.getPower_mW()) + "\n");
}
