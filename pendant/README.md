# RRPRRR Robot Arm Control Pendant

A web-based control interface for operating a RRPRRR configuration robotic arm. This project is designed to run on a Raspberry Pi that communicates with an Arduino for stepper motor control.

## Features

- **Joint Movement (moveJ)**: Control individual joint positions
- **Linear Movement (moveL)**: Control end effector position in Cartesian space
- **Jogging**: Make incremental adjustments to joint positions
- **Kinematics**: Robust forward and inverse kinematics calculations
- **Simulation Mode**: Test the interface without connecting to actual hardware

## Robot Configuration (RRPRRR)

- **Base Rotation (R)**: Rotates around the z-axis
- **Shoulder Rotation (R)**: Manages forward and backward motion
- **Prismatic Joint (P)**: Linear extension between two links via a lead screw
- **Elbow Rotation (R)**: Connects to the prismatic joint
- **Wrist Rotation (R)**: Controls wrist rotational movement
- **End Effector Rotation (R)**: Rotates the tool or gripper

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd pendant
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Running the Application

### Simulation Mode (Default)

By default, the application runs in simulation mode, which doesn't require an Arduino connection. This is perfect for testing the web interface and kinematics calculations.

```
python app.py
```

The web interface will be available at http://localhost:5001

### Hardware Mode

To run with actual hardware:

1. Connect the Arduino to your Raspberry Pi
2. Open `app.py` and set `SIMULATION_MODE = False`
3. Update the serial port in `app.py` if needed:
   ```python
   arduino_comm = ArduinoCommunicator('/dev/ttyUSB0', 115200)  # Adjust port as needed
   ```
4. Run the application:
   ```
   python app.py
   ```

## Arduino Communication

The application communicates with an Arduino that controls the stepper motors. The Arduino should be programmed to accept the following commands:

- `MOVE {json_data}`: Move the joints to the specified positions
- `ESTOP`: Emergency stop
- `STATUS`: Get the current status of the robot
- `PING`: Check connection (should respond with `PONG`)

## Project Structure

- `app.py`: Main Flask application
- `kinematics.py`: Forward and inverse kinematics calculations
- `arduino_communication.py`: Communication with the Arduino
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files

## Future Improvements

- 3D visualization of the robot arm
- Path planning and trajectory generation
- User authentication and multiple user support
- Saving and loading robot positions
- Integration with computer vision for object detection and grasping
