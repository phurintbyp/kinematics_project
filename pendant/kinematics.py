"""
we can set this file later when tata complete
"""
import numpy as np
from math import sin, cos, atan2, sqrt, pi
from config import ROBOT_DIMENSIONS, JOINT_LIMITS, ROBOT_CONFIG

class RobotParameters:
    """Robot physical parameters for the RRPRRR configuration"""
    def __init__(self):
        # Link lengths in mm from config
        self.base_height = ROBOT_DIMENSIONS['BASE_HEIGHT']
        self.link1_length = ROBOT_DIMENSIONS['LINK1_LENGTH']
        self.link2_min = ROBOT_DIMENSIONS['LINK2_MIN']
        self.link2_max = ROBOT_DIMENSIONS['LINK2_MAX']
        self.link3_length = ROBOT_DIMENSIONS['LINK3_LENGTH']
        self.link4_length = ROBOT_DIMENSIONS['LINK4_LENGTH']
        self.end_effector_length = ROBOT_DIMENSIONS['END_EFFECTOR_LENGTH']
        
        # Joint limits from config with both upper and lowercase keys for compatibility
        self.joint_limit_mapping = {
            'base_rotation': 'BASE_ROTATION',
            'shoulder_rotation': 'SHOULDER_ROTATION',
            'prismatic_extension': 'PRISMATIC_EXTENSION',
            'elbow_rotation': 'ELBOW_ROTATION',
            'elbow2_rotation': 'ELBOW2_ROTATION',
            'end_effector_rotation': 'END_EFFECTOR_ROTATION'
        }
        
        # Create a dictionary with lowercase keys for easier access
        self.joint_limits = {}
        for lowercase, uppercase in self.joint_limit_mapping.items():
            if uppercase in JOINT_LIMITS:
                self.joint_limits[lowercase] = JOINT_LIMITS[uppercase]
            else:
                # Fallback default limits if not found
                print(f"Warning: Joint limit not found for {uppercase}")
                self.joint_limits[lowercase] = (-180, 180)
        
        # Workspace limits
        self.workspace_limits = ROBOT_CONFIG.get('WORKSPACE_LIMITS', {
            'x': (-500, 500),
            'y': (-500, 500),
            'z': (0, 500),
            'roll': (-180, 180),
            'pitch': (-90, 90),
            'yaw': (-180, 180)
        })


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
                - elbow2_rotation (degrees)
                - end_effector_rotation (degrees)
                
        Returns:
            Dictionary with end effector position (x, y, z, roll, pitch, yaw)
        """
        # Convert joint angles from degrees to radians
        q1 = np.radians(joint_positions['base_rotation'])
        q2 = np.radians(joint_positions['shoulder_rotation'])
        d3 = joint_positions['prismatic_extension']  # Prismatic joint (mm)
        q4 = np.radians(joint_positions['elbow_rotation'])
        q5 = np.radians(joint_positions['elbow2_rotation'])
        q6 = np.radians(joint_positions['end_effector_rotation'])
        
        # Get robot parameters
        base_height = self.robot_params.base_height
        link1_length = self.robot_params.link1_length
        link3_length = self.robot_params.link3_length
        link4_length = self.robot_params.link4_length
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
        
        # Elbow2 rotation
        T45 = np.array([
            [cos(q5), -sin(q5), 0, link4_length * cos(q5)],
            [sin(q5), cos(q5), 0, link4_length * sin(q5)],
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
    
    def calculate_jacobian(self, joint_positions):
        """
        Calculate the Jacobian matrix at the current joint positions
        This is useful for velocity control in Cartesian space
        
        Args:
            joint_positions: Dictionary containing joint positions
       
        Returns:
            6x6 Jacobian matrix relating joint velocities to end effector velocities
        """
        # This is a simplified Jacobian calculation
        # For a real robot, you would use the analytical Jacobian
        
        # Small delta for numerical differentiation
        delta = 0.001
        
        # Current end effector position
        current_ee = self.calculate(joint_positions)
        
        # Initialize Jacobian matrix
        J = np.zeros((6, 6))
        
        # Joint names in order
        joints = ['base_rotation', 'shoulder_rotation', 'prismatic_extension', 
                 'elbow_rotation', 'elbow2_rotation', 'end_effector_rotation']
        
        # Calculate each column of the Jacobian
        for i, joint in enumerate(joints):
            # Make a copy of joint positions
            perturbed = joint_positions.copy()
            
            # Perturb the joint
            perturbed[joint] += delta
            
            # Calculate new end effector position
            new_ee = self.calculate(perturbed)
            
            # Calculate the partial derivatives
            J[0, i] = (new_ee['x'] - current_ee['x']) / delta
            J[1, i] = (new_ee['y'] - current_ee['y']) / delta
            J[2, i] = (new_ee['z'] - current_ee['z']) / delta
            J[3, i] = (new_ee['roll'] - current_ee['roll']) / delta
            J[4, i] = (new_ee['pitch'] - current_ee['pitch']) / delta
            J[5, i] = (new_ee['yaw'] - current_ee['yaw']) / delta
        
        return J


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
        link4_length = self.robot_params.link4_length
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
        
        # Calculate the distance from shoulder to end effector position
        shoulder_to_end = sqrt(xy_distance**2 + z_adjusted**2)
        
        # Calculate prismatic extension needed
        # Accounting for all links in the chain: link1, link3, link4, and end_effector
        d3 = shoulder_to_end - link1_length - link3_length - link4_length
        
        # Check if prismatic extension is within limits
        if d3 < link2_min or d3 > link2_max:
            return None  # No solution possible
        
        # For simplicity, we'll set elbow rotation to 0
        # In a more advanced implementation, these angles would be calculated
        # based on the specific robot configuration and target position
        q4 = 0
        
        # Calculate elbow2 rotation to achieve desired orientation
        # This is a simplified approach
        q5 = pitch
        
        # Calculate end effector rotation
        q6 = roll
        
        # Convert back to degrees
        joint_positions = {
            'base_rotation': np.degrees(q1),
            'shoulder_rotation': np.degrees(q2),
            'prismatic_extension': d3,
            'elbow_rotation': np.degrees(q4),
            'elbow2_rotation': np.degrees(q5),
            'end_effector_rotation': np.degrees(q6)
        }
        
        # Check joint limits
        for joint, value in joint_positions.items():
            limits = self.robot_params.joint_limits[joint]
            if value < limits[0] or value > limits[1]:
                return None  # Joint limit exceeded
        
        return joint_positions
    
    def calculate_differential(self, current_joints, target_ee, max_iterations=10, tolerance=0.001):
        """
        Calculate joint positions using differential inverse kinematics
        This is useful for smooth jogging in Cartesian space
        
        Args:
            current_joints: Dictionary with current joint positions
            target_ee: Dictionary with target end effector position
            max_iterations: Maximum number of iterations for convergence
            tolerance: Error tolerance for convergence
            
        Returns:
            Dictionary with new joint positions or None if no solution found
        """
        import sys  # For stdout.flush
        
        # Get the Jacobian calculator
        fk = self.fk
        
        # Current joint positions as a copy
        joints = current_joints.copy()
        
        # Joint names in order
        joint_names = ['base_rotation', 'shoulder_rotation', 'prismatic_extension', 
                      'elbow_rotation', 'elbow2_rotation', 'end_effector_rotation']
        
        print(f"Starting differential IK with joint positions: {joints}")
        print(f"Target end effector position: {target_ee}")
        sys.stdout.flush()
        
        # Convert joints to numpy array for calculations
        q = np.array([joints[j] for j in joint_names])
        
        # Iterate to find solution
        for i in range(max_iterations):
            # Current end effector position
            current_ee = fk.calculate(joints)
            
            # Calculate error
            error = np.array([
                target_ee['x'] - current_ee['x'],
                target_ee['y'] - current_ee['y'],
                target_ee['z'] - current_ee['z'],
                target_ee['roll'] - current_ee['roll'],
                target_ee['pitch'] - current_ee['pitch'],
                target_ee['yaw'] - current_ee['yaw']
            ])
            
            # Check convergence
            error_magnitude = np.linalg.norm(error)
            print(f"Iteration {i+1}, error magnitude: {error_magnitude}")
            sys.stdout.flush()
            
            if error_magnitude < tolerance:
                print(f"Converged after {i+1} iterations")
                print(f"Final joint positions: {joints}")
                sys.stdout.flush()
                return joints
            
            # Get Jacobian matrix
            J = fk.calculate_jacobian(joints)
            
            # Calculate pseudo-inverse of Jacobian
            J_inv = np.linalg.pinv(J)
            
            # Calculate joint increments
            dq = J_inv @ error
            
            # Update joint values
            q = q + dq
            
            # Update joints dictionary
            for j, name in enumerate(joint_names):
                old_value = joints[name]
                joints[name] = q[j]
                
                # Apply joint limits
                limits = self.robot_params.joint_limits[name]
                if joints[name] < limits[0]:
                    print(f"Joint {name} hit lower limit: {joints[name]} < {limits[0]}")
                    joints[name] = limits[0]
                elif joints[name] > limits[1]:
                    print(f"Joint {name} hit upper limit: {joints[name]} > {limits[1]}")
                    joints[name] = limits[1]
                
                print(f"Joint {name}: {old_value} -> {joints[name]}")
                sys.stdout.flush()
        
        # If we reach here, we didn't converge
        print(f"Failed to converge after {max_iterations} iterations")
        sys.stdout.flush()
        return None
