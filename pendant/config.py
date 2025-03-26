"""
Configuration file for the RRPRRR Robot Arm Control Pendant
All configurable parameters are centralized in this file
"""

# Flask and SocketIO Configuration
FLASK_CONFIG = {
    'SECRET_KEY': 'robotics-pendant',
    'HOST': '0.0.0.0',
    'PORT': 5001,
    'DEBUG': True
}

# Operation Mode
SIMULATION_MODE = True  # Set to False to enable actual Arduino communication

# Arduino Communication Settings
ARDUINO_CONFIG = {
    'PORT': '/dev/ttyUSB0',  # Adjust based on your system
    'BAUD_RATE': 115200,
    'TIMEOUT': 1.0,
    'COMMAND_DELAY': 0.1  # Delay between commands in seconds
}

# Robot Physical Parameters (in mm)
ROBOT_DIMENSIONS = {
    'BASE_HEIGHT': 100.0,
    'LINK1_LENGTH': 150.0,  # Length of first link (shoulder to prismatic joint)
    'LINK2_MIN': 100.0,     # Minimum extension of prismatic joint
    'LINK2_MAX': 300.0,     # Maximum extension of prismatic joint
    'LINK3_LENGTH': 150.0,  # Length of the link after prismatic joint
    'END_EFFECTOR_LENGTH': 50.0  # Length of end effector
}

# Joint Limits (in degrees or mm)
JOINT_LIMITS = {
    'BASE_ROTATION': (-180.0, 180.0),
    'SHOULDER_ROTATION': (-90.0, 90.0),
    'PRISMATIC_EXTENSION': (ROBOT_DIMENSIONS['LINK2_MIN'], ROBOT_DIMENSIONS['LINK2_MAX']),  # in mm
    'ELBOW_ROTATION': (-120.0, 120.0),
    'WRIST_ROTATION': (-180.0, 180.0),
    'END_EFFECTOR_ROTATION': (-180.0, 180.0)
}

# Default Initial Joint Positions
DEFAULT_JOINT_POSITIONS = {
    'base_rotation': 0.0,      # degrees
    'shoulder_rotation': 0.0,  # degrees
    'prismatic_extension': ROBOT_DIMENSIONS['LINK2_MIN'],  # mm
    'elbow_rotation': 0.0,     # degrees
    'wrist_rotation': 0.0,     # degrees
    'end_effector_rotation': 0.0  # degrees
}

# Jogging Increments
JOG_INCREMENTS = {
    'JOINT': 5.0,  # degrees for rotational joints
    'PRISMATIC': 10.0,  # mm for prismatic joint
    'EE_LINEAR': 10.0,  # mm for end effector linear movement
    'EE_ANGULAR': 5.0   # degrees for end effector angular movement
}

# File Paths
FILE_PATHS = {
    'SAVED_POSITIONS': 'data/saved_positions.json',
    'PROGRAM_SEQUENCES': 'data/program_sequences.json'
}

# UI Settings
UI_SETTINGS = {
    'NOTIFICATION_TIMEOUT': 3000,  # milliseconds
    'POSITION_DECIMAL_PLACES': 2,
    'UPDATE_INTERVAL': 100  # milliseconds
}
