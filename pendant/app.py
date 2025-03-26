from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import json
import time
from kinematics import ForwardKinematics, InverseKinematics
from arduino_communication import ArduinoCommunicator
import uuid
import datetime
import copy
from config import (
    FLASK_CONFIG, 
    SIMULATION_MODE, 
    ARDUINO_CONFIG, 
    DEFAULT_JOINT_POSITIONS, 
    JOG_INCREMENTS
)

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_CONFIG['SECRET_KEY']
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
# SIMULATION_MODE = True  # Set to False to enable actual Arduino communication

# Initialize the Arduino communicator (only if not in simulation mode)
arduino_comm = None
if not SIMULATION_MODE:
    arduino_comm = ArduinoCommunicator()  # Will use values from config

# Initialize kinematics calculators
fk = ForwardKinematics()
ik = InverseKinematics()

# Global variables
current_joint_positions = copy.deepcopy(DEFAULT_JOINT_POSITIONS)

current_ee_position = {
    'x': 0.0,  # mm
    'y': 0.0,  # mm
    'z': 0.0,  # mm
    'roll': 0.0,  # degrees
    'pitch': 0.0,  # degrees
    'yaw': 0.0  # degrees
}

# Store saved positions and programs
saved_positions = {}
program_sequences = {}
current_program = None
program_running = False

@app.route('/')
def index():
    """Render the main control interface"""
    return render_template('index.html')

@app.route('/api/joint_positions', methods=['GET'])
def get_joint_positions():
    return jsonify(current_joint_positions)

@app.route('/api/ee_position', methods=['GET'])
def get_ee_position():
    return jsonify(current_ee_position)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial positions to the client
    socketio.emit('joint_positions_update', current_joint_positions)
    socketio.emit('ee_position_update', current_ee_position)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def send_to_arduino(command_type, data):
    """
    Send commands to Arduino if not in simulation mode
    
    Args:
        command_type: Type of command (joint, emergency_stop, etc.)
        data: Data to send
        
    Returns:
        bool: True if successful or in simulation mode
    """
    if SIMULATION_MODE:
        print(f"SIMULATION: {command_type} command with data: {data}")
        return True
    
    if arduino_comm is None:
        print("Arduino communicator not initialized")
        return False
    
    if command_type == 'joint':
        return arduino_comm.send_joint_command(data)
    elif command_type == 'emergency_stop':
        return arduino_comm.send_emergency_stop()
    else:
        print(f"Unknown command type: {command_type}")
        return False

@socketio.on('moveJ')
def handle_moveJ(data):
    """Handle joint movement commands"""
    print(f"MoveJ command received: {data}")
    
    # Update the current joint positions
    for joint, value in data.items():
        if joint in current_joint_positions:
            current_joint_positions[joint] = float(value)
    
    # Calculate the new end effector position using forward kinematics
    ee_pos = fk.calculate(current_joint_positions)
    current_ee_position.update(ee_pos)
    
    # Send the command to the Arduino (if not in simulation mode)
    send_to_arduino('joint', current_joint_positions)
    
    # Broadcast the updated positions to all clients
    socketio.emit('joint_positions_update', current_joint_positions)
    socketio.emit('ee_position_update', current_ee_position)
    
    return jsonify({"status": "success"})

@socketio.on('moveL')
def handle_moveL(data):
    """Handle linear movement commands in Cartesian space"""
    print(f"MoveL command received: {data}")
    
    # Update the target end effector position
    target_position = current_ee_position.copy()
    for axis, value in data.items():
        if axis in target_position:
            target_position[axis] = float(value)
    
    # Calculate joint positions using inverse kinematics
    joint_positions = ik.calculate(target_position)
    
    if joint_positions:  # If a valid solution was found
        current_joint_positions.update(joint_positions)
        current_ee_position.update(target_position)
        
        # Send the command to the Arduino (if not in simulation mode)
        send_to_arduino('joint', current_joint_positions)
        
        # Broadcast the updated positions to all clients
        socketio.emit('joint_positions_update', current_joint_positions)
        socketio.emit('ee_position_update', current_ee_position)
        
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "No valid inverse kinematics solution found"})

@socketio.on('jog')
def handle_jog(data):
    """Handle incremental jogging commands"""
    print(f"Jog command received: {data}")
    
    joint_name = data.get('joint')
    increment = float(data.get('increment', 0))
    
    if joint_name in current_joint_positions:
        # Update the joint position with the increment
        current_joint_positions[joint_name] += increment
        
        # Calculate the new end effector position
        ee_pos = fk.calculate(current_joint_positions)
        current_ee_position.update(ee_pos)
        
        # Send the command to the Arduino (if not in simulation mode)
        send_to_arduino('joint', current_joint_positions)
        
        # Broadcast the updated positions
        socketio.emit('joint_positions_update', current_joint_positions)
        socketio.emit('ee_position_update', current_ee_position)
        
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": f"Unknown joint: {joint_name}"})

@socketio.on('emergency_stop')
def handle_emergency_stop():
    """Handle emergency stop command"""
    print("Emergency stop triggered")
    send_to_arduino('emergency_stop', None)
    return jsonify({"status": "success", "message": "Emergency stop triggered"})

@app.route('/api/moveJ', methods=['POST'])
def api_moveJ():
    """REST API endpoint for joint movement commands"""
    data = request.json
    print(f"MoveJ API command received: {data}")
    
    # Update the current joint positions
    for joint, value in data.items():
        if joint in current_joint_positions:
            current_joint_positions[joint] = float(value)
    
    # Calculate the new end effector position using forward kinematics
    ee_pos = fk.calculate(current_joint_positions)
    current_ee_position.update(ee_pos)
    
    # Send the command to the Arduino (if not in simulation mode)
    send_to_arduino('joint', current_joint_positions)
    
    # Broadcast the updated positions to all clients
    socketio.emit('joint_positions_update', current_joint_positions)
    socketio.emit('ee_position_update', current_ee_position)
    
    return jsonify({"status": "success"})

@app.route('/api/emergency_stop', methods=['POST'])
def api_emergency_stop():
    """REST API endpoint for emergency stop"""
    print("Emergency stop API triggered")
    send_to_arduino('emergency_stop', None)
    return jsonify({"status": "success", "message": "Emergency stop triggered"})

@app.route('/api/save_position', methods=['POST'])
def save_position():
    """Save the current position with a name"""
    data = request.json
    position_name = data.get('name')
    
    if not position_name:
        return jsonify({"status": "error", "message": "Position name is required"}), 400
    
    # Create a new position entry
    position_data = {
        'id': str(uuid.uuid4()),
        'name': position_name,
        'timestamp': datetime.datetime.now().isoformat(),
        'joint_positions': copy.deepcopy(current_joint_positions),
        'ee_position': copy.deepcopy(current_ee_position)
    }
    
    # Save the position
    saved_positions[position_data['id']] = position_data
    
    # Broadcast the updated saved positions list to all clients
    socketio.emit('saved_positions_update', list(saved_positions.values()))
    
    return jsonify({"status": "success", "position": position_data})

@app.route('/api/get_saved_positions', methods=['GET'])
def get_saved_positions():
    """Get all saved positions"""
    return jsonify({"status": "success", "positions": list(saved_positions.values())})

@app.route('/api/delete_position/<position_id>', methods=['DELETE'])
def delete_position(position_id):
    """Delete a saved position"""
    if position_id in saved_positions:
        del saved_positions[position_id]
        socketio.emit('saved_positions_update', list(saved_positions.values()))
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Position not found"}), 404

@app.route('/api/create_program', methods=['POST'])
def create_program():
    """Create a new program sequence"""
    data = request.json
    program_name = data.get('name')
    position_ids = data.get('position_ids', [])
    settings = data.get('settings', {})
    
    if not program_name:
        return jsonify({"status": "error", "message": "Program name is required"}), 400
    
    # Create a new program entry
    program_data = {
        'id': str(uuid.uuid4()),
        'name': program_name,
        'timestamp': datetime.datetime.now().isoformat(),
        'position_ids': position_ids,
        'settings': settings
    }
    
    # Save the program
    program_sequences[program_data['id']] = program_data
    
    # Broadcast the updated program list to all clients
    socketio.emit('program_sequences_update', list(program_sequences.values()))
    
    return jsonify({"status": "success", "program": program_data})

@app.route('/api/get_programs', methods=['GET'])
def get_programs():
    """Get all saved programs"""
    return jsonify({"status": "success", "programs": list(program_sequences.values())})

@app.route('/api/delete_program/<program_id>', methods=['DELETE'])
def delete_program(program_id):
    """Delete a saved program"""
    if program_id in program_sequences:
        del program_sequences[program_id]
        socketio.emit('program_sequences_update', list(program_sequences.values()))
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Program not found"}), 404

@app.route('/api/run_program/<program_id>', methods=['POST'])
def run_program(program_id):
    """Start running a program"""
    global current_program, program_running
    
    if program_id not in program_sequences:
        return jsonify({"status": "error", "message": "Program not found"}), 404
    
    if program_running:
        return jsonify({"status": "error", "message": "Another program is already running"}), 400
    
    # Set the current program and start running it
    current_program = program_sequences[program_id]
    program_running = True
    
    # Start the program execution in a background thread
    socketio.start_background_task(execute_program, current_program)
    
    return jsonify({"status": "success", "message": "Program started"})

@app.route('/api/stop_program', methods=['POST'])
def stop_program():
    """Stop the currently running program"""
    global program_running
    
    if not program_running:
        return jsonify({"status": "error", "message": "No program is currently running"}), 400
    
    # Stop the program
    program_running = False
    socketio.emit('program_status', {"status": "stopped"})
    
    return jsonify({"status": "success", "message": "Program stopped"})

def execute_program(program):
    """Execute a program sequence"""
    global program_running
    
    try:
        # Notify clients that the program is starting
        socketio.emit('program_status', {"status": "running", "program_id": program['id']})
        
        # Get the program settings
        settings = program.get('settings', {})
        speed_factor = get_speed_factor(settings.get('speed', 'medium'))
        repeat_count = int(settings.get('repeat_count', 1))
        
        # Run the program for the specified number of repeats
        for repeat in range(repeat_count):
            if not program_running:
                break
                
            # Notify clients about the current repeat
            socketio.emit('program_status', {
                "status": "running", 
                "program_id": program['id'],
                "current_repeat": repeat + 1,
                "total_repeats": repeat_count
            })
            
            # Execute each position in the sequence
            for idx, position_id in enumerate(program['position_ids']):
                if not program_running:
                    break
                    
                if position_id in saved_positions:
                    position = saved_positions[position_id]
                    
                    # Notify clients about the current position
                    socketio.emit('program_status', {
                        "status": "running", 
                        "program_id": program['id'],
                        "current_repeat": repeat + 1,
                        "total_repeats": repeat_count,
                        "current_position": idx + 1,
                        "total_positions": len(program['position_ids']),
                        "position_name": position['name']
                    })
                    
                    # Move to the position
                    move_to_position(position, speed_factor)
                    
                    # Wait a short time between positions
                    time.sleep(0.5)
        
        # Notify clients that the program has completed
        if program_running:
            socketio.emit('program_status', {"status": "completed", "program_id": program['id']})
    
    except Exception as e:
        print(f"Error executing program: {e}")
        socketio.emit('program_status', {"status": "error", "message": str(e)})
    
    finally:
        # Reset the program running flag
        program_running = False

def move_to_position(position, speed_factor=1.0):
    """Move to a saved position"""
    # Get the joint positions from the saved position
    target_joint_positions = position['joint_positions']
    
    # Update the current joint positions
    for joint, value in target_joint_positions.items():
        if joint in current_joint_positions:
            current_joint_positions[joint] = float(value)
    
    # Calculate the new end effector position using forward kinematics
    ee_pos = fk.calculate(current_joint_positions)
    current_ee_position.update(ee_pos)
    
    # Send the command to the Arduino if not in simulation mode
    if not SIMULATION_MODE:
        arduino_comm.send_joint_command(current_joint_positions)
    
    # Broadcast the updated positions to all clients
    socketio.emit('joint_positions_update', current_joint_positions)
    socketio.emit('ee_position_update', current_ee_position)
    
    # Simulate movement time based on speed factor
    time.sleep(1.0 / speed_factor)

def get_speed_factor(speed):
    """Convert speed setting to a numeric factor"""
    speed_factors = {
        'slow': 0.5,
        'medium': 1.0,
        'fast': 2.0
    }
    return speed_factors.get(speed, 1.0)

if __name__ == '__main__':
    import os
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Try to connect to the Arduino if not in simulation mode
    if not SIMULATION_MODE and arduino_comm is not None:
        connected = arduino_comm.connect()
        if not connected:
            print("Warning: Could not connect to Arduino. Running in simulation mode.")
            SIMULATION_MODE = True
    else:
        print("Running in simulation mode - no Arduino communication")
    
    # Start the Flask-SocketIO server
    socketio.run(
        app, 
        host=FLASK_CONFIG['HOST'], 
        port=FLASK_CONFIG['PORT'], 
        debug=FLASK_CONFIG['DEBUG']
    )
