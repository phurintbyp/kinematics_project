#include <Arduino.h>
#include "safety.h"
#include "config.h"

void initSafetyPins() {
  pinMode(X_MIN, INPUT_PULLUP);
  pinMode(X_MAX, INPUT_PULLUP);
  pinMode(Y_MIN, INPUT_PULLUP);
  pinMode(Y_MAX, INPUT_PULLUP);
  pinMode(Z_MIN, INPUT_PULLUP);
  pinMode(Z_MAX, INPUT_PULLUP);
}

bool isMoveSafe() {
  if (digitalRead(X_MIN) == HIGH) {
    return false;
  } else {
    return true;
  }
}