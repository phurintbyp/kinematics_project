# Arduino Integration for RRPRRR Robot Arm Control System

## Overview

This document explains how the web-based control interface communicates with the Arduino microcontroller to control the RRPRRR robotic arm configuration:

- R: Base rotation around the Z-axis
- R: Shoulder rotation (forward/backward)
- P: Prismatic joint extension/retraction
- R: Elbow rotation
- R: Elbow2 rotation
- R: End effector rotation 

The system uses a WebSocket connection from the frontend to a Python backend, which calculates joint positions using forward and inverse kinematics, and then sends commands to the Arduino via serial communication.

## Physical Model

The robot arm consists of the following links:

- Base height: Vertical offset from ground
- Link1: From base to shoulder joint
- Link2: Prismatic extension (variable length)
- Link3: From prismatic joint to elbow joint
- Link4: From elbow joint to elbow2 joint
- End effector: From elbow2 joint to end effector tip

## Command Flow

1. **Web Interface**: User interacts with the pendant interface to control the robot (jog controls, program execution)
2. **WebSocket**: Commands are sent to the backend via WebSocket
3. **Kinematics Engine**: Backend calculates all joint positions using forward/inverse kinematics
4. **Arduino Communication**: Joint positions are sent to Arduino as JSON commands
5. **Motor Control**: Arduino interprets commands and controls stepper motors

## Communication Protocol

The system uses JSON-based commands sent over a serial connection with the following settings:
- Baud Rate: 115200
- Port: Configurable (default: /dev/ttyACM0)
- Command Delay: 50ms between commands

## Implementation Details

The Arduino communication is implemented as follows:

1. **Initialization**: The Arduino communicator is initialized in `app.py` when the application starts:
   ```python
   arduino = None
   if not SIMULATION_MODE:
       arduino = ArduinoCommunicator()
   ```

2. **Router Integration**: The Arduino instance is passed to the motion module:
   ```python
   motion.arduino_communicator = arduino
   ```

3. **Command Sending**: When joint positions change (via jogging, moveJ, moveL), commands are sent to the Arduino.

4. **Simulation Mode**: When `SIMULATION_MODE` is set to `True` in `config.py`, no commands are sent to the Arduino, allowing testing without physical hardware.

## Jogging System

The robotic arm uses a standardized incremental jogging system with the following increment values:

- **Ultra Fine**: 0.1 degrees/mm (for precise adjustments)
- **Fine**: 1 degree/mm (for fine adjustments)
- **Medium**: 5 degrees/mm (default increment)
- **Coarse**: 10 degrees/mm (for larger movements)
- **X-Large**: 50 degrees/mm (for rapid positioning)

These values are configurable in `config.py` and are validated by the backend to ensure only standard increments are used.

## Command Format

### Joint Position Command

When controlling the robot, the backend sends *complete* joint positions for all 6 joints:

```json
{
  "cmd": "setJointPositions",
  "positions": {
    "j1": 0.0,      // Base rotation (degrees)
    "j2": 45.0,     // Shoulder rotation (degrees) 
    "j3": 150.0,    // Prismatic extension (mm)
    "j4": -30.0,    // Elbow rotation (degrees)
    "j5": 15.0,     // Elbow2 rotation (degrees)
    "j6": 0.0       // End effector rotation (degrees)
  }
}
```

### Individual Joint Movement

For incremental jogging of individual joints:

```json
{
  "cmd": "moveJoint",
  "joint": "j2",    // j1-j6 corresponding to the 6 joints
  "increment": 5.0  // Positive or negative value (degrees or mm)
}
```

### Cartesian Movement Command

For cartesian space movement (requires the Arduino to execute inverse kinematics or the backend sends pre-calculated joint positions):

```json
{
  "cmd": "setCartesianPosition",
  "position": {
    "x": 250.0,      // X coordinate (mm)
    "y": 0.0,        // Y coordinate (mm)
    "z": 150.0,      // Z coordinate (mm)
    "roll": 0.0,     // Roll angle (degrees)
    "pitch": 0.0,    // Pitch angle (degrees)
    "yaw": 0.0       // Yaw angle (degrees)
  }
}
```

### Emergency Stop

```json
{
  "cmd": "estop"
}
```

## Response Format

The Arduino should respond to commands with a JSON response:

```json
{
  "status": "ok"
}
```

Or in case of errors:

```json
{
  "status": "error",
  "message": "Joint limit exceeded"
}
```

## Arduino Responsibilities

The Arduino code should handle:

1. **Parsing Commands**: Reading and parsing JSON commands from serial
2. **Position Control**: Moving stepper motors to the requested joint positions
3. **Enforcing Limits**: Respecting physical limits of joints (though also done in backend)
4. **Error Reporting**: Providing feedback when commands cannot be executed
5. **Smooth Motion**: Implementing acceleration/deceleration for smooth movement

## Joint Mapping

| System Name            | Arduino Joint | Type        | Limits             |
|------------------------|--------------:|-------------|---------------------|
| base_rotation          | j1            | Rotary      | -180° to 180°      |
| shoulder_rotation      | j2            | Rotary      | -90° to 90°        |
| prismatic_extension    | j3            | Prismatic   | 0mm to 200mm       |
| elbow_rotation         | j4            | Rotary      | -90° to 90°        |
| elbow2_rotation        | j5            | Rotary      | -90° to 90°        |
| end_effector_rotation  | j6            | Rotary      | -180° to 180°      |

## Implementation Notes

1. The system is designed to work in simulation mode without Arduino hardware during development.
2. The backend handles all kinematics calculations, so the Arduino only needs to position the motors.
3. Each joint position command contains the absolute positions for all joints.
4. The Arduino should implement appropriate acceleration/deceleration for smooth motion.

## Error Handling

- If a command cannot be executed, the Arduino should respond with an error message.
- If the Arduino does not respond within the timeout period, the connection is considered failed.
- The system will attempt to reconnect to the Arduino if communication is lost.

## Testing Arduino Integration

You can test the Arduino integration by:

1. Setting `SIMULATION_MODE = False` in `config.py`
2. Ensuring the correct serial port is set in `ARDUINO_CONFIG`
3. Starting the application and using the web interface to send commands

When the system is working correctly, the robot should move according to the web interface controls, with all kinematics calculations handled by the backend.
