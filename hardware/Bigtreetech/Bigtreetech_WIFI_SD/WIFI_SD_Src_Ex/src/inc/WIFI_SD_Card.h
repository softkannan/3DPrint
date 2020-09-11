#ifndef WIFI_SD_Card_h
#define WIFI_SD_Card_h

#include "../Utility/Utility.h"

#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <LittleFS.h>

#ifdef DBG_PRINTLN
  #undef DBG_INIT
  #undef DBG_PRINT
  #undef DBG_PRINTLN
  // #define DBG_INIT(...)    { Serial1.begin(__VA_ARGS__); }
  // #define DBG_PRINT(...)     { Serial1.print(__VA_ARGS__); }
  // #define DBG_PRINTLN(...)   { Serial1.println(__VA_ARGS__); }
  #define DBG_INIT(...)   {}
  #define DBG_PRINT(...)    {}
  #define DBG_PRINTLN(...)  {}
#endif

#endif