
// Using the WebDAV server with Rigidbot 3D printer.
// Printer controller is a variation of Rambo running Marlin firmware
//======================================================================================================
// Changed 20.03.2020 by Shirokov V.V. aka Massaraksh7
//
// - Reading in setup() section file setup.ini in the root directory of SD-card and find out two strings:
//   Ssid=*****      with the name of Wifi-net
//   Password=*****  with the password
// - \\192.168.0.110\DavWWWRoot, enter in windows file explorer
// - add functions: ReadLine
//                  DivideStr
//======================================================================================================
#include "inc/Common.h"
#include "inc/WIFI_SD_Card.h"
#include "ESPWebDAV/ESPWebDAVEx.h"
#include <ESP8266NetBIOS.h>

char          g_WIFI_SSID[MAX_STR_BUFF_SIZE];
char      g_WIFI_Password[MAX_STR_BUFF_SIZE];
char      g_WIFI_HostName[MAX_STR_BUFF_SIZE];

ESPWebDAVEx DAV;

// ------------------------
void setup() {


  // --- Serial ---
  Serial.begin(OUTPUT_SERIAL_BAUD);
  PRINT_OUT_LN(OUTPUT_SERIAL_BAUD);
  PRINT_OUT_LN_PGM("");
  INIT_LED;
  blink();
  PRINT_OUT_LN_PGM("Initializing...");

  DAV.Init_EXT_SD_Card();
  
  g_WIFI_HostName[0] = 0;
  g_WIFI_SSID[0] = 0;
  g_WIFI_Password[0] = 0;
  
  if(DAV.Get_WIFI_Config(g_WIFI_HostName,g_WIFI_SSID,g_WIFI_Password)) {
    return;
  }

  // ----- WIFI -------
  // Set hostname first
  WiFi.persistent(false);
  WiFi.hostname(g_WIFI_HostName);
  // Reduce startup surge current
  WiFi.setAutoConnect(false);
  WiFi.mode(WIFI_OFF);
  WiFi.mode(WIFI_STA);
  WiFi.setPhyMode(WIFI_PHY_MODE_11N);
  WiFi.begin(g_WIFI_SSID, g_WIFI_Password);

  // Wait for connection
  while(WiFi.status() != WL_CONNECTED) {
    blink();
    PRINT_OUT_PGM(".");
  }

  PRINT_OUT_LN_PGM("");
  PRINT_OUT_PGM("Host name: ");PRINT_OUT_LN(g_WIFI_HostName);
  PRINT_OUT_PGM("Connected to: ");PRINT_OUT_LN(g_WIFI_SSID);
  PRINT_OUT_PGM("IP address: "); PRINT_OUT_LN(WiFi.localIP());
  PRINT_OUT_PGM("RSSI: "); PRINT_OUT_LN(WiFi.RSSI());
  PRINT_OUT_PGM("Mode: "); PRINT_OUT_LN(WiFi.getPhyMode());


  DAV.Init_WebDAV_Server_noSD();

  MDNS.begin(g_WIFI_HostName);
  NBNS.begin(g_WIFI_HostName);
}

// ------------------------
void loop() {
  MDNS.update();
  DAV.Loop();
}