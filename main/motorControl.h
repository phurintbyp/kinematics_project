#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "motor.h"

extern Motor joints[NUM_MOTORS];

void initMotors();
void setJointPositions(JsonObject &positions, bool homing = false);
void moveJoint(Motor &motor, float increment);
void printCurrentPos();
long angleToSteps(float angle);
void setAllMotorFastSpeed(long speeds[]);
void setAllMotorSlowSpeed(long speeds[]);
void moveAll();
void stopAll();
void setAllSoftLimits(float m1Min, float m1Max, float m2Min, float m2Max, float m3Min, float m3Max, float m4Min, float m4Max, float m5Min, float m5Max);
void home();
void findLimitSwitch();
void resetAllMotors();

#endif