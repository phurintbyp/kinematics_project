#ifndef Motor_h
#define Motor_h

#include "Arduino.h"

class Motor {
  public:
    Motor(byte stepPin, byte dirPin, byte enablePin);

    // Set motor speed parameters (no acceleration)
    void setSpeed(long stepIntervalMicros);

    // Move the motor at a constant speed
    void move();

    void enableMotor();
    void disableMotor();
    void setTargetPosition(long target);
    void setDirection(bool dir);
    
    bool hasReachedTarget(); 

    long getCurrentPosition();

    long getTargetPosition();
    void setSoftLimit(float softLimitMin, float softLimitMax);
    float getSoftLimitMin();
    float getSoftLimitMax();
    void stop();

  private:
    byte _stepPin;
    byte _dirPin;
    byte _enablePin;
    long _stepIntervalMicros;
    long _numSteps;
    long _currentPosition;
    long _targetPosition;
    float _softLimitMin;
    float _softLimitMax;
    int _accelSteps;
};

#endif
