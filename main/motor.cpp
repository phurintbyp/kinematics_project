#include "motor.h"

Motor::Motor(byte stepPin, byte dirPin, byte enablePin) {
  _stepPin   = stepPin;
  _dirPin    = dirPin;
  _enablePin = enablePin;

  pinMode(_stepPin, OUTPUT);
  pinMode(_dirPin,  OUTPUT);
  pinMode(_enablePin, OUTPUT);

  // Default positions
  _currentPosition = 0;
  _targetPosition  = 0;
  _stepsTaken      = 0;
  _totalSteps      = 0;

  _lastStepTime = micros();
}

void Motor::enableMotor() {
  digitalWrite(_enablePin, LOW);
}

void Motor::disableMotor() {
  digitalWrite(_enablePin, HIGH);
}

void Motor::setFastSpeed(long stepIntervalMicros) {
  _fastStepIntervalMicros = stepIntervalMicros;
}

void Motor::setSlowSpeed(long stepIntervalMicros) {
  _slowStepIntervalMicros = stepIntervalMicros;
}

void Motor::setAccelSteps(long accelSteps) {
  _accelSteps = accelSteps;
}

void Motor::setDirection(bool dir = false) {
  bool finalDir = _directionInverted ? !dir : dir;
  digitalWrite(_dirPin, finalDir);
}

void Motor::setTargetPosition(long target) {
  _targetPosition = target;
  // Recalc total steps
  _totalSteps = labs(_targetPosition - _currentPosition);
  _stepsTaken = 0;  // Reset for new move
}

long Motor::getTargetPosition() {
  return _targetPosition;
}

void Motor::setCurrentPosition(long pos) {
  _currentPosition = pos;
}

long Motor::getCurrentPosition() {
  return _currentPosition;
}

bool Motor::hasReachedTarget() {
  return (_currentPosition == _targetPosition);
}

void Motor::stop() {
  // Force the motor to consider itself "done"
  _targetPosition = _currentPosition;
}

void Motor::reset() {
  _stepsTaken = 0;
}

// The main non-blocking logic. Call this frequently
void Motor::update(bool enableAcceleration) {
  if (hasReachedTarget()) {
    return; // No movement needed
  }

  // Decide step interval
  if (enableAcceleration) {
    long stepsRemaining = labs(_targetPosition - _currentPosition);

    if (_stepsTaken < _accelSteps) {
      // acceleration
      float accelRatio = (float)_stepsTaken / (float)_accelSteps;
      _adjustedStepIntervalMicros = _slowStepIntervalMicros
        - (accelRatio * (_slowStepIntervalMicros - _fastStepIntervalMicros));
    }
    else if (stepsRemaining < _accelSteps) {
      // deceleration
      float decelRatio = (float)stepsRemaining / (float)_accelSteps;
      _adjustedStepIntervalMicros = _fastStepIntervalMicros
        + ((1.0f - decelRatio) * (_slowStepIntervalMicros - _fastStepIntervalMicros));
    }
    else {
      // constant speed
      _adjustedStepIntervalMicros = _fastStepIntervalMicros;
    }
  }
  else {
    // No acceleration -> always fast speed
    _adjustedStepIntervalMicros = _fastStepIntervalMicros;
  }

  // Check if it is time to step
  unsigned long now = micros();
  if (now - _lastStepTime >= (unsigned long)_adjustedStepIntervalMicros) {
    _lastStepTime = now;
    stepOnce();
  }
}

void Motor::stepOnce() {
  // One step pulse
  digitalWrite(_stepPin, HIGH);
  // Could do a short delay, but let's keep it minimal
  digitalWrite(_stepPin, LOW);

  // Update position
  _stepsTaken++;
  if (_targetPosition > _currentPosition)
    _currentPosition++;
  else
    _currentPosition--;
}

void Motor::setDirectionInverted(bool inverted) {
  _directionInverted = inverted;
}

// Soft limit
void Motor::setSoftLimit(float minAngle, float maxAngle) {
  _softLimitMin = minAngle;
  _softLimitMax = maxAngle;
}

bool Motor::isBeyondSoftLimit(float angle) {
  return (angle < _softLimitMin || angle > _softLimitMax);
}
