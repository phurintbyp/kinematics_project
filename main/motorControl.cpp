#include "motorControl.h"
#include "motor.h"
#include <Arduino.h>
#include <AccelStepper.h>
#include "safety.h"
#include "config.h"

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

void setAllMotorFastSpeed(long speed1, long speed2, long speed3) {
  motor1.setFastSpeed(speed1);
  motor2.setFastSpeed(speed2);
  motor3.setFastSpeed(speed3);
}

void setAllMotorSlowSpeed(long speed1, long speed2, long speed3) {
  motor1.setSlowSpeed(speed1);
  motor2.setSlowSpeed(speed2);
  motor3.setSlowSpeed(speed3);
}

long angleToSteps(float angle) {
  return round(angle / MICROSTEP_ANGLE);
}

float stepsToAngle(long angle) {
  return angle * MICROSTEP_ANGLE;
}

void moveAllTo(float m1Angle, float m2Angle, float m3Angle, bool homing = false) {
  if (motor1.isBeyondSoftLimit(m1Angle) || motor2.isBeyondSoftLimit(m2Angle) || motor3.isBeyondSoftLimit(m3Angle)) {
    Serial.println("Target position exceeds set soft limit.");
    return;
  } else if (!isMoveSafe()) {
    Serial.println("LIMIT SWITCH TRIGGERED! Cancelling move command.");
    return;
  }

  long m1Target = angleToSteps(m1Angle);
  long m2Target = angleToSteps(m2Angle);
  long m3Target = angleToSteps(m3Angle);

  motor1.setTargetPosition(m1Target);  // Set target position for motor1
  motor2.setTargetPosition(m2Target);  // Set target position for motor2
  motor3.setTargetPosition(m3Target);  // Set target position for motor3

  motor1.setTotalSteps();
  motor2.setTotalSteps();
  motor3.setTotalSteps();

  motor1.setDirection(motor1.getTargetPosition() > motor1.getCurrentPosition() ? HIGH : LOW);
  motor2.setDirection(motor2.getTargetPosition() > motor2.getCurrentPosition() ? HIGH : LOW);
  motor3.setDirection(motor3.getTargetPosition() > motor3.getCurrentPosition() ? HIGH : LOW);

    while (!motor1.hasReachedTarget() || !motor2.hasReachedTarget() || !motor3.hasReachedTarget()) {
      if (!isMoveSafe() && !homing) {
        Serial.println("LIMIT SWITCH TRIGGERED!");
        stopAll();
        break;
      }else {
        moveAll();
      }

  }
  resetAllMotors();
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

void home(){
  setAllMotorFastSpeed(M1_SPEED_FAST * HOMING_SEEK, M2_SPEED_FAST * HOMING_SEEK, M3_SPEED_FAST * HOMING_SEEK);
  findLimitSwitch();
  setAllMotorFastSpeed(M1_SPEED_FAST, M2_SPEED_FAST, M3_SPEED_FAST);
  moveAllTo(motor1.getCurrentPosition() + HOMING_PULL_OFF, motor2.getCurrentPosition() + HOMING_PULL_OFF, motor3.getCurrentPosition() + HOMING_PULL_OFF, true);

  setAllMotorFastSpeed(M1_SPEED_FAST * HOMING_FEED, M2_SPEED_FAST * HOMING_FEED, M3_SPEED_FAST * HOMING_FEED);
  findLimitSwitch();
  setAllMotorFastSpeed(M1_SPEED_FAST, M2_SPEED_FAST, M3_SPEED_FAST);
  moveAllTo(motor1.getCurrentPosition() + HOMING_PULL_OFF, motor2.getCurrentPosition() + HOMING_PULL_OFF, motor3.getCurrentPosition() + HOMING_PULL_OFF, true);

  motor1.setCurrentPosition(0);
  motor2.setCurrentPosition(0);
  motor3.setCurrentPosition(0);
  resetAllMotors();
  Serial.println("Homing complete!");
}

void findLimitSwitch() {
  motor1.setDirection(LOW);
  motor2.setDirection(LOW);
  motor3.setDirection(LOW);

  while (digitalRead(X_MIN) == LOW) {
    motor1.move(false);
    motor2.move(false);
    motor3.move(false);
  }
}

void resetAllMotors() {
  motor1.reset();
  motor2.reset();
  motor3.reset();
}