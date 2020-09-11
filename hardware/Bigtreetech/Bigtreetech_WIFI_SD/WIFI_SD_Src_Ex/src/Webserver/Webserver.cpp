#include "Webserver.h"
#include "../Utility/Utility.h"
#include <ESP8266WebServer.h>

extern ESP8266WebServer server;

void handleRoot() {
  LED_ON;
  server.send(200, "text/plain", "hello from esp8266!");
  LED_OFF;
}

void handleNotFound() {
  LED_ON;
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET)?"GET":"POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i=0; i<server.args(); i++){
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
  LED_OFF;
}

// ESP8266WebServer::HookFunction hookWebDAVForWebserver(const String& davRootDir, ESPWebDAVCore& dav)
// {
//     return [&dav, davRootDir](const String & method, const String & url, WiFiClient * client, ESP8266WebServer::ContentTypeFunction contentType)
//     {
//         return
//             url.indexOf(davRootDir) != 0 ? ESP8266WebServer::CLIENT_REQUEST_CAN_CONTINUE :
//             dav.parseRequest(method, url, client, contentType) ? ESP8266WebServer::CLIENT_REQUEST_IS_HANDLED :
//             ESP8266WebServer::CLIENT_MUST_STOP;
//     };
// }
