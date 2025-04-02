#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
public:
  Motor(byte stepPin, byte dirPin, byte enablePin);

  // Basic setup
  void enableMotor();
  void disableMotor();

  // Setting speeds
  void setFastSpeed(long stepIntervalMicros);
  void setSlowSpeed(long stepIntervalMicros);
  void setAccelSteps(long accelSteps);

  // Non-blocking update function
  // This is called in loop() to step if needed
  void update(bool enableAcceleration = true);

  // Movement
  void setTargetPosition(long target);   // sets where the motor should go
  long getTargetPosition();

  void setCurrentPosition(long pos);
  long getCurrentPosition();

  bool hasReachedTarget();
  void stop();    // Force the target to be current => no more movement
  void reset();   // Reset stepsTaken=0 for a new movement

  // Inversion of direction
  void setDirectionInverted(bool inverted);

  // Soft limits (optional)
  void setSoftLimit(float minAngle, float maxAngle);
  bool isBeyondSoftLimit(float angle);
  void setDirection(bool dir);

private:
  // Internal step logic
  void stepOnce();

  byte _stepPin;
  byte _dirPin;
  byte _enablePin;

  bool _directionInverted = false;

  // current status
  long _currentPosition = 0;
  long _targetPosition  = 0;

  long _stepsTaken      = 0;   // how many steps since we started this move
  long _totalSteps      = 0;   // total steps from start to target

  // time-based stepping
  unsigned long _lastStepTime = 0; // micros() when we last stepped

  long _accelSteps = 16000; // acceleration region in steps

  // user-chosen speeds (bigger number = slower, because it's microseconds)
  long _fastStepIntervalMicros = 1000;
  long _slowStepIntervalMicros = 2000;

  // The interval we actually use right now, based on acceleration/decel
  long _adjustedStepIntervalMicros = 1000;

  // Soft limit data
  float _softLimitMin = -9999.0;
  float _softLimitMax =  9999.0;
};

#endif
