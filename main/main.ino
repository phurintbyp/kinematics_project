#include "motorControl.h"
#include "config.h"

void setup()
{
  Serial.begin(115200);
  initMotors();
  setAllSoftLimits(-360, 360, -360, 360, -360, 360);
}

void loop()
{
  if (Serial.available()) {
    char command = Serial.read();
    switch (command) {
      case 'w': 
        setAllMotorFastSpeed(M1_SPEED_FAST, M2_SPEED_FAST, M3_SPEED_FAST);
        setAllMotorSlowSpeed(M1_SPEED_SLOW, M2_SPEED_SLOW, M3_SPEED_SLOW);
        moveAllTo(90, 0, 0); // Moves in angles
        break;
      case 'a': 
        setAllMotorFastSpeed(M1_SPEED_FAST, M2_SPEED_FAST, M3_SPEED_FAST);
        setAllMotorSlowSpeed(M1_SPEED_SLOW, M2_SPEED_SLOW, M3_SPEED_SLOW);
        moveAllTo(-90, 0, 0); 
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