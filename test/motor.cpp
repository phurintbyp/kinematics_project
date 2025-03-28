#include "Motor.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin) {
  _stepPin = stepPin;
  _dirPin = dirPin;
  _enablePin = enablePin;
  _currentPosition = 0;

  pinMode(_stepPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);
  pinMode(_enablePin, OUTPUT);

  _stepIntervalMicros = 0;
}

void Motor::enableMotor(){
  digitalWrite(_enablePin, LOW);
}

void Motor::disableMotor(){
  digitalWrite(_enablePin, HIGH);
}

void Motor::setSpeed(long stepIntervalMicros) {
  _stepIntervalMicros = stepIntervalMicros;  // Set the constant time interval between steps
}

void Motor::move() {
  // Move one step towards the target position
  digitalWrite(_stepPin, HIGH);  // Generate step pulse (HIGH)
  delayMicroseconds(_stepIntervalMicros);  // Wait for the set time interval
  digitalWrite(_stepPin, LOW);  // Generate step pulse (LOW)
  delayMicroseconds(_stepIntervalMicros);  // Wait for the set time interval

  // Increment or decrement position depending on direction
  if (_targetPosition > _currentPosition) {
    _currentPosition++;
  } else {
    _currentPosition--;
  }
}

void Motor::setDirection(bool dir) {
  digitalWrite(_dirPin, dir);
}

void Motor::setTargetPosition(long target) {
  _targetPosition = target;  // Set the target position
}

bool Motor::hasReachedTarget() {
  return _currentPosition == _targetPosition;  // Check if the motor has reached the target
}

long Motor::getCurrentPosition() {
  return _currentPosition;  // Return current position
}

long Motor::getTargetPosition() {
  return _targetPosition;  // Return target position
}

void Motor::stop() {
  _targetPosition = _currentPosition;
}
