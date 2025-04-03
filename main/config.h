#ifndef CONFIG_H
#define CONFIG_H

#define NUM_MOTORS 4

#define M1_STEP 54
#define M1_DIR 55
#define M1_ENABLE 38

// swap pins of y and z

#define M2_STEP 60
#define M2_DIR 61
#define M2_ENABLE 56

// #define M3_STEP 46
// #define M3_DIR 48
// #define M3_ENABLE 62

// Repurposed Extruder 0 pin
#define M3_STEP 26
#define M3_DIR 28
#define M3_ENABLE 24

// Repurposed Extruder 1 pin
#define M4_STEP 36
#define M4_DIR 34
#define M4_ENABLE 30

// Limit Switches
// For additional limit switches look at Z_MAX and aux pins

const int hardLimit[NUM_MOTORS] = {3, 2, 14, 15};

#define HOMING_SEEK 1.5 // (1/1.5) speed
#define HOMING_FEED 5 // (1/5) speed

const int HOMING_PULL_OFF[NUM_MOTORS] = {90, 90, 150, 90}; // Degrees

//lower = higher speed
const long SPEED_SLOW[NUM_MOTORS] = {500, 500, 500, 500};
const long SPEED_FAST[NUM_MOTORS] = {300, 200, 100, 300};
const long HOMING_SEEK_SPEED[NUM_MOTORS] = {SPEED_FAST[0] * HOMING_SEEK, SPEED_FAST[1] * HOMING_SEEK, SPEED_FAST[2] * HOMING_SEEK, SPEED_FAST[3] * HOMING_SEEK};
const long HOMING_FEED_SPEED[NUM_MOTORS] = {SPEED_FAST[0] * HOMING_FEED, SPEED_FAST[1] * HOMING_FEED, SPEED_FAST[2] * HOMING_FEED, SPEED_FAST[3] * HOMING_FEED};

#define MICROSTEP_ANGLE 0.05625

const long ACCEL_STEPS[NUM_MOTORS] = {400, 2000, 2000, 2000};
const bool MOTOR_INVERTED[NUM_MOTORS] = {false, false, false, false};

#endif