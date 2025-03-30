#include <Arduino.h>
#include "motorControl.h"
#include <ArduinoJson.h>
#include "comms.h"

String readSerialCommand() {
  String input = Serial.readStringUntil('\n');
  return input;
}

void processCommand(String command) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, command);

  if (error) {
    Serial.print("Failed to parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  const char* cmd = doc["cmd"];

  if (strcmp(cmd, "setJointPositions") == 0) {
    JsonObject pos = doc["positions"];
    setJointPositions(pos);
  }
  else if (strcmp(cmd, "moveJoint") == 0) {
    const char* joint = doc["joint"];
    float increment = doc["increment"];

    if (joint[0] == 'j' && joint[1] >= '1' && joint[1] <= '5') {
      int index = joint[1] - '1';
      moveJoint(joints[index], increment);
    } else {
      Serial.println("Unknown joint");
    }
  }
  else if (strcmp(cmd, "setCartesianPosition") == 0) {
    // Handle setCartesianPosition
  }
  else if (strcmp(cmd, "estop") == 0) {
    Serial.println("E-STOP");
  }
  else {
    Serial.println("Unknown command");
  }
}
