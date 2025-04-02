#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "motor.h"

extern Motor joints[NUM_MOTORS];

void initMotors();
void setJointPositions(JsonObject &positions);
void moveJoint(Motor &motor, float increment, bool homing = false);
void printCurrentPos();
long angleToSteps(float angle);
void setAllMotorFastSpeed(long speeds[]);
void setAllMotorSlowSpeed(long speeds[]);
void moveAll(bool enableAcceleration = true);
void stopAll();
void home();
void findLimitSwitch(int joint, bool seeking);
void resetAllMotors();

#endif