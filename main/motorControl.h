#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H

void initMotors();
void moveAllTo(float m1Angle, float m2Angle, float m3Angle);
void printCurrentPos();
long angleToSteps(float angle);
void setAllMotorSpeed(long speed1, long speed2, long speed3);
void moveAll();
void stopAll();
void setAllSoftLimits(float m1Min, float m1Max, float m2Min, float m2Max, float m3Min, float m3Max);

#endif