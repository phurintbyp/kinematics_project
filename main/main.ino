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
  setAllSoftLimits(M1_SOFT_MIN, M1_SOFT_MAX, M2_SOFT_MIN, M2_SOFT_MAX, M3_SOFT_MIN, M3_SOFT_MAX, M4_SOFT_MIN, M4_SOFT_MAX, M5_SOFT_MIN, M5_SOFT_MAX);
}

void loop()
{
  if (Serial.available() && isMoveSafe()) {
    char command = Serial.read();
    switch (command) {
      case 'w': 
        position["j1"] = 90;
        position["j2"] = 0;
        position["j3"] = 0;
        position["j4"] = 0;
        position["j5"] = 0;

        setAllMotorFastSpeed(SPEED_FAST);
        setAllMotorSlowSpeed(SPEED_SLOW);
        setJointPositions(position);
        break;
      case 's':
        position["j1"] = -90;
        position["j2"] = 0;
        position["j3"] = 0;
        position["j4"] = 0;
        position["j5"] = 0;

        setAllMotorFastSpeed(SPEED_FAST);
        setAllMotorSlowSpeed(SPEED_SLOW);
        setJointPositions(position);
        break;
      case 'a':
        setAllMotorFastSpeed(SPEED_FAST);
        setAllMotorSlowSpeed(SPEED_SLOW);
        moveJoint(joints[0], 5);
        printCurrentPos(); 
        break;
      case 'd':
        setAllMotorFastSpeed(SPEED_FAST);
        setAllMotorSlowSpeed(SPEED_SLOW);
        moveJoint(joints[0], -5);
        printCurrentPos(); 
        break;
      case 'p': 
        printCurrentPos(); 
        break;
      case 'h':
        home();
        break;
    } 
  }
}