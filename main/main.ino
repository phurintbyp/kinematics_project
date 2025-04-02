#include <ArduinoJson.h>
#include "motorControl.h"
#include "config.h"
#include "comms.h"
#include "safety.h"

// No global doc or pos needed here.

void setup()
{
  Serial.begin(115200);
  initMotors(); // sets up motors (enable, speed, etc.)
}

void loop()
{
  // 1) Handle incoming commands from serial
  if (Serial.available() > 0) {
    String command = readSerialCommand();  // from comms.cpp
    if (command.length() > 0) {
      Serial.println(command);             // debug
      processCommand(command);             // parse JSON and set target positions
    }
  }

  updateAll(true);

  // 3) Optional: check safety or other code here
}
