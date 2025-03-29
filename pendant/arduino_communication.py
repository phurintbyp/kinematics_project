import serial
import time
import json
import threading
from config import ARDUINO_CONFIG

class ArduinoCommunicator:
    """
    Handles communication with the Arduino that controls the stepper motors
    for the RRPRRR robotic arm.
    """
    def __init__(self, port=None, baud_rate=None, timeout=None):
        # Use values from config if not explicitly provided
        self.port = port if port is not None else ARDUINO_CONFIG['PORT']
        self.baud_rate = baud_rate if baud_rate is not None else ARDUINO_CONFIG['BAUD_RATE']
        self.timeout = timeout if timeout is not None else ARDUINO_CONFIG['TIMEOUT']
        self.command_delay = ARDUINO_CONFIG['COMMAND_DELAY']
        self.serial = None
        self.connected = False
        self.lock = threading.Lock()  # Thread lock for serial communication
        # Try to connect on initialization
        self.connect()

    def connect(self):
        """
        Establish connection with the Arduino
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close the serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("Disconnected from Arduino")
    
    def send_command(self, command_dict):
        """
        Send a command to the Arduino as JSON
        
        Args:
            command_dict: Dictionary containing the command
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        if not self.connected or not self.serial:
            print("Not connected to Arduino")
            return False
        
        try:
            with self.lock:  # Ensure thread safety for serial communication
                # Convert command to JSON string and add newline
                command_json = json.dumps(command_dict) + '\n'
                self.serial.write(command_json.encode())
                self.serial.flush()
                time.sleep(self.command_delay)  # Small delay to ensure command is processed
                
                # Wait for and parse response
                response = self.serial.readline().decode().strip()
                if response:
                    try:
                        response_dict = json.loads(response)
                        if response_dict.get('status') == 'ok':
                            return True
                        else:
                            print(f"Arduino error: {response_dict.get('message', 'Unknown error')}")
                            return False
                    except json.JSONDecodeError:
                        print(f"Invalid response from Arduino: {response}")
                        return False
                else:
                    print("No response from Arduino")
                    return False
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
            return False
    
    def send_joint_command(self, joint_positions):
        """
        Send joint movement command with specific position for each joint
        
        Args:
            joint_positions: Dictionary of joint positions (degrees for rotary joints, mm for prismatic)
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        # We're sending specific joint positions to the Arduino
        # Arduino only needs to move motors to these positions, not calculate kinematics
        command = {
            'cmd': 'setJointPositions',
            'positions': {
                'j1': joint_positions['base_rotation'],
                'j2': joint_positions['shoulder_rotation'],
                'j3': joint_positions['prismatic_extension'],
                'j4': joint_positions['elbow_rotation'],
                'j5': joint_positions['elbow2_rotation'],
                'j6': joint_positions['end_effector_rotation']
            }
        }
        return self.send_command(command)
    
    def send_jog_command(self, jog_data):
        """
        Send jog command for incremental movement of a specific joint
        
        Args:
            jog_data: Dictionary containing joint name and increment
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        # Map joint names to joint numbers
        joint_map = {
            'base_rotation': 'j1',
            'shoulder_rotation': 'j2',
            'prismatic_extension': 'j3',
            'elbow_rotation': 'j4',
            'elbow2_rotation': 'j5',
            'end_effector_rotation': 'j6'
        }
        
        joint_number = joint_map.get(jog_data['joint'])
        if not joint_number:
            print(f"Invalid joint name: {jog_data['joint']}")
            return False
            
        command = {
            'cmd': 'moveJoint',
            'joint': joint_number,
            'increment': jog_data['increment']
        }
        return self.send_command(command)
    
    def send_emergency_stop(self):
        """
        Send emergency stop command
        
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        command = {'cmd': 'estop'}
        return self.send_command(command)
