#include "motorControl.h"
#include "motor.h"
#include <Arduino.h>
#include <AccelStepper.h>
#include "safety.h"

const int M1_STEP = 54;
const int M1_DIR = 55;
const int M1_ENABLE = 38;

const int M2_STEP = 60;
const int M2_DIR = 61;
const int M2_ENABLE = 56;

const int M3_STEP = 46;
const int M3_DIR = 48;
const int M3_ENABLE = 62;

// Repurposed Extruder 0 pin
const int M4_STEP = 26;
const int M4_DIR = 28;
const int M4_ENABLE = 24;

// Repurposed Extruder 1 pin
const int M5_STEP = 34;
const int M5_DIR = 36;
const int M5_ENABLE = 30;

const float MICROSTEP_ANGLE = 0.05625;

Motor motor1(M1_STEP, M1_DIR, M1_ENABLE);  
Motor motor2(M2_STEP, M2_DIR, M2_ENABLE);  
Motor motor3(M3_STEP, M3_DIR, M3_ENABLE);  

void initMotors()
{
  motor1.enableMotor();
  motor2.enableMotor();
  motor3.enableMotor();

  Serial.println("Setup motors successfully");
}

void setAllMotorSpeed(long speed1, long speed2, long speed3) {
  motor1.setSpeed(speed1);
  motor2.setSpeed(speed2);
  motor3.setSpeed(speed3);
}

long angleToSteps(float angle) {
  return round(angle / MICROSTEP_ANGLE);
}

float stepsToAngle(long angle) {
  return angle * MICROSTEP_ANGLE;
}

void moveAllTo(float m1Angle, float m2Angle, float m3Angle) {
  if (m1Angle < motor1.getSoftLimitMin() || m1Angle > motor1.getSoftLimitMax() || m2Angle < motor2.getSoftLimitMin() || m2Angle > motor2.getSoftLimitMax() || m3Angle < motor3.getSoftLimitMin() || m3Angle > motor3.getSoftLimitMax()) {
    Serial.println("Target position exceeds set soft limit.");
    return;
  }

  long m1Target = angleToSteps(m1Angle);
  long m2Target = angleToSteps(m2Angle);
  long m3Target = angleToSteps(m3Angle);

  motor1.setTargetPosition(m1Target);  // Set target position for motor1
  motor2.setTargetPosition(m2Target);  // Set target position for motor2
  motor3.setTargetPosition(m3Target);  // Set target position for motor3

  motor1.setDirection(motor1.getTargetPosition() > motor1.getCurrentPosition() ? HIGH : LOW);
  motor2.setDirection(motor2.getTargetPosition() > motor2.getCurrentPosition() ? HIGH : LOW);
  motor3.setDirection(motor3.getTargetPosition() > motor3.getCurrentPosition() ? HIGH : LOW);

  while (!motor1.hasReachedTarget() || !motor2.hasReachedTarget() || !motor3.hasReachedTarget()) {
    if (!isMoveSafe()) {
      Serial.println("LIMIT SWITCH TRIGGERED!");
      stopAll();
      break;
    }else {
      moveAll();
    }
  }
  Serial.println("All motors reached their target!");
}

void moveAll(){
  if (motor1.getCurrentPosition() != motor1.getTargetPosition()) {
    motor1.move();
  }

  if (motor2.getCurrentPosition() != motor2.getTargetPosition()) {
    motor2.move();
  }

  if (motor3.getCurrentPosition() != motor3.getTargetPosition()) {
    motor3.move();
  }
}

void stopAll() {
  motor1.stop();
  motor2.stop();
  motor3.stop();
}

void printCurrentPos(){
  Serial.print("Motor 1 Position : ");
  Serial.println(stepsToAngle(motor1.getCurrentPosition()));
  Serial.print("Motor 2 Position : ");
  Serial.println(stepsToAngle(motor2.getCurrentPosition()));
  Serial.print("Motor 3 Position : ");
  Serial.println(stepsToAngle(motor3.getCurrentPosition()));
  Serial.println("------------------------------");
}

void setAllSoftLimits(float m1Min, float m1Max, float m2Min, float m2Max, float m3Min, float m3Max) {
  motor1.setSoftLimit(m1Min, m1Max);
  motor2.setSoftLimit(m2Min, m2Max);
  motor3.setSoftLimit(m3Min, m3Max);
}