#ifndef Webserver_h
#define Webserver_h


//extern "C"
//ESP8266WebServer::HookFunction hookWebDAVForWebserver(const String& davRootDir, ESPWebDAV& dav);

void handleRoot();
void handleNotFound();

#endif