#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H

void initMotors();
void moveAllTo(long m1Target, long m2Target, long m3Target);
void printCurrentPos();
long stepsToAngle(float steps);
void setAllMotorSpeed(long speed1, long speed2, long speed3);
void moveAll();
void stopAll();

extern bool isMoving;
extern const long MAX_SPEED;

#endif