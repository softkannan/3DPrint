#ifndef Utility_h
#define Utility_h

#include "../inc/Common.h"

// LED is connected to GPIO2 on this board
#define INIT_LED      {pinMode(2, OUTPUT);}
#define LED_ON        {digitalWrite(2, LOW);}
#define LED_OFF       {digitalWrite(2, HIGH);}

#define PRINT_OUT_PGM(x)        serialprintPGM(PSTR(x))
#define PRINT_OUT_P(x)          serialprintPGM(x)
#define PRINT_OUT_LN_PGM(x)     (serialprintPGM(PSTR(x)),serialprintPGM(PSTR("\r\n")))
#define PRINT_OUT_LN_P(x)       (serialprintPGM(x),serialprintPGM(PSTR("\r\n")))
#define PRINT_OUT_LN(x)         Serial.println(x)
#define PRINT_OUT(x)            Serial.print(x)


void blink();
void errorBlink();
void serialprintPGM(PGM_P str);

#endif