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
        
    def connect(self):
        """
        Establish connection with the Arduino
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            
            # Wait for Arduino to reset after connection
            time.sleep(2)
            
            # Send a test command and wait for response
            self.serial.write(b'PING\n')
            response = self.serial.readline().decode('utf-8').strip()
            
            if response == 'PONG':
                self.connected = True
                print(f"Successfully connected to Arduino on {self.port}")
                return True
            else:
                print(f"Connected to port {self.port}, but received unexpected response: {response}")
                self.serial.close()
                self.serial = None
                return False
                
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.serial = None
            return False
    
    def disconnect(self):
        """Disconnect from the Arduino"""
        if self.serial:
            self.serial.close()
            self.serial = None
            self.connected = False
            print("Disconnected from Arduino")
    
    def is_connected(self):
        """Check if connected to Arduino"""
        return self.connected and self.serial is not None
    
    def send_command(self, command):
        """
        Send a command to the Arduino
        
        Args:
            command (str): Command string to send
            
        Returns:
            str: Response from Arduino or None if error
        """
        if not self.is_connected():
            print("Not connected to Arduino")
            return None
        
        try:
            with self.lock:
                # Send the command with newline termination
                self.serial.write(f"{command}\n".encode('utf-8'))
                
                # Wait for and read the response
                response = self.serial.readline().decode('utf-8').strip()
                return response
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
            return None
    
    def send_joint_command(self, joint_positions):
        """
        Send joint positions to the Arduino
        
        Args:
            joint_positions (dict): Dictionary of joint positions
            
        Returns:
            bool: True if command was sent successfully
        """
        # Format the joint positions as a JSON string
        command = "MOVE " + json.dumps(joint_positions)
        
        response = self.send_command(command)
        
        if response == "OK":
            return True
        else:
            print(f"Error sending joint command. Response: {response}")
            return False
    
    def send_emergency_stop(self):
        """
        Send emergency stop command to Arduino
        
        Returns:
            bool: True if command was sent successfully
        """
        response = self.send_command("ESTOP")
        
        if response == "STOPPED":
            return True
        else:
            print(f"Error sending emergency stop. Response: {response}")
            return False
    
    def get_status(self):
        """
        Get the current status from the Arduino
        
        Returns:
            dict: Status information or None if error
        """
        response = self.send_command("STATUS")
        
        if response:
            try:
                status = json.loads(response)
                return status
            except json.JSONDecodeError:
                print(f"Error parsing status response: {response}")
                return None
        else:
            return None
