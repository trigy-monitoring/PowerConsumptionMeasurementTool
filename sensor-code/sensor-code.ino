#include "Wire.h"
#include "Adafruit_INA219.h"

Adafruit_INA219 ina219(0x40);

void setup() {
  Serial.begin(9600);
  while (!Serial) {}

  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) {
      delay(10);
    }
  }
}

void loop() {
  Serial.print(millis());
  Serial.print(" ");
  Serial.print(ina219.getCurrent_mA());
  Serial.print(" ");
  Serial.println(ina219.getPower_mW());
  delay(1);
}
