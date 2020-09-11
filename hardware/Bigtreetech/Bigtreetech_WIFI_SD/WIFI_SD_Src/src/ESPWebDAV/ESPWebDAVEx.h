#ifndef ESPWebDAVEx_h
#define ESPWebDAVEx_h

class ESPWebDAVEx {
public:

    void Init_EXT_SD_Card();
    void Init_WebDAV_Server_noSD();
    void Init_WebDAV_Server();

    void Loop();
    unsigned char Get_WIFI_Config(char* pWIFI_HostName,char* pWIFI_SSID, char* pWIFI_Password);
};


#endif