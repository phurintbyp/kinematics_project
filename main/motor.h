#ifndef Motor_h
#define Motor_h

#include "Arduino.h"

class Motor {
  public:
    Motor(byte stepPin, byte dirPin, byte enablePin);

    // Set motor speed parameters
    void setFastSpeed(long stepIntervalMicros);
    void setSlowSpeed(long stepIntervalMicros);

    void move(bool enableAcceleration = true);

    void enableMotor();
    void disableMotor();
    void setTargetPosition(long target);
    void setDirection(bool dir);
    void setDirectionInverted(bool inverted);
    bool hasReachedTarget(); 

    long getCurrentPosition();

    long getTargetPosition();
    void setAccelSteps(long accelSteps);
    void getAccelSteps();
    void stop();
    void setCurrentPosition(long pos);
    void setTotalSteps();
    void reset();

  private:
    byte _stepPin;
    byte _dirPin;
    byte _enablePin;
    long _fastStepIntervalMicros;
    long _slowStepIntervalMicros;
    long _numSteps;
    long _currentPosition;
    long _targetPosition;
    long _accelSteps;
    long _stepsTaken;
    int _adjustedStepIntervalMicros;
    long _totalSteps;
    bool _directionInverted = false;
};

#endif
