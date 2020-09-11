// Using the WebDAV server with Rigidbot 3D printer.
// Printer controller is a variation of Rambo running Marlin firmware
//======================================================================================================
// Changed 20.03.2020 by Shirokov V.V. aka Massaraksh7
//
// - Reading in setup() section file setup.ini in the root directory of SD-card and find out two strings:
//   Ssid=*****      with the name of Wifi-net
//   Password=*****  with the password
//
// - add functions: ReadLine
//                  DivideStr
//======================================================================================================

#include <ESP8266WiFi.h>
#include <ESPWebDAV.h>

#include <string>
#include <SdFat.h>
SdFat SD;

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

// LED is connected to GPIO2 on this board
#define INIT_LED      {pinMode(2, OUTPUT);}
#define LED_ON        {digitalWrite(2, LOW);}
#define LED_OFF       {digitalWrite(2, HIGH);}

#define HOSTNAME    "WiFi-SD-Card-3DPrinter"
#define SERVER_PORT   80
#define SPI_BLOCKOUT_PERIOD 20000UL

#define SD_CS   4
#define MISO    12
#define MOSI    13
#define SCLK    14
#define CS_SENSE  5


char ssid[50];
char password[50];
char ss[50];

ESPWebDAV dav;
String statusMessage;
bool initFailed = false;

volatile long spiBlockoutTime = 0;
bool weHaveBus = false;

//------------------------Shirokov V.V. aka Massaraksh7 23.03.2020

File file;

int ReadLine(File* file, char* str, size_t size) {
  char ch;
  int rtn;
  size_t n = 0;
  while (true) {
    // check for EOF
    if (!file->available()) {
      rtn = 0;
      break;
    }
    if (file->read(&ch, 1) != 1) {
      // read error
      rtn = -1;
      break;
    }
    // Delete CR and Space.
    if (ch == '\r' || ch == ' ') {
      continue;
    }
    if (ch == '\n') {
      rtn = 0;
      break;
    }
    if ((n + 1) >= size) {
      // string too long
      rtn = -2;
      n--;
      break;
    }
    str[n++] = ch;
  }
  str[n] = '\0';
  return rtn;
}

void DivideStr(char*str, char*s1, char*s2, char sym)
{
int i,r,n1,n2;
i=-1;n1=0;n2=0;r=0;
while(str[i+1]!=0)
   {
   i++;
   if (str[i]==sym){r++;continue;}
   if (str[i]==' '){continue;}
   if (r==0){s1[n1]=str[i];n1++;continue;}
   if (r==1){s2[n2]=str[i];n2++;continue;}
   }
s1[n1]=0;s2[n2]=0;
}
//=====================================================

// ------------------------
void setup() {
String str1,str2;  
char s1[50],s2[50];
// ------------------------
  // ----- GPIO -------
  // Detect when other master uses SPI bus
  pinMode(CS_SENSE, INPUT);
  attachInterrupt(CS_SENSE, []() {
    if(!weHaveBus)
      spiBlockoutTime = millis() + SPI_BLOCKOUT_PERIOD;
  }, FALLING);
  
  //DBG_INIT(115200);
  //DBG_PRINTLN("");
  Serial.begin(115200);
  Serial.println(115200);
  Serial.println("");
  INIT_LED;
  blink();
  
  // wait for other master to assert SPI bus first
  Serial.println("Delay...");
  delay(SPI_BLOCKOUT_PERIOD);
//------------------------Shirokov V.V. aka Massaraksh7
  if (!SD.begin(SD_CS)) {
    Serial.println("begin SD failed");
    return;
  }
  file = SD.open("SETUP.INI", FILE_READ);
  if (!file) {
    Serial.println("open file failed");
    return;
  }

  for (int i=0;i<2;i++)
     {
     if (ReadLine(&file,ss,50)!=0) { Serial.println("Reading failed!");return;}
     DivideStr(ss,s1,s2,'=');
     str1=String(s1);str2=String(s2);str1.toUpperCase();
     if (str1=="SSID"){str2.toCharArray(ssid,str2.length()+1);}
     if (str1=="PASSWORD"){str2.toCharArray(password,str2.length()+1);}
//     if (str1=="HOSTNAME"){str2.toCharArray(HOSTNAME,s2.length()+1);}     
     }  

  file.close();
//=====================================================

  // ----- WIFI -------
  // Set hostname first
  WiFi.hostname(HOSTNAME);
  // Reduce startup surge current
  WiFi.setAutoConnect(false);
  WiFi.mode(WIFI_STA);
  WiFi.setPhyMode(WIFI_PHY_MODE_11N);
  WiFi.begin(ssid, password);

  // Wait for connection
  while(WiFi.status() != WL_CONNECTED) {
    blink();
    DBG_PRINT(".");
  }

//  DBG_PRINTLN("");
    Serial.print("Connected to ");Serial.println(ssid);
    Serial.print("IP address: "); Serial.println(WiFi.localIP());
//  DBG_PRINT("RSSI: "); DBG_PRINTLN(WiFi.RSSI());
//  DBG_PRINT("Mode: "); DBG_PRINTLN(WiFi.getPhyMode());


  // ----- SD Card and Server -------
  // Check to see if other master is using the SPI bus
  while(millis() < spiBlockoutTime)
    blink();
  
  takeBusControl();
  
  // start the SD DAV server
  if(!dav.init(SD_CS, SPI_FULL_SPEED, SERVER_PORT))   {
    statusMessage = "Failed to initialize SD Card";
    DBG_PRINT("ERROR: "); DBG_PRINTLN(statusMessage);
    // indicate error on LED
    errorBlink();
    initFailed = true;
  }
  else
    blink();

  relenquishBusControl();
  DBG_PRINTLN("WebDAV server started");
}



// ------------------------
void loop() {
// ------------------------
  if(millis() < spiBlockoutTime)
    blink();

  // do it only if there is a need to read FS
  if(dav.isClientWaiting()) {
    if(initFailed)
      return dav.rejectClient(statusMessage);
    
    // has other master been using the bus in last few seconds
    if(millis() < spiBlockoutTime)
      return dav.rejectClient("Marlin is reading from SD card");
    
    // a client is waiting and FS is ready and other SPI master is not using the bus
    takeBusControl();
    dav.handleClient();
    relenquishBusControl();
  }
}



// ------------------------
void takeBusControl() {
// ------------------------
  weHaveBus = true;
  LED_ON;
  pinMode(MISO, SPECIAL); 
  pinMode(MOSI, SPECIAL); 
  pinMode(SCLK, SPECIAL); 
  pinMode(SD_CS, OUTPUT);
}



// ------------------------
void relenquishBusControl() {
// ------------------------
  pinMode(MISO, INPUT); 
  pinMode(MOSI, INPUT); 
  pinMode(SCLK, INPUT); 
  pinMode(SD_CS, INPUT);
  LED_OFF;
  weHaveBus = false;
}




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

