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
    
    bool hasReachedTarget(); 

    long getCurrentPosition();

    long getTargetPosition();
    void setSoftLimit(float softLimitMin, float softLimitMax);
    float getSoftLimitMin();
    float getSoftLimitMax();
    void setAccelSteps(long accelSteps);
    void getAccelSteps();
    void stop();
    void setCurrentPosition(long pos);
    bool isBeyondSoftLimit(float angle);
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
    float _softLimitMin;
    float _softLimitMax;
    long _accelSteps;
    long _stepsTaken;
    int _adjustedStepIntervalMicros;
    long _totalSteps;
};

#endif
