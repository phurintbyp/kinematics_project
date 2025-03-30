#include "Motor.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin) {
  _stepPin = stepPin;
  _dirPin = dirPin;
  _enablePin = enablePin;
  _currentPosition = 0;
  _stepsTaken = 0;
  _totalSteps = 0;

  pinMode(_stepPin, OUTPUT);
  pinMode(_dirPin, OUTPUT);
  pinMode(_enablePin, OUTPUT);

  _fastStepIntervalMicros = 0;
  _slowStepIntervalMicros = 0;
}

void Motor::enableMotor(){
  digitalWrite(_enablePin, LOW);
}

void Motor::disableMotor(){
  digitalWrite(_enablePin, HIGH);
}

void Motor::setFastSpeed(long stepIntervalMicros) {
  _fastStepIntervalMicros = stepIntervalMicros;
}

void Motor::setSlowSpeed(long stepIntervalMicros) {
  _slowStepIntervalMicros = stepIntervalMicros;
}

void Motor::move(bool enableAcceleration = true) {
  if (enableAcceleration) {
    long stepsRemaining = abs(_targetPosition - _currentPosition);
    if (_stepsTaken < _accelSteps) {
      float accelRatio = (float)_stepsTaken / _accelSteps;
      _adjustedStepIntervalMicros = _slowStepIntervalMicros - accelRatio * (_slowStepIntervalMicros - _fastStepIntervalMicros);
    }
    else if (stepsRemaining < _accelSteps) {
      float decelRatio = (float)stepsRemaining / _accelSteps;
      _adjustedStepIntervalMicros = _fastStepIntervalMicros + (1.0 - decelRatio) * (_slowStepIntervalMicros - _fastStepIntervalMicros);
    }
    else {
      _adjustedStepIntervalMicros = _fastStepIntervalMicros;
    }
  } else {
    _adjustedStepIntervalMicros = _fastStepIntervalMicros;
  }
  digitalWrite(_stepPin, HIGH);
  delayMicroseconds(_adjustedStepIntervalMicros);
  digitalWrite(_stepPin, LOW);
  delayMicroseconds(_adjustedStepIntervalMicros);
  _stepsTaken++;
  

  if (_targetPosition > _currentPosition) {
    _currentPosition++;
  } else {
    _currentPosition--;
  }
}

void Motor::reset() {
  _stepsTaken = 0;
}

void Motor::setTotalSteps() {
  _totalSteps = abs(_targetPosition - _currentPosition);
}

// void Motor::move() {
//   digitalWrite(_stepPin, HIGH);
//   delayMicroseconds(_stepIntervalMicros);
//   digitalWrite(_stepPin, LOW);
//   delayMicroseconds(_stepIntervalMicros);

//   if (_targetPosition > _currentPosition) {
//     _currentPosition++;
//   } else {
//     _currentPosition--;
//   }
// }

void Motor::setDirection(bool dir) {
  digitalWrite(_dirPin, dir);
}

void Motor::setSoftLimit(float softLimitMin, float softLimitMax) {
  if (softLimitMin > softLimitMax) {
    Serial.println("Error: Min limit cannot be greater than max limit.");
    return;
  }
  _softLimitMin = softLimitMin;
  _softLimitMax = softLimitMax;
}

float Motor::getSoftLimitMin() {
  return _softLimitMin;
}

float Motor::getSoftLimitMax() {
  return _softLimitMax;
}

bool Motor::isBeyondSoftLimit(float angle) {
  if (angle < _softLimitMin || angle > _softLimitMax) {
    return true;
  } else {
    return false;
  }
}

void Motor::setTargetPosition(long target) {
  _targetPosition = target;  // Set the target position
}

void Motor::setCurrentPosition(long pos) {
  _currentPosition = pos;  // Set the target position
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

void Motor::setAccelSteps(long accelSteps){
  _accelSteps = accelSteps;
}

void Motor::getAccelSteps(){
  return _accelSteps;
}

void Motor::stop() {
  _targetPosition = _currentPosition;
}
