#include "motorControl.h"
#include "safety.h"
#include "motor.h"

const int M1_SPEED = 100; //lower = higher speed
const int M2_SPEED = 300;
const int M3_SPEED = 300;

void setup()
{
  Serial.begin(115200);
  initMotors();
  setAllMotorSpeed(M1_SPEED, M2_SPEED, M3_SPEED);
  setAllSoftLimits(-360, 360, -360, 360, -360, 360);
}

void loop()
{
  if (Serial.available()&& isMoveSafe()) {
    char command = Serial.read();
    switch (command) {
      case 'w': moveAllTo(90, 0, 0); break; // Moves in angles
      case 'a': moveAllTo(-90, 0, 0); break;
      case 'p': printCurrentPos(); break;
    }
  }
}