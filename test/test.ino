#include "motorControl.h"
#include "safety.h"
#include "motor.h"

const int M1_ACCEL = 20000;
const int M2_ACCEL = 20000;
const int M3_ACCEL = 20000;

const long MAX_SPEED = 50000.0;

unsigned long lastTime = 0;
unsigned long printInterval = 1000;

void setup()
{
  Serial.begin(9600);
  // initMotors(M1_ACCEL, M2_ACCEL, M3_ACCEL);
  // initSafetyPins();
  initMotors();  // Initialize motors
  setAllMotorSpeed(100, 300, 300);  // Set speed for all motors
}

void loop()
{
  if (Serial.available()&& isMoveSafe()) {
    char command = Serial.read();
    switch (command) {
      case 'w': moveAllTo(20000, 0, 0); break;
      case 'a': moveAllTo(-20000, 0, 0); break;
      case 'p': printCurrentPos(); break;
    }
  }
}