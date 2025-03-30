#ifndef CONFIG_H
#define CONFIG_H

#define NUM_MOTORS 5

#define M1_STEP 54
#define M1_DIR 55
#define M1_ENABLE 38

#define M2_STEP 60
#define M2_DIR 61
#define M2_ENABLE 56

#define M3_STEP 46
#define M3_DIR 48
#define M3_ENABLE 62

// Repurposed Extruder 0 pin
#define M4_STEP 26
#define M4_DIR 28
#define M4_ENABLE 24

// Repurposed Extruder 1 pin
#define M5_STEP 34
#define M5_DIR 36
#define M5_ENABLE 30

// Limit Switches
// For additional limit switches look at aux pins
#define X_MIN 3
#define X_MAX 2
#define Y_MIN 14
#define Y_MAX 15
#define Z_MIN 18
#define Z_MAX 19

#define M1_SOFT_MIN -360
#define M1_SOFT_MAX 360
#define M2_SOFT_MIN -360
#define M2_SOFT_MAX 360
#define M3_SOFT_MIN -360
#define M3_SOFT_MAX 360
#define M4_SOFT_MIN -360
#define M4_SOFT_MAX 360
#define M5_SOFT_MIN -360
#define M5_SOFT_MAX 360

#define HOMING_SEEK 1.5 // (1/1.5) speed
#define HOMING_FEED 3 // (1/3) speed
#define HOMING_PULL_OFF 15 // degrees

//lower = higher speed
const long SPEED_SLOW[5] = {1000, 1000, 1000, 1000, 1000};
const long SPEED_FAST[5] = {150, 150, 150, 300, 300};
const long HOMING_SEEK_SPEED[5] = {SPEED_FAST[0] * HOMING_SEEK, SPEED_FAST[1] * HOMING_SEEK, SPEED_FAST[2] * HOMING_SEEK, SPEED_FAST[3] * HOMING_SEEK, SPEED_FAST[4] * HOMING_SEEK};
const long HOMING_FEED_SPEED[5] = {SPEED_FAST[0] * HOMING_FEED, SPEED_FAST[1] * HOMING_FEED, SPEED_FAST[2] * HOMING_FEED, SPEED_FAST[3] * HOMING_FEED, SPEED_FAST[4] * HOMING_FEED};

#define MICROSTEP_ANGLE 0.05625

const long ACCEL_STEPS[5] = {400, 2000, 2000, 2000, 2000};

#endif