#include <ArduinoJson.h>
#include "motorControl.h"
#include "config.h"
#include "comms.h"
#include "safety.h"

StaticJsonDocument<256> document;
JsonObject position = document.to<JsonObject>();

void setup()
{
  Serial.begin(115200);
  initMotors();
}

void loop()
{
  if (Serial.available() > 0) {
    String command = readSerialCommand();  // Read the incoming JSON command
    Serial.println(command);
    if (command.length() > 0) {
      processCommand(command);             // Process and execute the command
    }
  }
}