// Using the WebDAV server with Rigidbot 3D printer.
// Printer controller is a RUMBA running Marlin firmware

#include <ESP8266WiFi.h>           //https://github.com/esp8266/Arduino
#include <DNSServer.h>            //Local DNS Server used for redirecting all requests to the configuration portal
#include <ESP8266WebServer.h>     //Local WebServer used to serve the configuration portal
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager WiFi Configuration Magic																								  																						  																								
#include <ESPWebDAV.h>           // https://github.com/ardyesp/ESPWebDAV
// LED is connected to GPIO2 on this board
#define INIT_LED			{pinMode(2, OUTPUT);}
#define LED_ON				{digitalWrite(2, LOW);}
#define LED_OFF				{digitalWrite(2, HIGH);}
#define HOSTNAME		"WiFiSDcard"
#define SERVER_PORT		80
#define SPI_BLOCKOUT_PERIOD	20000
#define SD_CS		4
#define MISO		12
#define MOSI		13
#define SCLK		14
#define CS_SENSE	5
#define SPI_SPEED SD_SCK_MHZ(50)

WiFiServer server(80);  //Set web server port number to 80
int serverPort;
String header; // Variable to store the HTTP request
ESPWebDAV dav;
String statusMessage;
bool initFailed = false;
volatile long spiBlockoutTime = 0;
bool weHaveBus = false;
void ICACHE_RAM_ATTR testspi();

void setup() {
  // Detect when other master uses SPI bus
  pinMode(CS_SENSE, INPUT);
  attachInterrupt(digitalPinToInterrupt(CS_SENSE), testspi, FALLING);

  INIT_LED;
  blink();

  // wait for other master to assert SPI bus first
  delay(SPI_BLOCKOUT_PERIOD);
  // Log into access point

  WiFiManager wifiManager;   //Initialize library, in your setup function
  //wifiManager.resetSettings();  // clears logon info for testing
  WiFi.hostname("WiFiSDcard");
  wifiManager.setDebugOutput(false);
  wifiManager.setMinimumSignalQuality(7);
  wifiManager.setRemoveDuplicateAPs(false);
  // wifiManager.setConnectTimeout(60);
  wifiManager.autoConnect("WiFiSDcard", "12345678"); // fallback AP name and password   first parameter is name of access point, second is the password
  wifiManager.setConfigPortalTimeout(180); // it will wait 3 minutes When the time passes, the autoConnect function will return

  // ----- SD Card and Server -------
  // Check to see if other master is using the SPI bus
  while (millis() < spiBlockoutTime)
    blink();

  takeBusControl();

  // start the SD DAV server
  if (!dav.init(SD_CS, SPI_SPEED, SERVER_PORT))		{
    // indicate error on LED
    errorBlink();
    initFailed = true;
  }
  else
    blink();

  relenquishBusControl();
}

void loop() {
  // ------------------------
  if (millis() < spiBlockoutTime)
    blink();

  // do it only if there is a need to read FS
  if (dav.isClientWaiting())	{
    if (initFailed)
      return dav.rejectClient(statusMessage);

    // has other master been using the bus in last few seconds
    if (millis() < spiBlockoutTime)
      return dav.rejectClient("Marlin is reading from SD card");

    // a client is waiting and FS is ready and other SPI master is not using the bus
    takeBusControl();
    dav.handleClient();
    relenquishBusControl();
  }
}

void testspi() {
  if (!weHaveBus)
    spiBlockoutTime = millis() + SPI_BLOCKOUT_PERIOD;
}
// ------------------------
void takeBusControl()	{
  // ------------------------
  weHaveBus = true;
  LED_ON;
  pinMode(MISO, SPECIAL);
  pinMode(MOSI, SPECIAL);
  pinMode(SCLK, SPECIAL);
  pinMode(SD_CS, OUTPUT);
}

// ------------------------
void relenquishBusControl()	{
  // ------------------------
  pinMode(MISO, INPUT);
  pinMode(MOSI, INPUT);
  pinMode(SCLK, INPUT);
  pinMode(SD_CS, INPUT);
  LED_OFF;
  weHaveBus = false;
}

// ------------------------
void blink()	{
  // ------------------------
  LED_ON;
  delay(100);
  LED_OFF;
  delay(400);
}

// ------------------------
void errorBlink()	{
  // ------------------------
  for (int i = 0; i < 100; i++)	{
    LED_ON;
    delay(50);
    LED_OFF;
    delay(50);
  }
}
