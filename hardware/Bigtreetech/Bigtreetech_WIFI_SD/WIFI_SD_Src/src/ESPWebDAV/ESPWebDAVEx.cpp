#define FS_NO_GLOBALS
#include "ESPWebDAVEx.h"
#include <SdFat.h>
#include "ESPWebDAV.h"
#include "../Utility/Utility.h"

#define SD_CS       4
#define MISO        12
#define MOSI        13
#define SCLK        14
#define CS_SENSE    5
#define SPI_SPEED   SD_SCK_MHZ(50)

SdFat sd;
ESPWebDAV g_dav;

String    g_StatusMsg;
bool      g_InitFailed = false;

volatile unsigned long g_SPI_BlockoutTime = 0;
bool g_bWeHaveBus = false;

// ------------------------
void takeBusControl() {
// ------------------------
  g_bWeHaveBus = true;
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
  g_bWeHaveBus = false;
}

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
// devides the '=' sign
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
// SD Card interrupt handler
void ICACHE_RAM_ATTR SD_CARD_CS_SENSE_HANDLER() {
  if(!g_bWeHaveBus) {
    g_SPI_BlockoutTime = millis() + SPI_BLOCKOUT_PERIOD;
  }
}


void ESPWebDAVEx::Init_EXT_SD_Card() {
    // ----- GPIO -------
    // Detect when other master uses SPI bus
    pinMode(CS_SENSE, INPUT);
    attachInterrupt(CS_SENSE, SD_CARD_CS_SENSE_HANDLER, FALLING);
        
    // wait for other master to assert SPI bus first
    PRINT_OUT_LN_PGM("Delay...");
    delay(SPI_BLOCKOUT_PERIOD);
}

unsigned char ESPWebDAVEx::Get_WIFI_Config(char* pWIFI_HostName,char* pWIFI_SSID, char* pWIFI_Password) {
  struct AfterReturn {
    ~AfterReturn() {
      relenquishBusControl();
    }
  }OnReturn;

  String str1,str2;  
  char s1[MAX_STR_BUFF_SIZE],s2[MAX_STR_BUFF_SIZE];
  // ----- SD Card and Server -------
  // Check to see if other master is using the SPI bus
  while(millis() < g_SPI_BlockoutTime) {
    blink();
  }

  takeBusControl();

  if (!sd.begin(SD_CS, SPI_FULL_SPEED)) {
    PRINT_OUT_LN_PGM("begin SD failed");
    g_StatusMsg = "Failed to initialize SD Card";
    // indicate error on LED
    errorBlink();
    return 1;
  }
  else {
    PRINT_OUT_LN_PGM("SD card mounted");
  }

  File file = sd.open("SETUP.INI", FILE_READ);
  if (!file) {
    PRINT_OUT_LN_PGM("open file failed");
    return 1;
  }
  else {
    PRINT_OUT_LN_PGM("SETUP.INI file found.");
  }
  char tempBuff[MAX_STR_BUFF_SIZE];
  for (int index=0;index < 3;index++) {
    if (ReadLine(&file,tempBuff,MAX_STR_BUFF_SIZE)!=0) { 
      PRINT_OUT_LN_PGM("Reading failed!");
      break;
    }
    DivideStr(tempBuff,s1,s2,'=');
    str1=String(s1);str2=String(s2);str1.toUpperCase();
    if (str1=="SSID"){str2.toCharArray(pWIFI_SSID,str2.length()+1);}
    if (str1=="PASSWORD"){str2.toCharArray(pWIFI_Password,str2.length()+1);}
    if (str1=="HOSTNAME"){str2.toCharArray(pWIFI_HostName,str2.length()+1);}     
  }  
  file.close();

  if(strlen(pWIFI_HostName) == 0) {
    strcpy(pWIFI_HostName,DEFAULT_HOSTNAME);
  }
  if(strlen(pWIFI_Password) == 0 || strlen(pWIFI_SSID) == 0) {
    PRINT_OUT_LN_PGM("found no config / invalid config file, place SETUP.INI on SDCARD root folder using following format ...");
    PRINT_OUT_LN_PGM("SSID=<WIFI_Name>");
    PRINT_OUT_LN_PGM("PASSWORD=<WIFI_Password>");
    PRINT_OUT_LN_PGM("HOSTNAME=<WIFI_Device_Name>");
    return 1;
  }
  return 0;
}

void ESPWebDAVEx::Init_WebDAV_Server_noSD() {
  // start the SD DAV server
  g_dav.init_nosd(DEFAULT_SERVER_PORT);
  PRINT_OUT_LN_PGM("WebDAV server started");
}

void ESPWebDAVEx::Init_WebDAV_Server() {
  // ----- SD Card and Server -------
  // Check to see if other master is using the SPI bus
  while(millis() < g_SPI_BlockoutTime) {
    blink();
  }
  takeBusControl();
  // start the SD DAV server
  if(!g_dav.init(SD_CS, SPI_SPEED, DEFAULT_SERVER_PORT)) {
    g_StatusMsg = "Failed to initialize SD Card";
    PRINT_OUT_PGM("ERROR: "); PRINT_OUT_LN(g_StatusMsg);
    // indicate error on LED
    errorBlink();
    g_InitFailed = true;
  }
  else {
    blink();
  }
  relenquishBusControl();
  PRINT_OUT_LN_PGM("WebDAV server started");
}

void ESPWebDAVEx::Loop() {
    // ------------------------
  if(millis() < g_SPI_BlockoutTime) {
    blink();
  }

  // do it only if there is a need to read FS
  if(g_dav.isClientWaiting()) {
    if(g_InitFailed) {
      g_dav.rejectClient(g_StatusMsg);
    }
    // has other master been using the bus in last few seconds
    else if(millis() < g_SPI_BlockoutTime) {
      g_dav.rejectClient("Marlin is reading from SD card");
    }
    else {
      // a client is waiting and FS is ready and other SPI master is not using the bus
      takeBusControl();
      g_dav.handleClient();
      relenquishBusControl();
    }
  }
}