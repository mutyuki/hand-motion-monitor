#include <Wire.h>
#include "KX122.h"

KX122 kx122(KX122_DEVICE_ADDRESS_1F);
const char HAND_ID = 'R';

void setup() {
  byte rc;

  Serial.begin(115200);
  while (!Serial);

  Wire.begin();

  rc = kx122.init();
  if (rc != 0) {
    Serial.println("ERROR,KX122 init failed");
  }
}

void loop() {
  float acc[3];
  byte rc = kx122.get_val(acc);

  if (rc == 0) {
    // 形式: R,ax,ay,az
    Serial.print(HAND_ID);
    Serial.print(",");
    Serial.print(acc[0], 4);
    Serial.print(",");
    Serial.print(acc[1], 4);
    Serial.print(",");
    Serial.println(acc[2], 4);
  }

  delay(50);  // 約20Hz
}
