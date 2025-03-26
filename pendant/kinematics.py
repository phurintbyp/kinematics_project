import numpy as np
from math import sin, cos, atan2, sqrt, pi
from config import ROBOT_DIMENSIONS, JOINT_LIMITS

class RobotParameters:
    """Robot physical parameters for the RRPRRR configuration"""
    def __init__(self):
        # Link lengths in mm from config
        self.base_height = ROBOT_DIMENSIONS['BASE_HEIGHT']
        self.link1_length = ROBOT_DIMENSIONS['LINK1_LENGTH']
        self.link2_min = ROBOT_DIMENSIONS['LINK2_MIN']
        self.link2_max = ROBOT_DIMENSIONS['LINK2_MAX']
        self.link3_length = ROBOT_DIMENSIONS['LINK3_LENGTH']
        self.end_effector_length = ROBOT_DIMENSIONS['END_EFFECTOR_LENGTH']
        
        # Joint limits from config
        self.joint_limits = {
            'base_rotation': JOINT_LIMITS['BASE_ROTATION'],
            'shoulder_rotation': JOINT_LIMITS['SHOULDER_ROTATION'],
            'prismatic_extension': JOINT_LIMITS['PRISMATIC_EXTENSION'],
            'elbow_rotation': JOINT_LIMITS['ELBOW_ROTATION'],
            'wrist_rotation': JOINT_LIMITS['WRIST_ROTATION'],
            'end_effector_rotation': JOINT_LIMITS['END_EFFECTOR_ROTATION']
        }


class ForwardKinematics:
    """Forward kinematics calculator for RRPRRR robot"""
    def __init__(self):
        self.robot_params = RobotParameters()
    
    def calculate(self, joint_positions):
        """
        Calculate the end effector position based on joint angles
        
        Args:
            joint_positions: Dictionary containing joint positions
                - base_rotation (degrees)
                - shoulder_rotation (degrees)
                - prismatic_extension (mm)
                - elbow_rotation (degrees)
                - wrist_rotation (degrees)
                - end_effector_rotation (degrees)
                
        Returns:
            Dictionary with end effector position (x, y, z, roll, pitch, yaw)
        """
        # Convert joint angles from degrees to radians
        q1 = np.radians(joint_positions['base_rotation'])
        q2 = np.radians(joint_positions['shoulder_rotation'])
        d3 = joint_positions['prismatic_extension']  # Prismatic joint (mm)
        q4 = np.radians(joint_positions['elbow_rotation'])
        q5 = np.radians(joint_positions['wrist_rotation'])
        q6 = np.radians(joint_positions['end_effector_rotation'])
        
        # Get robot parameters
        base_height = self.robot_params.base_height
        link1_length = self.robot_params.link1_length
        link3_length = self.robot_params.link3_length
        end_effector_length = self.robot_params.end_effector_length
        
        # Calculate transformation matrices using DH parameters
        # Base to shoulder transformation
        T01 = np.array([
            [cos(q1), -sin(q1), 0, 0],
            [sin(q1), cos(q1), 0, 0],
            [0, 0, 1, base_height],
            [0, 0, 0, 1]
        ])
        
        # Shoulder to prismatic joint
        T12 = np.array([
            [cos(q2), -sin(q2), 0, link1_length * cos(q2)],
            [sin(q2), cos(q2), 0, link1_length * sin(q2)],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Prismatic joint extension
        T23 = np.array([
            [1, 0, 0, d3],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Elbow rotation
        T34 = np.array([
            [cos(q4), -sin(q4), 0, link3_length * cos(q4)],
            [sin(q4), cos(q4), 0, link3_length * sin(q4)],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Wrist rotation
        T45 = np.array([
            [cos(q5), -sin(q5), 0, 0],
            [sin(q5), cos(q5), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # End effector rotation
        T56 = np.array([
            [cos(q6), -sin(q6), 0, end_effector_length],
            [sin(q6), cos(q6), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Calculate the final transformation matrix
        T06 = T01 @ T12 @ T23 @ T34 @ T45 @ T56
        
        # Extract position and orientation
        position = T06[:3, 3]
        
        # Extract roll, pitch, yaw from rotation matrix
        rotation_matrix = T06[:3, :3]
        
        # Calculate roll, pitch, yaw (ZYX Euler angles)
        pitch = np.arcsin(-rotation_matrix[2, 0])
        
        if abs(cos(pitch)) > 1e-10:
            roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            # Gimbal lock case
            roll = 0
            yaw = np.arctan2(-rotation_matrix[0, 1], rotation_matrix[1, 1])
        
        return {
            'x': float(position[0]),
            'y': float(position[1]),
            'z': float(position[2]),
            'roll': float(np.degrees(roll)),
            'pitch': float(np.degrees(pitch)),
            'yaw': float(np.degrees(yaw))
        }


class InverseKinematics:
    """Inverse kinematics calculator for RRPRRR robot"""
    def __init__(self):
        self.robot_params = RobotParameters()
        self.fk = ForwardKinematics()
    
    def calculate(self, target_position):
        """
        Calculate joint positions to achieve the target end effector position
        
        Args:
            target_position: Dictionary with target position
                - x, y, z (mm)
                - roll, pitch, yaw (degrees)
                
        Returns:
            Dictionary with joint positions or None if no solution found
        """
        # Extract target position and orientation
        x = target_position['x']
        y = target_position['y']
        z = target_position['z']
        roll = np.radians(target_position['roll'])
        pitch = np.radians(target_position['pitch'])
        yaw = np.radians(target_position['yaw'])
        
        # Get robot parameters
        base_height = self.robot_params.base_height
        link1_length = self.robot_params.link1_length
        link2_min = self.robot_params.link2_min
        link2_max = self.robot_params.link2_max
        link3_length = self.robot_params.link3_length
        end_effector_length = self.robot_params.end_effector_length
        
        # Adjust z for base height
        z_adjusted = z - base_height
        
        # Calculate base rotation (q1)
        q1 = atan2(y, x)
        
        # Calculate distance from base to end effector in XY plane
        xy_distance = sqrt(x**2 + y**2)
        
        # Adjust for end effector length
        xy_distance -= end_effector_length
        
        # Calculate shoulder rotation (q2), prismatic extension (d3), and elbow rotation (q4)
        # This is a simplified approach - in a real system, you might need numerical methods
        # or more complex geometric calculations
        
        # Calculate shoulder angle using geometric approach
        shoulder_angle = atan2(z_adjusted, xy_distance)
        q2 = shoulder_angle
        
        # Calculate the distance from shoulder to wrist
        shoulder_to_wrist = sqrt(xy_distance**2 + z_adjusted**2)
        
        # Calculate prismatic extension needed
        d3 = shoulder_to_wrist - link1_length - link3_length
        
        # Check if prismatic extension is within limits
        if d3 < link2_min or d3 > link2_max:
            print(f"Prismatic joint extension {d3} is out of range [{link2_min}, {link2_max}]")
            return None
        
        # For simplicity, we'll set elbow rotation to 0
        q4 = 0.0
        
        # Set wrist rotation and end effector rotation based on target orientation
        # This is a simplified approach
        q5 = pitch
        q6 = roll
        
        # Create joint positions dictionary
        joint_positions = {
            'base_rotation': np.degrees(q1),
            'shoulder_rotation': np.degrees(q2),
            'prismatic_extension': d3,
            'elbow_rotation': np.degrees(q4),
            'wrist_rotation': np.degrees(q5),
            'end_effector_rotation': np.degrees(q6)
        }
        
        # Validate joint limits
        for joint, value in joint_positions.items():
            min_val, max_val = self.robot_params.joint_limits[joint]
            if value < min_val or value > max_val:
                print(f"Joint {joint} value {value} is out of range [{min_val}, {max_val}]")
                return None
        
        # Verify the solution with forward kinematics
        ee_pos = self.fk.calculate(joint_positions)
        error = sqrt((ee_pos['x'] - target_position['x'])**2 + 
                     (ee_pos['y'] - target_position['y'])**2 + 
                     (ee_pos['z'] - target_position['z'])**2)
        
        if error > 10.0:  # 10mm tolerance
            print(f"IK solution has high error: {error}mm")
            return None
        
        return joint_positions
