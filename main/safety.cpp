#include <Arduino.h>
#include "safety.h"
#include "config.h"

void initSafetyPins() {
  pinMode(hardLimit[0], INPUT_PULLUP);
  pinMode(hardLimit[1], INPUT_PULLUP);
  pinMode(hardLimit[2], INPUT_PULLUP);
  pinMode(hardLimit[3], INPUT_PULLUP);
  pinMode(hardLimit[4], INPUT_PULLUP);
}

bool isMoveSafe() {
  if (digitalRead(hardLimit[0]) == LOW || digitalRead(hardLimit[1]) == LOW) {
    return false;
  } else {
    return true;
  }
}