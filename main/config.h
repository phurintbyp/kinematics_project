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
// For additional limit switches look at Z_MAX and aux pins

const int hardLimit[NUM_MOTORS] = {3, 2, 14, 15, 18};

#define M1_SOFT_MIN -360
#define M1_SOFT_MAX 11880
#define M2_SOFT_MIN -360
#define M2_SOFT_MAX 360
#define M3_SOFT_MIN -360
#define M3_SOFT_MAX 360
#define M4_SOFT_MIN -360
#define M4_SOFT_MAX 360
#define M5_SOFT_MIN -360
#define M5_SOFT_MAX 360

#define HOMING_SEEK 1.5 // (1/1.5) speed
#define HOMING_FEED 5 // (1/3) speed

const int HOMING_PULL_OFF[NUM_MOTORS] = {360, 90, 90, 90, 90};

//lower = higher speed
const long SPEED_SLOW[NUM_MOTORS] = {500, 1000, 1000, 1000, 1000};
const long SPEED_FAST[NUM_MOTORS] = {50, 150, 150, 300, 300};
const long HOMING_SEEK_SPEED[NUM_MOTORS] = {SPEED_FAST[0] * HOMING_SEEK, SPEED_FAST[1] * HOMING_SEEK, SPEED_FAST[2] * HOMING_SEEK, SPEED_FAST[3] * HOMING_SEEK, SPEED_FAST[4] * HOMING_SEEK};
const long HOMING_FEED_SPEED[NUM_MOTORS] = {SPEED_FAST[0] * HOMING_FEED, SPEED_FAST[1] * HOMING_FEED, SPEED_FAST[2] * HOMING_FEED, SPEED_FAST[3] * HOMING_FEED, SPEED_FAST[4] * HOMING_FEED};

#define MICROSTEP_ANGLE 0.05625

const long ACCEL_STEPS[NUM_MOTORS] = {400, 2000, 2000, 2000, 2000};

#endif