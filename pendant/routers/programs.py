from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any
import asyncio
import copy
import json
import time
import sys
import uuid
import datetime
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ROBOT_CONFIG
import kinematics

router = APIRouter(tags=["programs"])

import routers.motion as motion

saved_positions = {}

programs = {}

class SavePositionRequest(BaseModel):
    name: str

class ProgramStep(BaseModel):
    type: str  # 'moveJ', 'moveL', 'wait', 'io'
    data: Dict[str, Any]

class Program(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    steps: List[ProgramStep]
    created: str
    modified: str

class CreateProgramRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class UpdateProgramRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[ProgramStep]] = None


def save_data_to_file(filename, data):
    """Save data to a JSON file"""
    try:

        os.makedirs("data", exist_ok=True)
        

        filepath = os.path.join("data", filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filepath}")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"Error saving data to file {filename}: {e}")
        sys.stdout.flush()
        return False

def load_data_from_file(filename, default=None):
    """Load data from a JSON file"""
    try:
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"Data loaded from {filepath}")
            sys.stdout.flush()
            return data
        else:
            print(f"File {filepath} not found, returning default value")
            sys.stdout.flush()
            return default if default is not None else {}
    except Exception as e:
        print(f"Error loading data from file {filename}: {e}")
        sys.stdout.flush()
        return default if default is not None else {}

# Program execution
async def execute_program(program_id, background_tasks: BackgroundTasks):
    """Execute a program by ID"""
    if program_id not in programs:
        print(f"Program {program_id} not found")
        sys.stdout.flush()
        return False
    
    program = programs[program_id]
    print(f"Executing program: {program['name']}")
    sys.stdout.flush()
    
    # Send program start notification
    message = {
        "type": "program_execution",
        "status": "started",
        "program_id": program_id,
        "timestamp": time.time()
    }
    for connection in motion.active_connections:
        try:
            await connection.send_json(message)
        except:
            pass
    
    # Execute each step
    step_index = 0
    for step in program["steps"]:
        step_index += 1
        step_type = step["type"]
        step_data = step["data"]
        
        # Send step start notification
        message = {
            "type": "program_execution",
            "status": "step_started",
            "program_id": program_id,
            "step_index": step_index,
            "step_type": step_type,
            "timestamp": time.time()
        }
        for connection in motion.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
        
        # Execute step based on type
        success = False
        if step_type == "moveJ":
            success = await motion.handle_moveJ(step_data)
        elif step_type == "moveL":
            success = await motion.handle_moveL(step_data)
        elif step_type == "wait":
            # Wait for specified time in seconds
            wait_time = step_data.get("time", 1)
            print(f"Waiting for {wait_time} seconds")
            sys.stdout.flush()
            await asyncio.sleep(wait_time)
            success = True
        elif step_type == "io":
            # Handle I/O operations (placeholder for future implementation)
            io_action = step_data.get("action", "")
            io_pin = step_data.get("pin", 0)
            io_value = step_data.get("value", 0)
            print(f"IO operation: {io_action} on pin {io_pin} with value {io_value}")
            sys.stdout.flush()
            # TODO: Implement actual I/O operations with Arduino
            success = True
        
        # Send step completion notification
        message = {
            "type": "program_execution",
            "status": "step_completed" if success else "step_failed",
            "program_id": program_id,
            "step_index": step_index,
            "step_type": step_type,
            "timestamp": time.time()
        }
        for connection in motion.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
        
        # Stop execution if step failed
        if not success:
            print(f"Program execution stopped due to failure in step {step_index}: {step_type}")
            sys.stdout.flush()
            
            # Send program failure notification
            message = {
                "type": "program_execution",
                "status": "failed",
                "program_id": program_id,
                "failed_step": step_index,
                "timestamp": time.time()
            }
            for connection in motion.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass
            
            return False
    
    # Send program completion notification
    message = {
        "type": "program_execution",
        "status": "completed",
        "program_id": program_id,
        "timestamp": time.time()
    }
    for connection in motion.active_connections:
        try:
            await connection.send_json(message)
        except:
            pass
    
    print(f"Program {program_id} executed successfully")
    sys.stdout.flush()
    return True


@router.post("/programs/save_position")
async def api_save_position(request: SavePositionRequest):
    """Save the current position with a name"""
    position_id = str(uuid.uuid4())
    saved_positions[position_id] = {
        "id": position_id,
        "name": request.name,
        "timestamp": datetime.datetime.now().isoformat(),
        "joint_positions": copy.deepcopy(motion.current_joint_positions),
        "ee_position": copy.deepcopy(motion.current_ee_position)
    }
    
    # Save to file
    save_data_to_file("saved_positions.json", saved_positions)
    
    return {
        "success": True,
        "position_id": position_id,
        "position": saved_positions[position_id]
    }

@router.get("/programs/saved_positions")
def api_get_saved_positions():
    """Get all saved positions"""
    return {"positions": list(saved_positions.values())}

@router.delete("/programs/saved_positions/{position_id}")
def api_delete_position(position_id: str):
    """Delete a saved position"""
    if position_id in saved_positions:
        del saved_positions[position_id]
        save_data_to_file("saved_positions.json", saved_positions)
        return {"success": True}
    else:
        return {"success": False, "error": "Position not found"}

@router.post("/programs/programs")
def api_create_program(request: CreateProgramRequest):
    """Create a new program"""
    program_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    programs[program_id] = {
        "id": program_id,
        "name": request.name,
        "description": request.description,
        "steps": [],
        "created": timestamp,
        "modified": timestamp
    }
    
    save_data_to_file("programs.json", programs)
    
    return {
        "success": True,
        "program_id": program_id,
        "program": programs[program_id]
    }

@router.get("/programs/programs")
def api_get_programs():
    """Get all programs"""
    return {"programs": list(programs.values())}

@router.get("/programs/programs/{program_id}")
def api_get_program(program_id: str):
    """Get a specific program"""
    if program_id in programs:
        return programs[program_id]
    else:
        return {"success": False, "error": "Program not found"}

@router.put("/programs/programs/{program_id}")
def api_update_program(program_id: str, request: UpdateProgramRequest):
    """Update a program"""
    if program_id not in programs:
        return {"success": False, "error": "Program not found"}
    
    if request.name is not None:
        programs[program_id]["name"] = request.name
    
    if request.description is not None:
        programs[program_id]["description"] = request.description
    
    if request.steps is not None:
        programs[program_id]["steps"] = [step.dict() for step in request.steps]
    
    programs[program_id]["modified"] = datetime.datetime.now().isoformat()
    
    save_data_to_file("programs.json", programs)
    
    return {
        "success": True,
        "program": programs[program_id]
    }

@router.delete("/programs/programs/{program_id}")
def api_delete_program(program_id: str):
    """Delete a program"""
    if program_id in programs:
        del programs[program_id]
        save_data_to_file("programs.json", programs)
        return {"success": True}
    else:
        return {"success": False, "error": "Program not found"}

@router.post("/programs/programs/{program_id}/execute")
async def api_execute_program(program_id: str, background_tasks: BackgroundTasks):
    """Execute a program"""
    if program_id not in programs:
        return {"success": False, "error": "Program not found"}
    
    background_tasks.add_task(execute_program, program_id, background_tasks)
    
    return {"success": True, "message": f"Program {program_id} execution started"}


saved_positions = load_data_from_file("saved_positions.json", {})
programs = load_data_from_file("programs.json", {})
