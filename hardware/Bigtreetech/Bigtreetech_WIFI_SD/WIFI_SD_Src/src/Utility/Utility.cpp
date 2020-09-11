#include "Utility.h"

// ------------------------
void blink()  {
// ------------------------
  LED_ON; 
  delay(100); 
  LED_OFF; 
  delay(400);
}

// ------------------------
void errorBlink() {
// ------------------------
  for(int i = 0; i < 100; i++)  {
    LED_ON; 
    delay(50); 
    LED_OFF; 
    delay(50);
  }
}

void serialprintPGM(PGM_P str) {
  while (const char c = pgm_read_byte(str++)) Serial.print(c);
}