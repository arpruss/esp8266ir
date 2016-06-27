// public domain code by Alexander Pruss

#include <string.h>
#include <ESP8266WiFi.h>
#include <EEPROM.h>
#include <IRremoteESP8266.h>

#define memzero(p,s) memset((p),0,(s))

#define PORT 5678
#define DEVICE "IRToWebThingy"
#define AP_NAME DEVICE

#define MAX_DATA 256
#define MAX_CLIENTS 5

#define SSID_LENGTH 33
#define PSK_LENGTH  64
#if 0
const char ssid[SSID_LENGTH] = "xxxx";
const char psk[PSK_LENGTH] = "yyyy";
#else
#include "c:/users/alexander/Documents/Arduino/private.h"
#endif

#define QUIET  ((uint8_t)'q')
#define COPY   ((uint8_t)'c')

#define LINE_LENGTH 256

char commandLine[LINE_LENGTH];
int commandLineLength = 0;
char lineData[LINE_LENGTH];

WiFiServer server(PORT);
WiFiClient serverClients[MAX_CLIENTS];
int latestClient = -1;
static int RECV_PIN = 0; // IR decoder pin
static uint8_t serialMode = QUIET;

static IRrecv irrecv(RECV_PIN);

#define SSID_OFFSET 2
#define PSK_OFFSET (SSID_OFFSET+SSID_LENGTH)
#define SERIAL_MODE_OFFSET (PSK_OFFSET+PSK_LENGTH)

void LoadSettings() {
    uint8_t buffer[512];
    EEPROM.begin(512);
    uint8_t sum = 0;
    for (int i = 0 ; i < 512 ; i++) {
      buffer[i] = EEPROM.read(i);
      if (i>=2) 
        sum += buffer[i];
    }
    EEPROM.end();
    if (buffer[0] != 'S' || buffer[1] != sum) {
      Serial.println("Using defaults, no saved settings.\r\n");
      return;
    }
    Serial.println("Restoring settings.\r\n");
    memcpy(ssid, buffer+SSID_OFFSET, SSID_LENGTH);
    memcpy(psk, buffer+PSK_OFFSET, PSK_LENGTH);
    serialMode = buffer[SERIAL_MODE_OFFSET];
}

void setup()
{
  Serial.begin(115200); 
  LoadSettings();
  if (ssid[0]) {
    Serial.println("Attempting to connect to WiFi.\r\n");
    WiFi.begin(ssid, psk[0] ? psk : NULL);
    for (int i = 0 ; i < 30 && WiFi.status() != WL_CONNECTED ; i++)
       delay(500);
  }
  if (!ssid[0] || WiFi.status() != WL_CONNECTED) {
    Serial.println("Starting AP.\r\n");
    WiFi.disconnect();
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(AP_NAME);
    Serial.println(String(DEVICE " on 192.168.4.1:")+PORT+"\r\n");
  }
  else {
    Serial.println(String(DEVICE " on ")+WiFi.localIP().toString()+String(":")+PORT+"\r\n");
  }
  irrecv.enableIRIn();  // Start the receiver

  server.begin();
  server.setNoDelay(true);
}

void SaveSettings() {
  uint8_t buffer[512];
  memzero(buffer, 512);
  memcpy(buffer+SSID_OFFSET, ssid, SSID_LENGTH);
  memcpy(buffer+PSK_OFFSET, psk, PSK_LENGTH);
  buffer[SERIAL_MODE_OFFSET] = serialMode;
  uint8_t sum = 0;
  for (int i = 2 ; i < 512 ; i++) {
     sum += buffer[i];
  }
  buffer[0] = 'S';
  buffer[1] = sum;
  EEPROM.begin(512);
  for (int i = 0; i < 512 ;i++) {
    EEPROM.write(i, buffer[i]);
  }
  EEPROM.end();
  Serial.println("Saving settings.\r\n");
}

void processCommand(char* command) {
  Serial.print("Command: ");
  Serial.println(command);
  if (!strncmp(command, "help", 4)) {
    strcpy(lineData, "ssid [AP ssid]\r\n"
                     "psk [AP password]\r\n"
                     "reboot\r\n"
                     "serial quiet|copy\r\n");
    return;
  }
  else if (!strncmp(command, "ssid", 4)) {
    memzero(ssid, SSID_LENGTH);
    if (command[4] == ' ') {
      char *p = command+5;
      for (int i = 0 ; i < SSID_LENGTH-1 && p[i] && p[i] != '\r' && p[i] != '\n' ; i++) {
        ssid[i] = p[i];
      }
    }
    SaveSettings();
    strcpy(lineData, "OK\r\n");
  }
  else if (!strncmp(command, "psk", 3)) {
    memzero(psk, PSK_LENGTH);
    if (command[3] == ' ') {
      char *p = command+4;
      for (int i = 0 ; i < PSK_LENGTH-1 && p[i] && p[i] != '\r' && p[i] != '\n' ; i++) {
        psk[i] = p[i];
      }
    }
    SaveSettings();
    strcpy(lineData, "OK\r\n");
  }
  else if (!strncmp(command, "serial ", 7)) {
    serialMode = command[7];
    SaveSettings();
    strcpy(lineData, "OK\r\n");
  }
  else if (!strncmp(command, "reboot", 6)) {
    ESP.reset();
  }
  else {
    strcpy(lineData, "Unknown command\r\n");
  }
}

//+=============================================================================
// Display encoding type
//
char* encoding (decode_results *results)
{
  switch (results->decode_type) {
    default:
    case UNKNOWN:      
        return "UNKNOWN";
    case MAGIQUEST:    
        return "MAGIQUEST";
    case NEC:          
        return "NEC";
    case SONY:         
        return "SONY";
    case RC5:          
        return "RC5";
    case RC6:          
        return "RC6";
    case DISH:         
        return "DISH";
    case SHARP:        
        return "SHARP";
    case JVC:          
        return "JVC";
    case SANYO:        
        return "SANYO";
    case MITSUBISHI:   
        return "MITSUBISHI";
    case SAMSUNG:      
        return "SAMSUNG";
    case LG:           
        return "LG";
    case WHYNTER:      
        return "WHYNTER";
    case AIWA_RC_T501: 
        return "AIWA_RC_T501";
    case PANASONIC:    
        return "PANASONIC";
  }
}

void loop()
{
  if (server.hasClient()) {
    int i;
    for (i = 0; i < MAX_CLIENTS ; i++) {
      if (!serverClients[i] || !serverClients[i].connected()) {
        if (serverClients[i])
          serverClients[i].stop();
        serverClients[i] = server.available();
        serverClients[i].write(DEVICE " ready\r\n");
        latestClient = i;
        break;
      }
    }
    if (i == MAX_CLIENTS)
      server.available().stop();
  }

  decode_results  result;      

  if (irrecv.decode(&result)) {
      irrecv.resume();  
      if (result.decode_type != UNKNOWN) {  
          unsigned int aux = 0;
          if (result.decode_type == PANASONIC)
            aux = result.panasonicAddress;
          else if (result.decode_type == MAGIQUEST)
            aux = result.magiquestMagnitude;
          sprintf(lineData, "%s,%ld,%d,%lx,%x", 
            encoding(&result), millis(), (int)result.bits, 
            (unsigned long)result.value, aux);

          if (serialMode == COPY)
            Serial.println(lineData);

          for (int i = 0 ; i < MAX_CLIENTS ; i++) {
            if (serverClients[i] && serverClients[i].connected()) {
              serverClients[i].write((const uint8_t*) lineData, (int)strlen(lineData));
              serverClients[i].write("\r\n", 2);
            }
          }
      }
  }

  if (latestClient >= 0 && serverClients[latestClient] && serverClients[latestClient].available()) {
    do {
      char c = serverClients[latestClient].read();
      if (c == '\r' || c == '\n') {
        commandLine[commandLineLength] = 0;
        if (commandLineLength > 0) {
          processCommand(commandLine);
          commandLineLength = 0;
          serverClients[latestClient].write((const uint8_t*)lineData, strlen(lineData));
        }
      }
      else if (commandLineLength < LINE_LENGTH-1) {
        commandLine[commandLineLength++] = c;
      }      
    } while(serverClients[latestClient].available());
  }

  yield();
}

