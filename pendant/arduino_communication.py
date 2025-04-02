import serial
import time
import json
import threading
import asyncio
from config import ARDUINO_CONFIG
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routers import motion

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
                    response_dict = self.process_response(response)
                    if response_dict and response_dict.get('status') == 'ok':
                        return True
                    else:
                        print(f"Arduino error: {response_dict.get('message', 'Unknown error')}")
                        return False
                else:
                    print("No response from Arduino")
                    return False
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
            return False
    
    def process_response(self, response):
        """Process a response from the Arduino"""
        try:
            if isinstance(response, str):
                print(f"Raw response from Arduino: {response}")
                sys.stdout.flush()
                
                response_data = json.loads(response)
                print(f"Parsed JSON from Arduino: {response_data}")
                sys.stdout.flush()
                
                # Check if this is a move completion notification
                if response_data.get('status') == 'move_done':
                    print("MOVE DONE signal detected from Arduino!")
                    sys.stdout.flush()
                    # Notify the websocket clients
                    self.broadcast_move_done(response_data)
                
                return response_data
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON response from Arduino: {response}")
            sys.stdout.flush()
            return None
    
    def broadcast_move_done(self, data):
        """Broadcast move done to websocket clients"""
        # The message will be picked up by the WebSocket handler in app.py
        # and routed to motion.handle_move_done
        for connection in motion.active_connections:
            asyncio.create_task(connection.send_json({
                'type': 'move_done',
                'data': data,
                'timestamp': time.time()
            }))
    
    def send_joint_command(self, joint_positions):
        """
        Send joint movement command with specific position for each joint
        
        Args:
            joint_positions: Dictionary of joint positions (degrees for all joints)
            
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
                'j3': joint_positions['prismatic_extension'],  # Already converted in motion.py
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
            
        # Increment is already converted in motion.py if needed
        command = {
            'cmd': 'moveJoint',
            'joint': joint_number,
            'increment': jog_data['increment']
        }
        return self.send_command(command)
    
    def send_home_command(self):
        """
        Send home command to Arduino and wait for completion
        
        Returns:
            bool: True if homing completed successfully, False otherwise
        """
        if not self.connected or not self.serial:
            print("Not connected to Arduino")
            return False
        
        try:
            with self.lock:  # Ensure thread safety for serial communication
                # Send home command
                command = {'cmd': 'home'}
                command_json = json.dumps(command) + '\n'
                self.serial.write(command_json.encode())
                self.serial.flush()
                
                print("Home command sent to Arduino, waiting for completion...")
                
                # Wait for initial acknowledgment
                response = self.serial.readline().decode().strip()
                if not response:
                    print("No initial response from Arduino")
                    return False
                
                try:
                    response_dict = self.process_response(response)
                    if response_dict and response_dict.get('status') != 'ok':
                        print(f"Arduino error: {response_dict.get('message', 'Unknown error')}")
                        return False
                    
                    print("Arduino acknowledged home command, waiting for completion...")
                    
                    # Now wait for the home completion message
                    # This could take some time as the Arduino performs the homing sequence
                    while True:
                        completion_response = self.serial.readline().decode().strip()
                        if not completion_response:
                            # If we timeout waiting for a response
                            time.sleep(0.5)  # Small delay before trying again
                            continue
                        
                        try:
                            completion_dict = self.process_response(completion_response)
                            if completion_dict and completion_dict.get('status') == 'home_done':
                                print("Homing completed successfully")
                                return True
                            elif completion_dict and completion_dict.get('status') == 'error':
                                print(f"Homing error: {completion_dict.get('message', 'Unknown error')}")
                                return False
                        except json.JSONDecodeError:
                            print(f"Invalid completion response from Arduino: {completion_response}")
                            continue
                        
                except json.JSONDecodeError:
                    print(f"Invalid response from Arduino: {response}")
                    return False
                
        except Exception as e:
            print(f"Error during homing: {e}")
            return False

    def send_emergency_stop(self):
        """
        Send emergency stop command
        
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        command = {'cmd': 'estop'}
        return self.send_command(command)
