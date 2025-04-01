#include "motorControl.h"
#include "motor.h"
#include <Arduino.h>
#include "safety.h"
#include "config.h"
#include <ArduinoJson.h>

Motor joints[NUM_MOTORS] = {
  Motor(M1_STEP, M1_DIR, M1_ENABLE),
  Motor(M2_STEP, M2_DIR, M2_ENABLE),
  Motor(M3_STEP, M3_DIR, M3_ENABLE),
  Motor(M4_STEP, M4_DIR, M4_ENABLE),
  Motor(M5_STEP, M5_DIR, M5_ENABLE)
};

float m1Angle = 0;
float m2Angle = 0;
float m3Angle = 0;
float m4Angle = 0;
float m5Angle = 0;

StaticJsonDocument<256> doc;
JsonObject pos = doc.to<JsonObject>();

bool allReached = false;

void initMotors()
{
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].enableMotor();
    joints[i].setAccelSteps(ACCEL_STEPS[i]);
    joints[i].setDirectionInverted(MOTOR_INVERTED[i]);
  }
}

void setAllMotorFastSpeed(long speeds[]) {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].setFastSpeed(speeds[i]);
  }
}

void setAllMotorSlowSpeed(long speeds[]) {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].setSlowSpeed(speeds[i]);
  }
}

long angleToSteps(float angle) {
  return round(angle / MICROSTEP_ANGLE);
}

float stepsToAngle(long angle) {
  return angle * MICROSTEP_ANGLE;
}

void setJointPositions(JsonObject &positions) {
  float angle[5] = {
    positions["j1"],
    positions["j2"],
    positions["j3"],
    positions["j4"],
    positions["j5"]
  };

  for (int i = 0; i < NUM_MOTORS; i++) {
    if (joints[i].isBeyondSoftLimit(angle[i])) {
      Serial.println("Target position exceeds set soft limit.");
      return;
    }
    joints[i].setTargetPosition(angleToSteps(angle[i]));
    joints[i].setTotalSteps();
    joints[i].setDirection(joints[i].getTargetPosition() > joints[i].getCurrentPosition() ? HIGH : LOW);
  }
  
  while (!joints[0].hasReachedTarget() || !joints[1].hasReachedTarget() || !joints[2].hasReachedTarget() || !joints[3].hasReachedTarget() || !joints[4].hasReachedTarget()) {
      if (!isMoveSafe()) {
        Serial.println("LIMIT SWITCH TRIGGERED!");
        stopAll();
        break;
      }else {
        moveAll(true);
      }
  }
  resetAllMotors();
  Serial.println("All motors reached their target!");
}

void moveAll(bool enableAcceleration = true){
  if (joints[0].getCurrentPosition() != joints[0].getTargetPosition()) {
    joints[0].move(enableAcceleration);
  }

  if (joints[1].getCurrentPosition() != joints[1].getTargetPosition()) {
    joints[1].move(enableAcceleration);
  }

  if (joints[2].getCurrentPosition() != joints[2].getTargetPosition()) {
    joints[2].move(enableAcceleration);
  }

  if (joints[3].getCurrentPosition() != joints[3].getTargetPosition()) {
    joints[3].move(enableAcceleration);
  }

  if (joints[4].getCurrentPosition() != joints[4].getTargetPosition()) {
    joints[4].move(enableAcceleration);
  }
}

void stopAll() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].stop();
  }
}

void printCurrentPos(){
  for (int i = 0; i < NUM_MOTORS; i++) {
    Serial.print("Joint ");
    Serial.print(i + 1);
    Serial.print(" Position : ");
    Serial.println(stepsToAngle(joints[i].getCurrentPosition()));
  }
  Serial.println("------------------------------");
}

void setAllSoftLimits(float m1Min, float m1Max, float m2Min, float m2Max, float m3Min, float m3Max, float m4Min, float m4Max, float m5Min, float m5Max) {
  joints[0].setSoftLimit(m1Min, m1Max);
  joints[1].setSoftLimit(m2Min, m2Max);
  joints[2].setSoftLimit(m3Min, m3Max);
  joints[3].setSoftLimit(m4Min, m4Max);
  joints[4].setSoftLimit(m5Min, m5Max);
}

void home() {
  // Later implement homing for multiple joints here
  findLimitSwitch(0, true);
  moveJoint(joints[0], HOMING_PULL_OFF[0], true);

  delay(200);

  findLimitSwitch(0, false);
  moveJoint(joints[0], HOMING_PULL_OFF[0], true);

  joints[0].setCurrentPosition(0);
  joints[0].reset();
  Serial.println("Homing complete");
}

void findLimitSwitch(int joint, bool seeking) {
  float speed = seeking ? HOMING_SEEK_SPEED[joint] : HOMING_FEED_SPEED[joint];
  joints[joint].setFastSpeed(speed);
  Serial.println(HOMING_SEEK_SPEED[joint]);
  joints[joint].setDirection(LOW);

  while (digitalRead(hardLimit[1]) == HIGH) {
    joints[joint].move(false);
  }
  joints[joint].setFastSpeed(SPEED_FAST[joint]);
  // while (digitalRead(X_MAX) == HIGH) {
  //   joints[1].move(false);
  // }
}

void resetAllMotors() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].reset();
  }
}

void moveJoint(Motor &motor, float increment, bool homing = false) {
  float targetAngle = stepsToAngle(motor.getCurrentPosition()) + increment;
    if (motor.isBeyondSoftLimit(targetAngle)) {
      Serial.println("Target exceeds soft limit.");
      return;
    }
    motor.setTargetPosition(angleToSteps(targetAngle));
    motor.setTotalSteps();
    motor.setDirection(motor.getTargetPosition() > motor.getCurrentPosition() ? HIGH : LOW);

    while (!motor.hasReachedTarget()) {
      if (!isMoveSafe() && !homing) {
        Serial.println("LIMIT SWITCH TRIGGERED!");
        motor.stop();
        break;
      }
      motor.move();
    }
  resetAllMotors();
}