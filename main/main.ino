#include <ArduinoJson.h>
#include "motorControl.h"
#include "config.h"
#include "comms.h"
#include "safety.h"
#include <Servo.h>

Servo myServo;

// No global doc or pos needed here.

void setup()
{
  Serial.begin(115200);
  initMotors(); // sets up motors (enable, speed, etc.)
  myServo.attach(4); // Attach servo to pin 9 (change if needed)
}

void loop()
{
  // 1) Handle incoming commands from serial
  if (Serial.available() > 0) {
    String command = readSerialCommand();  // from comms.cpp
    if (command.length() > 0) {
      Serial.println(command);             // debug
      processCommand(command);             // parse JSON and set target 
    }
  }

  // 3) Optional: check safety or other code here
  // for (int angle = 0; angle <= 180; angle++) {
  //   myServo.write(angle);
  //   delay(15); // Smooth movement
  // }

  // delay(500); // Wait at 180°

  // // Move back from 180° to 0°
  // for (int angle = 180; angle >= 0; angle--) {
  //   myServo.write(angle);
  //   delay(15);
  // }

  // delay(500); // Wait at 0°
}
