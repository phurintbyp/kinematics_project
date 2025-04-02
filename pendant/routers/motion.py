from fastapi import APIRouter, WebSocket, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
import asyncio
import copy
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import JOG_CONFIG, JOG_INCREMENTS, JOINT_LIMITS, ROBOT_CONFIG, SIMULATION_MODE
import kinematics

# Will be set by app.py
arduino_communicator = None

router = APIRouter(tags=["motion"])

fk = kinematics.ForwardKinematics()
ik = kinematics.InverseKinematics()

current_joint_positions = {
    'base_rotation': 0,
    'shoulder_rotation': 0,
    'prismatic_extension': 200,  # Start with some extension
    'elbow_rotation': 0,
    'elbow2_rotation': 0,
    'end_effector_rotation': 0
}

current_ee_position = fk.calculate(current_joint_positions)

jog_state = {
    'active': False,
    'mode': 'joint',  # 'joint' or 'cartesian'
    'joint': None,    # Active joint for joint mode
    'axis': None,     # Active axis for cartesian mode
    'direction': 0,   # -1, 0, or 1
    'velocity': 50,   # Percentage of max velocity (1-100)
    'target_velocity': 0,  # Calculated target velocity
    'last_update_time': 0  # Time of last position update
}

class JogCommand(BaseModel):
    mode: str
    velocity: Optional[int] = 50
    joint: Optional[str] = None
    axis: Optional[str] = None
    direction: int

class JogVelocity(BaseModel):
    velocity: int

class MoveJCommand(BaseModel):
    joint_positions: Dict[str, float]
    velocity: Optional[int] = 50

class MoveLCommand(BaseModel):
    position: Dict[str, float]
    velocity: Optional[int] = 50

class SavePositionRequest(BaseModel):
    name: str


def check_joint_limits(target_positions):
    """Check if target joint positions are within limits"""
    for joint, position in target_positions.items():
        # Map joint names to config joint limit keys
        joint_limit_mapping = {
            'base_rotation': 'BASE_ROTATION',
            'shoulder_rotation': 'SHOULDER_ROTATION',
            'prismatic_extension': 'PRISMATIC_EXTENSION',
            'elbow_rotation': 'ELBOW_ROTATION',
            'elbow2_rotation': 'ELBOW2_ROTATION',
            'end_effector_rotation': 'END_EFFECTOR_ROTATION'
        }
        
        if joint in joint_limit_mapping:
            limit_key = joint_limit_mapping[joint]
            
            if limit_key in JOINT_LIMITS:
                joint_limits = JOINT_LIMITS[limit_key]
                
                # Enforce joint limits
                if position < joint_limits[0] or position > joint_limits[1]:
                    return False, f"Joint {joint} position {position} exceeds limits {joint_limits}"
    
    return True, "All joint positions within limits"

def update_joint_position(joint, increment):
    """Update joint position with increment and enforce limits"""
    global current_joint_positions
    
    # Get current position
    current_position = current_joint_positions[joint]
    
    # Map joint names to config joint limit keys
    joint_limit_mapping = {
        'base_rotation': 'BASE_ROTATION',
        'shoulder_rotation': 'SHOULDER_ROTATION',
        'prismatic_extension': 'PRISMATIC_EXTENSION',
        'elbow_rotation': 'ELBOW_ROTATION',
        'elbow2_rotation': 'ELBOW2_ROTATION',
        'end_effector_rotation': 'END_EFFECTOR_ROTATION'
    }
    
    # Get joint limits using the mapping
    limit_key = joint_limit_mapping.get(joint, None)
    if limit_key and limit_key in JOINT_LIMITS:
        joint_limits = JOINT_LIMITS[limit_key]
    else:
        # Fallback to default limits
        print(f"Warning: No limits found for joint {joint}, using default limits")
        sys.stdout.flush()
        joint_limits = (-180, 180)
    
    # Calculate new position with limit enforcement
    new_position = current_position + increment
    new_position = max(joint_limits[0], min(joint_limits[1], new_position))
    
    # Update position
    current_joint_positions[joint] = new_position
    
    print(f"Updated joint {joint}: {current_position} -> {new_position} (limits: {joint_limits})")
    sys.stdout.flush()
    
    return new_position

def update_cartesian_position(axis, increment):
    """Update cartesian position with increment and enforce limits"""
    global current_joint_positions, current_ee_position
    
    # Create a copy of the current end effector position
    new_ee_position = current_ee_position.copy()
    
    # Apply the increment to the specified axis
    new_ee_position[axis] += increment
    
    # Check workspace limits
    workspace_limits = ROBOT_CONFIG.get('WORKSPACE_LIMITS', {
        'x': (-500, 500),
        'y': (-500, 500),
        'z': (0, 500),
        'roll': (-180, 180),
        'pitch': (-90, 90),
        'yaw': (-180, 180)
    })
    
    # Enforce workspace limits
    for ax, (min_val, max_val) in workspace_limits.items():
        if ax in new_ee_position:
            new_ee_position[ax] = max(min_val, min(max_val, new_ee_position[ax]))
    
    # Ensure all required cartesian parameters exist
    required_cartesian_params = ['x', 'y', 'z', 'roll', 'pitch', 'yaw']
    for param in required_cartesian_params:
        if param not in new_ee_position:
            # If missing, copy from current position or use default
            if param in current_ee_position:
                new_ee_position[param] = current_ee_position[param]
            else:
                # Default values
                defaults = {'x': 0, 'y': 0, 'z': 0, 'roll': 0, 'pitch': 0, 'yaw': 0}
                new_ee_position[param] = defaults[param]
                print(f"Warning: Missing required cartesian parameter '{param}', using default value {defaults[param]}")
                sys.stdout.flush()
    
    print(f"Attempting IK for target position: {new_ee_position}")
    sys.stdout.flush()
    
    try:
        # Calculate new joint positions using inverse kinematics
        new_joint_positions = ik.calculate_differential(
            current_joint_positions, 
            new_ee_position,
            max_iterations=10,
            tolerance=0.001
        )
        
        # Update positions if inverse kinematics found a solution
        if new_joint_positions:
            # Make a copy of the global variable to avoid reference issues
            global_copy = current_joint_positions.copy()
            
            # Update each joint position individually
            for joint, value in new_joint_positions.items():
                global_copy[joint] = value
            
            # Update the global variable with the copy
            current_joint_positions.update(global_copy)
            
            # Recalculate end effector position using forward kinematics to ensure consistency
            current_ee_position = fk.calculate(current_joint_positions)
            print(f"Updated cartesian position. New joint positions: {current_joint_positions}")
            print(f"New cartesian position: {current_ee_position}")
            sys.stdout.flush()
            return True
        else:
            # If no solution found, keep current positions
            print(f"No IK solution found for target position: {new_ee_position}")
            sys.stdout.flush()
            return False
    except Exception as e:
        print(f"Error during inverse kinematics calculation: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False

active_connections = []

async def broadcast_position_update():
    """Broadcast current positions to all connected clients"""
    message = {
        "type": "position_update",
        "timestamp": time.time(),
        "joint_positions": current_joint_positions,
        "ee_position": current_ee_position
    }
    
    print(f"Position update sent to {len(active_connections)} connection(s)")
    sys.stdout.flush()
    
    for i, connection in enumerate(active_connections):
        try:
            await connection.send_json(message)
            print(f"Position update sent to connection {i}")
            sys.stdout.flush()
        except:
            print(f"Failed to send position update to connection {i}")
            sys.stdout.flush()


async def jog_motion_control(background_tasks: BackgroundTasks):
    """Background task for continuous jogging motion"""
    global current_joint_positions, current_ee_position, jog_state
    
    print("Starting jog motion control background task")
    sys.stdout.flush()
    
    try:
        while jog_state['active']:
            # Calculate elapsed time since last update
            current_time = time.time()
            elapsed_time = current_time - jog_state['last_update_time']
            jog_state['last_update_time'] = current_time
            
            # Apply jogging based on mode
            if jog_state['mode'] == 'joint' and jog_state['joint']:
                # Joint jogging
                joint = jog_state['joint']
                
                # Apply jogging in joint space
                velocity = jog_state['target_velocity']  # degrees per second or mm per second
                increment = velocity * elapsed_time       # Calculate increment based on elapsed time
                
                if abs(increment) > 0.001:  # Only update if increment is significant
                    update_joint_position(joint, increment)
                    
                    # Update end effector position using forward kinematics
                    current_ee_position = fk.calculate(current_joint_positions)
                    
                    # Broadcast updated positions to all clients
                    await broadcast_position_update()
            
            elif jog_state['mode'] == 'cartesian' and jog_state['axis']:
                # Cartesian jogging
                axis = jog_state['axis']
                
                # Apply jogging in cartesian space
                velocity = jog_state['target_velocity']  # mm per second or degrees per second for orientation
                increment = velocity * elapsed_time       # Calculate increment based on elapsed time
                
                if abs(increment) > 0.001:  # Only update if increment is significant
                    # Update cartesian position (this will also update joint positions through IK)
                    position_updated = update_cartesian_position(axis, increment)
                    
                    if position_updated:
                        # Broadcast updated positions to all clients
                        await broadcast_position_update()
                    else:
                        print(f"Failed to update cartesian position for axis {axis}")
                        sys.stdout.flush()
            
            # Wait for next update
            await asyncio.sleep(JOG_CONFIG['UPDATE_INTERVAL'])
    
    except Exception as e:
        print(f"Error in jog motion control: {e}")
        sys.stdout.flush()
    
    finally:
        print("Jog motion control background task ended")
        sys.stdout.flush()
        jog_state['active'] = False

async def handle_jog_start(data):
    """Handle start of jogging motion"""
    global jog_state
    
    # Update jog state
    jog_state['active'] = True
    jog_state['mode'] = data.get('mode', 'joint')
    jog_state['direction'] = data.get('direction', 0)
    jog_state['velocity'] = data.get('velocity', 50)
    jog_state['last_update_time'] = time.time()
    
    # Set target velocity based on the mode
    # For joint mode
    if jog_state['mode'] == 'joint':
        jog_state['joint'] = data.get('joint')
        jog_state['axis'] = None
        
        # Get max velocity for this specific joint
        max_velocity = JOG_CONFIG['MAX_VELOCITY']['joint'].get(jog_state['joint'], 30)
        jog_state['target_velocity'] = (jog_state['direction'] * jog_state['velocity'] / 100.0) * max_velocity
        
    # For cartesian mode
    elif jog_state['mode'] == 'cartesian':
        jog_state['joint'] = None
        jog_state['axis'] = data.get('axis')
        
        # Get max velocity for this specific axis
        max_velocity = JOG_CONFIG['MAX_VELOCITY']['cartesian'].get(jog_state['axis'], 30)
        jog_state['target_velocity'] = (jog_state['direction'] * jog_state['velocity'] / 100.0) * max_velocity
    
    print(f"Starting jogging: mode={jog_state['mode']}, "
          f"{'joint=' + jog_state['joint'] if jog_state['joint'] else 'axis=' + jog_state['axis']}, "
          f"direction={jog_state['direction']}, velocity={jog_state['velocity']}%, "
          f"target_velocity={jog_state['target_velocity']}")
    sys.stdout.flush()

async def handle_jog_stop():
    """Handle stop of jogging motion"""
    global jog_state
    
    # Update jog state
    jog_state['active'] = False
    jog_state['direction'] = 0
    jog_state['target_velocity'] = 0
    
    print("Stopping jogging")
    sys.stdout.flush()
    
    # Send jog stop message to all clients
    message = {
        "type": "jog_stop",
        "timestamp": time.time()
    }
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

async def handle_jog_velocity(data):
    """Handle change of jogging velocity"""
    global jog_state
    
    velocity = data.get('velocity', 50)
    jog_state['velocity'] = max(1, min(100, velocity))
    
    # Update target velocity based on the mode
    if jog_state['mode'] == 'joint' and jog_state['joint']:
        # Get max velocity for this specific joint
        max_velocity = JOG_CONFIG['MAX_VELOCITY']['joint'].get(jog_state['joint'], 30)
        jog_state['target_velocity'] = (jog_state['direction'] * jog_state['velocity'] / 100.0) * max_velocity
    elif jog_state['mode'] == 'cartesian' and jog_state['axis']:
        # Get max velocity for this specific axis
        max_velocity = JOG_CONFIG['MAX_VELOCITY']['cartesian'].get(jog_state['axis'], 30)
        jog_state['target_velocity'] = (jog_state['direction'] * jog_state['velocity'] / 100.0) * max_velocity
    
    print(f"Changing jogging velocity to {jog_state['velocity']}%, target_velocity: {jog_state['target_velocity']}")
    sys.stdout.flush()

async def handle_jog_increment(data):
    """Handle a discrete jogging increment"""
    global current_joint_positions, current_ee_position
    
    mode = data.get('mode', 'joint')
    increment_size = data.get('increment', 5)  # Default 5 units (degrees or mm)
    direction = data.get('direction', 0)
    
    print(f"Received jog increment: mode={mode}, increment={increment_size}, direction={direction}")
    sys.stdout.flush()
    
    # Validate increment size against config
    # If the increment is not one of our standard increments, find the closest one
    standard_increments = [inc for inc_name, inc in JOG_INCREMENTS[mode].items()]
    if increment_size not in standard_increments:
        # Find the closest standard increment
        closest_increment = min(standard_increments, key=lambda x: abs(x - increment_size))
        print(f"Non-standard increment {increment_size} received, using closest standard increment {closest_increment}")
        increment_size = closest_increment
    
    # Calculate the actual increment based on direction
    actual_increment = increment_size * direction
    position_updated = False
    
    if mode == 'joint':
        joint = data.get('joint')
        if joint in current_joint_positions:
            # Update joint position
            old_position = current_joint_positions[joint]
            update_joint_position(joint, actual_increment)
            new_position = current_joint_positions[joint]
            
            # Update end effector position
            current_ee_position = fk.calculate(current_joint_positions)
            position_updated = True
            
            print(f"Jogged joint {joint} by {actual_increment} degrees: {old_position} -> {new_position}")
            sys.stdout.flush()
            
            # Send command to Arduino if connected and not in simulation mode
            if arduino_communicator and not SIMULATION_MODE:
                success = arduino_communicator.send_joint_command(current_joint_positions)
                if success:
                    print(f"Jog command sent to Arduino: {current_joint_positions}")
                else:
                    print("Failed to send jog command to Arduino")
                sys.stdout.flush()
            
    elif mode == 'cartesian':
        axis = data.get('axis')
        if axis in current_ee_position:
            # Update cartesian position
            old_position = current_ee_position[axis]
            position_updated = update_cartesian_position(axis, actual_increment)
            
            if position_updated:
                new_position = current_ee_position[axis]
                print(f"Jogged axis {axis} by {actual_increment} {'mm' if axis in ['x', 'y', 'z'] else 'degrees'}: {old_position} -> {new_position}")
                sys.stdout.flush()
                
                # Send command to Arduino if connected and not in simulation mode
                if arduino_communicator and not SIMULATION_MODE:
                    success = arduino_communicator.send_cartesian_command(current_ee_position)
                    if success:
                        print(f"Jog command sent to Arduino: {current_ee_position}")
                    else:
                        print("Failed to send jog command to Arduino")
                    sys.stdout.flush()
    
    # Broadcast updated positions if changed
    if position_updated:
        # Send command to Arduino if connected and not in simulation mode
        if arduino_communicator and not SIMULATION_MODE:
            if mode == 'joint':
                arduino_communicator.send_joint_command(current_joint_positions)
            else:  # cartesian mode requires inverse kinematics which is already calculated
                arduino_communicator.send_joint_command(current_joint_positions)
            print(f"Joint command sent to Arduino: {current_joint_positions}")
            sys.stdout.flush()
        
        await broadcast_position_update()


async def handle_moveJ(data):
    """Handle moveJ command (joint space motion)"""
    global current_joint_positions, current_ee_position
    
    target_positions = data.get('joint_positions', {})
    velocity_percentage = data.get('velocity', 50)
    
    print(f"Received moveJ command to positions: {target_positions}, velocity: {velocity_percentage}%")
    sys.stdout.flush()
    
    # Check if all required joints are present
    for joint in current_joint_positions.keys():
        if joint not in target_positions:
            print(f"Missing joint {joint} in moveJ command")
            sys.stdout.flush()
            return False
    
    # Check joint limits
    valid, message = check_joint_limits(target_positions)
    if not valid:
        print(f"Joint limits check failed: {message}")
        sys.stdout.flush()
        return False
    
    # TODO: Implement trajectory planning for smooth motion
    # For now, just update positions directly (this is not how a real robot would move)
    current_joint_positions.update(target_positions)
    
    # Update end effector position
    current_ee_position = fk.calculate(current_joint_positions)
    
    # Send command to Arduino if connected and not in simulation mode
    if arduino_communicator and not SIMULATION_MODE:
        success = arduino_communicator.send_joint_command(current_joint_positions)
        if success:
            print(f"MoveJ command sent to Arduino: {current_joint_positions}")
        else:
            print("Failed to send moveJ command to Arduino")
        sys.stdout.flush()
    
    # Broadcast updated positions
    await broadcast_position_update()
    
    print(f"Completed moveJ to: {target_positions}")
    sys.stdout.flush()
    return True

async def handle_moveL(data):
    """Handle moveL command (linear Cartesian motion)"""
    global current_joint_positions, current_ee_position
    
    target_position = data.get('position', {})
    velocity_percentage = data.get('velocity', 50)
    
    print(f"Received moveL command to position: {target_position}, velocity: {velocity_percentage}%")
    sys.stdout.flush()
    
    # Check if all required cartesian coordinates are present
    required_coords = ['x', 'y', 'z']
    for coord in required_coords:
        if coord not in target_position:
            print(f"Missing coordinate {coord} in moveL command")
            sys.stdout.flush()
            return False
    
    # Create full target position (including orientation)
    full_target = current_ee_position.copy()
    for coord, value in target_position.items():
        full_target[coord] = value
    
    # Check workspace limits
    workspace_limits = ROBOT_CONFIG.get('WORKSPACE_LIMITS', {})
    for coord, (min_val, max_val) in workspace_limits.items():
        if coord in full_target and (full_target[coord] < min_val or full_target[coord] > max_val):
            print(f"Target position exceeds workspace limits for {coord}: {full_target[coord]} not in {min_val} to {max_val}")
            sys.stdout.flush()
            return False
    
    # Calculate inverse kinematics
    target_joint_positions = ik.calculate(full_target)
    
    if not target_joint_positions:
        print(f"No IK solution found for target position: {full_target}")
        sys.stdout.flush()
        return False
    
    # Check joint limits
    valid, message = check_joint_limits(target_joint_positions)
    if not valid:
        print(f"Joint limits check failed: {message}")
        sys.stdout.flush()
        return False
    
    # TODO: Implement linear trajectory planning
    # For now, just update positions directly (this is not a true linear motion)
    current_joint_positions.update(target_joint_positions)
    current_ee_position = full_target
    
    # Send command to Arduino if connected and not in simulation mode
    if arduino_communicator and not SIMULATION_MODE:
        success = arduino_communicator.send_joint_command(current_joint_positions)
        if success:
            print(f"MoveL command sent to Arduino: {current_joint_positions}")
        else:
            print("Failed to send moveL command to Arduino")
        sys.stdout.flush()
    
    # Broadcast updated positions
    await broadcast_position_update()
    
    print(f"Completed moveL to: {full_target}")
    sys.stdout.flush()
    return True

async def handle_emergency_stop():
    """Handle emergency stop"""
    global jog_state
    
    print("EMERGENCY STOP ACTIVATED")
    sys.stdout.flush()
    
    # Stop any active jogging
    jog_state['active'] = False
    jog_state['direction'] = 0
    jog_state['target_velocity'] = 0

    # Send emergency stop message to all clients
    message = {
        "type": "emergency_stop",
        "timestamp": time.time()
    }
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass
    
    return True


@router.get("/joint_positions")
def get_joint_positions():
    """Get current joint positions"""
    return current_joint_positions

@router.get("/ee_position")
def get_ee_position():
    """Get current end effector position"""
    return current_ee_position

@router.post("/jog_start")
async def api_jog_start(command: JogCommand, background_tasks: BackgroundTasks):
    """Start jogging motion"""
    await handle_jog_start(command.dict())
    
    # Start background task if not already running
    if jog_state['active']:
        background_tasks.add_task(jog_motion_control, background_tasks)
    
    return {"success": True}

@router.post("/jog_stop")
async def api_jog_stop():
    """Stop jogging motion"""
    await handle_jog_stop()
    return {"success": True}

@router.post("/jog_velocity")
async def api_jog_velocity(command: JogVelocity):
    """Change jogging velocity"""
    await handle_jog_velocity(command.dict())
    return {"success": True}

@router.post("/emergency_stop")
async def api_emergency_stop():
    """Emergency stop"""
    await handle_emergency_stop()
    return {"success": True}

@router.post("/moveJ")
async def api_moveJ(command: MoveJCommand):
    """Execute a moveJ command"""
    success = await handle_moveJ(command.dict())
    return {"success": success}

@router.post("/moveL")
async def api_moveL(command: MoveLCommand):
    """Execute a moveL command"""
    success = await handle_moveL(command.dict())
    return {"success": success}
