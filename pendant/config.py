"""
Configuration file for the RRPRRR robotic arm control system
Contains robot dimensions, joint limits, Arduino communication settings, and simulation mode
"""

# Set to True to run in simulation mode without Arduino hardware
# To enable hardware control, set this to False and ensure Arduino is connected
SIMULATION_MODE = True  # Change to False for real hardware control

# Arduino communication settings
ARDUINO_CONFIG = {
    'PORT': '/dev/ttyACM0',  # Default Arduino port on Raspberry Pi
    'BAUD_RATE': 115200,
    'TIMEOUT': 1.0,          # Serial timeout in seconds
    'COMMAND_DELAY': 0.05    # Delay between commands in seconds
}

# Robot physical dimensions in mm
ROBOT_DIMENSIONS = {
    'BASE_HEIGHT': 100,      # Height of the base from ground
    'LINK1_LENGTH': 150,     # Length of the first link (shoulder to prismatic joint)
    'LINK2_MIN': 0,          # Minimum extension of prismatic joint
    'LINK2_MAX': 200,        # Maximum extension of prismatic joint
    'LINK3_LENGTH': 150,     # Length of the third link (prismatic joint to elbow)
    'LINK4_LENGTH': 100,     # Length of the fourth link (elbow to elbow2)
    'END_EFFECTOR_LENGTH': 100  # Length of end effector
}

# Joint limits in degrees (min, max) or mm for prismatic joint
JOINT_LIMITS = {
    'BASE_ROTATION': (-180, 180),         # Base rotation (degrees)
    'SHOULDER_ROTATION': (-90, 90),       # Shoulder rotation (degrees)
    'PRISMATIC_EXTENSION': (0, 200),      # Prismatic extension (mm)
    'ELBOW_ROTATION': (-135, 135),        # Elbow rotation (degrees)
    'ELBOW2_ROTATION': (-90, 90),         # Elbow2 rotation (degrees)
    'END_EFFECTOR_ROTATION': (-180, 180)  # End effector rotation (degrees)
}

# Default joint positions
DEFAULT_JOINT_POSITIONS = {
    'base_rotation': 0,
    'shoulder_rotation': 0,
    'prismatic_extension': 50,
    'elbow_rotation': 0,
    'elbow2_rotation': 0,
    'end_effector_rotation': 0
}

# Jog increments for different modes
JOG_INCREMENTS = {
    'joint': {  # Degrees for rotary joints, mm for prismatic
        'ultra_fine': 0.1,
        'fine': 1,
        'medium': 5,
        'coarse': 10,
        'x_large': 50
    },
    'cartesian': {  # mm for position, degrees for orientation
        'ultra_fine': 0.1,
        'fine': 1,
        'medium': 5,
        'coarse': 10,
        'x_large': 50
    }
}

# Jogging configuration
JOG_CONFIG = {
    'UPDATE_INTERVAL': 0.05,  # Seconds between jog updates
    'ACCELERATION': 50,       # Units per second^2
    'DECELERATION': 100,      # Units per second^2
    'MAX_VELOCITY': {
        'joint': {
            'base_rotation': 30,          # Degrees per second
            'shoulder_rotation': 20,
            'prismatic_extension': 50,    # mm per second
            'elbow_rotation': 30,
            'elbow2_rotation': 45,
            'end_effector_rotation': 60
        },
        'cartesian': {
            'x': 50,                      # mm per second
            'y': 50,
            'z': 30,
            'roll': 45,                   # Degrees per second
            'pitch': 45,
            'yaw': 45
        }
    }
}

# Robot configuration
ROBOT_CONFIG = {
    # Joint types (rotary or prismatic)
    'JOINT_TYPES': {
        'base_rotation': 'rotary',
        'shoulder_rotation': 'rotary',
        'prismatic_extension': 'prismatic',
        'elbow_rotation': 'rotary',
        'elbow2_rotation': 'rotary',
        'end_effector_rotation': 'rotary'
    },
    
    # Joint home positions
    'HOME_POSITION': {
        'base_rotation': 0,
        'shoulder_rotation': 0,
        'prismatic_extension': 50,
        'elbow_rotation': 0,
        'elbow2_rotation': 0,
        'end_effector_rotation': 0
    },
    
    # Joint speeds (degrees/second or mm/second)
    'DEFAULT_SPEEDS': {
        'base_rotation': 30,
        'shoulder_rotation': 20,
        'prismatic_extension': 50,
        'elbow_rotation': 30,
        'elbow2_rotation': 45,
        'end_effector_rotation': 60
    },

    # Workspace limits (mm and degrees)
    'WORKSPACE_LIMITS': {
        'x': (-500, 500),
        'y': (-500, 500),
        'z': (0, 500),
        'roll': (-180, 180),
        'pitch': (-90, 90),
        'yaw': (-180, 180)
    }
}

# Movement parameters
MOVEMENT_PARAMS = {
    'MAX_ACCELERATION': 50,      # Maximum acceleration for smooth movements
    'INTERPOLATION_POINTS': 50,  # Number of points for trajectory interpolation
    'MIN_MOVEMENT_TIME': 0.5,    # Minimum time for any movement (seconds)
    'JOG_INCREMENT': {           # Default jog increments
        'joint': 5,              # 5 degrees for rotary joints
        'cartesian': 10          # 10 mm for cartesian movements
    }
}

# Web server settings
SERVER_CONFIG = {
    'HOST': '0.0.0.0',           # Listen on all interfaces
    'PORT': 8000,                # Web server port
    'DEBUG': True,               # Enable debug mode
    'WEBSOCKET_PATH': '/ws',     # WebSocket endpoint
    'STATIC_DIR': 'static',      # Static files directory
    'TEMPLATES_DIR': 'templates' # Templates directory
}
