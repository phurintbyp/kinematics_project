#ifndef CONFIG_H
#define CONFIG_H

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

#define HOMING_SEEK 1.5 // (1/1.5) speed
#define HOMING_FEED 3 // (1/3) speed
#define HOMING_PULL_OFF 15 // degrees

//lower = higher speed
#define M1_SPEED_SLOW 300
#define M2_SPEED_SLOW 300
#define M3_SPEED_SLOW 300

#define M1_SPEED_FAST 100
#define M2_SPEED_FAST 100
#define M3_SPEED_FAST 100

#define MICROSTEP_ANGLE 0.05625

#define ACCEL_STEPS_M1 16000
#define ACCEL_STEPS_M2 16000
#define ACCEL_STEPS_M3 16000

#endif