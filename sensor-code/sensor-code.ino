#include "Wire.h"
#include "Adafruit_INA219.h"

Adafruit_INA219 ina219(0x40);

#define RECORDING_FOR_MS 90000

long reads = 0;

void setup() {
  Serial.begin(9600);

  while (!Serial) {
    delay(10);
  }

  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) {
      delay(10);
    }
  }
}

void loop() {
#if RECORDING_FOR_MS == 0
  performMeasurement();
#else
  if (millis() <= RECORDING_FOR_MS) {
    performMeasurement();
  }
#endif

  delay(1);
}

void performMeasurement()
{
  Serial.print(String(millis()) + " " + String(ina219.getCurrent_mA()) + " " + String(ina219.getPower_mW()) + "\n");
  reads++;
}
