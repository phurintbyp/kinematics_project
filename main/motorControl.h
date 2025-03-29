#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H

void initMotors();
void moveAllTo(float m1Angle, float m2Angle, float m3Angle, bool homing = false);
void printCurrentPos();
long angleToSteps(float angle);
void setAllMotorFastSpeed(long speed1, long speed2, long speed3);
void setAllMotorSlowSpeed(long speed1, long speed2, long speed3);
void moveAll();
void stopAll();
void setAllSoftLimits(float m1Min, float m1Max, float m2Min, float m2Max, float m3Min, float m3Max);
void home();
void findLimitSwitch();
void resetAllMotors();

#endif