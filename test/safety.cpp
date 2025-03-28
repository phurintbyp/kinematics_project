#include <Arduino.h>
#include "safety.h"

// For additional limit switches look at aux pins
const int X_MIN = 3;
const int X_MAX = 2;
const int Y_MIN = 14;
const int Y_MAX = 15;
const int Z_MIN = 18;
const int Z_MAX = 19;

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