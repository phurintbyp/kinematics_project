# RRPRRR Robot Arm Control Pendant

A web-based control interface for a 6-DOF robotic arm with RRPRRR (Revolute-Revolute-Prismatic-Revolute-Revolute-Revolute) configuration. This project is designed to run on a Raspberry Pi that communicates with an Arduino for stepper motor control.

## Features

- **Intuitive Web Interface**: Control the robot arm from any device with a web browser
- **Jogging Controls**: Precisely move individual joints or the end effector
- **Program Mode**: Create, save, and execute sequences of movements
- **Real-time Position Feedback**: Monitor joint angles and end effector position
- **Emergency Stop**: Quickly halt all operations with a prominent emergency stop button
- **Configurable Parameters**: Easily adjust all settings through a centralized configuration file

## System Architecture

The system consists of:

1. **Web Server**: Flask-based backend with SocketIO for real-time communication
2. **Frontend**: HTML/CSS/JavaScript interface with responsive design
3. **Kinematics Engine**: Forward and inverse kinematics calculations
4. **Arduino Communication**: Serial interface to control the physical robot (or simulation mode)

## Arduino Communication Protocol

This section details how the Raspberry Pi communicates with the Arduino to control the robot arm. This information is crucial for anyone implementing the Arduino firmware.

### Serial Connection Parameters

- **Port**: Configurable in `config.py` (default: `/dev/ttyUSB0`)
- **Baud Rate**: 115200 bps
- **Data Format**: 8 data bits, no parity, 1 stop bit (8N1)

### Command Protocol

All commands are sent as JSON strings terminated with a newline character (`\n`). The Arduino should parse these commands and respond accordingly.

#### Command Types

1. **Joint Movement (moveJ)**
   ```json
   {"cmd": "moveJ", "base_rotation": 45.0, "shoulder_rotation": 30.0, "prismatic_extension": 150.0, "elbow_rotation": 20.0, "wrist_rotation": 10.0, "end_effector_rotation": 0.0}
   ```
   Moves all joints to the specified positions (in degrees for rotational joints, mm for prismatic).

2. **Emergency Stop**
   ```json
   {"cmd": "estop"}
   ```
   Immediately stops all motion.

3. **Status Request**
   ```json
   {"cmd": "status"}
   ```
   Requests the current status of the robot.

4. **Connection Test**
   ```json
   {"cmd": "ping"}
   ```
   Simple connectivity test.

### Expected Responses

The Arduino should respond to each command with a JSON string, also terminated with a newline:

1. **Acknowledgment**
   ```json
   {"status": "ok", "message": "Command received"}
   ```

2. **Error**
   ```json
   {"status": "error", "message": "Error description"}
   ```

3. **Status Response**
   ```json
   {"status": "ok", "positions": {"base_rotation": 45.0, "shoulder_rotation": 30.0, "prismatic_extension": 150.0, "elbow_rotation": 20.0, "wrist_rotation": 10.0, "end_effector_rotation": 0.0}}
   ```

4. **Ping Response**
   ```json
   {"status": "ok", "message": "pong"}
   ```

### Arduino Implementation Guidelines

1. **Serial Buffer Handling**:
   - Implement a robust serial buffer to collect incoming data until a newline is received
   - Parse the JSON string using a lightweight JSON parser (e.g., ArduinoJson library)

2. **Motor Control**:
   - Use stepper motor drivers (e.g., A4988, DRV8825) for precise control
   - Implement acceleration/deceleration profiles to prevent missed steps
   - Consider using a dedicated stepper motor library (e.g., AccelStepper)

3. **Safety Features**:
   - Implement hardware limit switches for each joint
   - Process emergency stop commands with highest priority
   - Add watchdog functionality to stop motion if communication is lost

4. **Example Arduino Code Structure**:
   ```cpp
   #include <ArduinoJson.h>
   #include <AccelStepper.h>

   // Define stepper motors
   AccelStepper baseMotor(AccelStepper::DRIVER, BASE_STEP_PIN, BASE_DIR_PIN);
   // Define other motors...

   void setup() {
     Serial.begin(115200);
     // Configure motors...
   }

   void loop() {
     // Check for incoming commands
     if (Serial.available()) {
       String command = Serial.readStringUntil('\n');
       processCommand(command);
     }
     
     // Update motor positions
     baseMotor.run();
     // Update other motors...
   }

   void processCommand(String commandStr) {
     StaticJsonDocument<256> doc;
     DeserializationError error = deserializeJson(doc, commandStr);
     
     if (error) {
       sendErrorResponse("Invalid JSON");
       return;
     }
     
     String cmd = doc["cmd"];
     
     if (cmd == "moveJ") {
       // Process moveJ command
       float baseAngle = doc["base_rotation"];
       // Get other joint values...
       moveJoints(baseAngle, ...);
       sendAcknowledgment();
     } 
     else if (cmd == "estop") {
       emergencyStop();
       sendAcknowledgment();
     }
     // Handle other commands...
   }
   ```

## Installation and Setup

### Prerequisites

- Python 3.8+
- Arduino IDE (if connecting to physical hardware)
- Modern web browser

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pendant
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the application in `config.py`:
   - Set `SIMULATION_MODE = False` to connect to real hardware
   - Adjust `ARDUINO_CONFIG['PORT']` to match your Arduino's serial port

## Usage

1. Start the server:
   ```bash
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5001
   ```

3. Use the interface to:
   - Jog individual joints using the + and - buttons
   - Save positions for later use
   - Create programs by sequencing saved positions
   - Execute programs with the Run button
   - Use the emergency stop button if needed

## Configuration

All configurable parameters are centralized in `config.py`, including:

- Flask and server settings
- Arduino communication parameters
- Robot physical dimensions
- Joint limits
- Default positions
- UI settings

## License

[MIT License](LICENSE)

## Acknowledgments

- Built with Flask and Socket.IO
- Uses modern web technologies for the frontend
- Developed for educational and research purposes
