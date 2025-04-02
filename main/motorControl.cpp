#include "motorControl.h"
#include "motor.h"
#include "config.h"
#include "safety.h"

// Create global array of motors
Motor joints[NUM_MOTORS] = {
  Motor(M1_STEP, M1_DIR, M1_ENABLE),
  Motor(M2_STEP, M2_DIR, M2_ENABLE),
  Motor(M3_STEP, M3_DIR, M3_ENABLE),
  Motor(M4_STEP, M4_DIR, M4_ENABLE),
  Motor(M5_STEP, M5_DIR, M5_ENABLE)
};

enum HomingState {
  IDLE,
  SEEKING_FAST,
  FIRST_PULL_OFF,
  SEEKING_SLOW,
  SECOND_PULL_OFF,
  DONE
};

HomingState homingState = IDLE;

// The joint we are homing
int homingJoint = -1;

// Timestamps for non-blocking time checks
unsigned long homingTimer = 0;

// This indicates how far we want to pull off
float pullOffDistance = 0.0;


bool homingAll = false;
int currentJoint = 0;


void initMotors() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].enableMotor();
    joints[i].setFastSpeed(SPEED_FAST[i]);
    joints[i].setSlowSpeed(SPEED_SLOW[i]);
    joints[i].setAccelSteps(ACCEL_STEPS[i]);
  }
  Serial.println("Motors initialized!");
}

void setAllSoftLimits(float m1Min, float m1Max,
                      float m2Min, float m2Max,
                      float m3Min, float m3Max,
                      float m4Min, float m4Max,
                      float m5Min, float m5Max)
{
  joints[0].setSoftLimit(m1Min, m1Max);
  joints[1].setSoftLimit(m2Min, m2Max);
  joints[2].setSoftLimit(m3Min, m3Max);
  joints[3].setSoftLimit(m4Min, m4Max);
  joints[4].setSoftLimit(m5Min, m5Max);
}

// Non-blocking setJointPositions
void setJointPositions(JsonObject &positions) {
  float angles[NUM_MOTORS] = {
    positions["j1"],
    positions["j2"],
    positions["j3"],
    positions["j4"],
    positions["j5"]
  };

  // Convert angles => steps, assign target
  for (int i = 0; i < NUM_MOTORS; i++) {
    // If you want to do a soft limit check, do it here:
    // if (joints[i].isBeyondSoftLimit(angles[i])) { ... }
    long steps = angleToSteps(angles[i]);
    joints[i].setTargetPosition(steps);
    joints[i].setDirection(joints[i].getTargetPosition() > joints[i].getCurrentPosition() ? HIGH : LOW);
    joints[i].reset(); // So it can accelerate from 0 again
  }
  while (!joints[0].hasReachedTarget() || !joints[1].hasReachedTarget() || !joints[2].hasReachedTarget() || !joints[3].hasReachedTarget() || !joints[4].hasReachedTarget() ) {
    if (!isMoveSafe()) {
      Serial.println("LIMIT SWITCH TRIGGERED!");
      stopAll();
      break;
    }
    updateAll(true);
  }
  Serial.println("{“status”: “move_done”}");
}

// The function that your loop() will call frequently
// to let the motors do their stepping in parallel
void updateAll(bool enableAcceleration) {
  for (int i = 0; i < NUM_MOTORS; i++) {
    if (!joints[i].hasReachedTarget()) {
      joints[i].update(enableAcceleration);
    }
  }
}

// Example usage: if you want a blocking approach until done
// you can do something like:
void blockUntilAllReached(bool enableAcceleration) {
  bool allReached = false;
  while (!allReached) {
    allReached = true;
    for (int i = 0; i < NUM_MOTORS; i++) {
      if (!joints[i].hasReachedTarget()) {
        allReached = false;
        // update them
        joints[i].update(enableAcceleration);
      }
    }
  }
}

void stopAll() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].stop();
  }
}

void resetAllMotors() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    joints[i].reset();
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

void printCurrentPos() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    Serial.print("Joint ");
    Serial.print(i + 1);
    Serial.print(" pos: ");
    Serial.println(joints[i].getCurrentPosition());
  }
  Serial.println("----------------------");
}

void moveJoint(Motor &motor, float increment, bool homing) {
  float currentAngle = motor.getCurrentPosition() * MICROSTEP_ANGLE;
  float targetAngle  = currentAngle + increment;
  long  steps        = (long)round(targetAngle / MICROSTEP_ANGLE);
  
  motor.setTargetPosition(steps);
  motor.setDirection(motor.getTargetPosition() > motor.getCurrentPosition() ? HIGH : LOW);
  motor.reset(); // so it can accelerate from 0 again

  // If you want to block until done:
  while (!motor.hasReachedTarget()) {
    if (!isMoveSafe() && !homing) {
      Serial.println("LIMIT SWITCH TRIGGERED!");
      motor.stop();
      break;
    }
    motor.update(false); 
  }
}


void startHoming(int joint, bool seeking = true) {
  homingJoint = joint;
  homingState = seeking ? SEEKING_FAST : SEEKING_SLOW;
  pullOffDistance = HOMING_PULL_OFF[joint];

  // Decide direction for homing, e.g. LOW if limit is on that side
  bool homingDir = LOW;  
  joints[joint].setDirection(LOW);

  // Set a large target so the motor keeps moving in that direction
  long bigTarget = (homingDir == LOW) ? -999999L : 999999L;
  joints[joint].setTargetPosition(bigTarget);

  // Set speed: fast if seeking=true, else slow
  float speed = seeking ? HOMING_SEEK_SPEED[joint] : HOMING_FEED_SPEED[joint];
  joints[joint].setFastSpeed(speed);
  joints[joint].reset(); // so we can accelerate from zero if needed

  Serial.print("Homing started for joint ");
  Serial.print(joint);
  Serial.print(" in ");
  Serial.println(seeking ? "FAST" : "SLOW");
}


void updateHoming() {
  switch (homingState) {

    // Idle means we're not homing
    case IDLE:
      // Do nothing
      break;

    // 1) SEEKING_FAST: move quickly to find the limit switch
    case SEEKING_FAST: {
      if (digitalRead(hardLimit[1]) == LOW) {
        // Limit triggered
        joints[homingJoint].stop(); // stop stepping
        // Transition to FIRST_PULL_OFF
        homingState = FIRST_PULL_OFF;
        joints[homingJoint].setCurrentPosition(0);
        joints[homingJoint].reset(); // so we can do a new movement from 0 steps

        Serial.println("Limit triggered: now pulling off (fast -> first pull off).");
      } else {
        // Keep stepping this motor
        joints[homingJoint].update(false); // No acceleration needed, we are already at "fast" speed
      }
      break;
    }

    // 2) FIRST_PULL_OFF: move away from switch by pullOffDistance
    case FIRST_PULL_OFF: {
      moveJoint(joints[homingJoint], HOMING_PULL_OFF[homingJoint], true);

      Serial.println("First pull off done -> seeking slow");
        // Next -> SEEKING_SLOW
        homingState = SEEKING_SLOW;

        // Set big target again, but slow speed
        bool homingDir = LOW; // same direction as before
        long bigTarget = (homingDir == LOW) ? -999999L : 999999L;
        joints[homingJoint].setTargetPosition(bigTarget);
        joints[homingJoint].setFastSpeed(HOMING_FEED_SPEED[homingJoint]);
        joints[homingJoint].setDirection(LOW);
        joints[homingJoint].reset();
      
      break;
    }

    // 3) SEEKING_SLOW: approach limit again slowly
    case SEEKING_SLOW: {
      if (digitalRead(hardLimit[1]) == LOW) {
        // triggered again
        joints[homingJoint].stop();
        homingState = SECOND_PULL_OFF;

        // second pull off
        joints[homingJoint].setCurrentPosition(0);
        joints[homingJoint].reset();

        Serial.println("Switch triggered again -> second pull off");
      } else {
        joints[homingJoint].update(false);
      }
      break;
    }

    // 4) SECOND_PULL_OFF: final pull off
    case SECOND_PULL_OFF: {
      moveJoint(joints[homingJoint], HOMING_PULL_OFF[homingJoint], true);

      joints[homingJoint].setCurrentPosition(0); // final pos = 0
      joints[homingJoint].reset();
      homingState = DONE;
      Serial.println("Homing complete -> final pos = 0");
      break;
    }

    // 5) DONE: not doing anything, user can set homingState = IDLE or call startHoming() for next joint
    case DONE: 
      // We remain here or we can set IDLE 
      break;
  }
}

void home(int joint) {
  startHoming(joint, true); // seeking = true => fast approach

  // Wait until homingState == DONE
  while (homingState != DONE) {
    updateHoming();
    delay(1); // small yield
  }
}

void homeAll() {
  for (int j = 0; j < NUM_MOTORS; j++) {
    home(j);  // blocking call from above
  }
  Serial.println("{“status”: “home_done”}");
}

long angleToSteps(float angle) {
  return round(angle / MICROSTEP_ANGLE);
}

float stepsToAngle(long steps) {
  return steps * MICROSTEP_ANGLE;
}
