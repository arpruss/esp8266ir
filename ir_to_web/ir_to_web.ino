// public domain code by Alexander Pruss

#include <ESP8266WiFi.h>
#include <IRremoteESP8266.h>

#define MAX_DATA 256
#define MAX_CLIENTS 5

#if 0
const char* ssid = "xxxx";
const char* password = "yyyy";
#else
#include "../private.h"
#endif

char lineData[256];

WiFiServer server(5678);
WiFiClient serverClients[MAX_CLIENTS];

static int RECV_PIN = 0; // IR decoder pin

static IRrecv irrecv(RECV_PIN);

void  setup ( )
{
  Serial.begin(115200); 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.println(String("Connected as ")+WiFi.localIP().toString()+String(":5678"));
  irrecv.enableIRIn();  // Start the receiver
  server.begin();
  server.setNoDelay(true);
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



void toLineData(decode_results *results)
{
  unsigned int aux = 0;
  if (results->decode_type == PANASONIC)
    aux = results->panasonicAddress;
  else if (results->decode_type == MAGIQUEST)
    aux = results->magiquestMagnitude;
  sprintf(lineData, "%s,%d,%lx,%x", encoding(results),
    (int)results->bits, (unsigned long)results->value, aux);
}


void loop()
{
  if (server.hasClient()) {
    for (int i = 0; i < MAX_CLIENTS ; i++) {
      if (!serverClients[i] || !serverClients[i].connected()) {
        if (serverClients[i])
          serverClients[i].stop();
        serverClients[i] = server.available();
        return;
      }
    }
    server.available().stop();
  }

  decode_results  result;        

  if (irrecv.decode(&result) && result.decode_type != UNKNOWN) {  
      toLineData(&result);
      Serial.println(lineData);
      for (int i = 0 ; i < MAX_CLIENTS ; i++) {
        if (serverClients[i] && serverClients[i].connected()) {
          serverClients[i].write((const uint8_t*) lineData, (int)strlen(lineData));
          serverClients[i].write("\r\n", 2);
        }
      }
      irrecv.resume();              
  }
}

