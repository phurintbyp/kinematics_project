from fastapi import FastAPI, WebSocket, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import sys
import os
import time
from config import SIMULATION_MODE
from arduino_communication import ArduinoCommunicator
from routers import motion, programs

app = FastAPI(title="Robotic Arm Control API")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


frontend_build_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "build")
if os.path.exists(frontend_build_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_path, "static")), name="static")

app.include_router(motion.router, prefix="/api/motion", tags=["motion"])
app.include_router(programs.router, prefix="/api", tags=["programs"])

arduino = None
if not SIMULATION_MODE:
    arduino = ArduinoCommunicator()
    if not arduino.connected:
        print("WARNING: Failed to connect to Arduino. Operating in simulation mode.")
        sys.stdout.flush()

# Pass Arduino communicator to motion module
motion.arduino_communicator = arduino

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    

    connection_id = len(motion.active_connections)
    motion.active_connections.append(websocket)
    
    print(f"New WebSocket connection accepted. Active connections: {len(motion.active_connections)}")
    sys.stdout.flush()
    
    try:

        initial_message = {
            "type": "position_update",
            "timestamp": time.time(),
            "joint_positions": motion.current_joint_positions,
            "ee_position": motion.current_ee_position
        }
        await websocket.send_json(initial_message)
        print(f"Position update sent to connection {connection_id}")
        sys.stdout.flush()
        

        while True:
            data = await websocket.receive_json()
            print(f"Received WebSocket message: {data}")
            sys.stdout.flush()
            
            message_type = data.get('type', '')
            
            # Update handler for move_done message
            if message_type == 'move_done':
                await motion.handle_move_done(data)
                
            elif message_type == 'jog_start':
                await motion.handle_jog_start(data)
                

                if motion.jog_state['active']:
                    background_tasks = BackgroundTasks()
                    background_tasks.add_task(motion.jog_motion_control, background_tasks)
            
            elif message_type == 'jog_stop':
                await motion.handle_jog_stop()
            
            elif message_type == 'jog_velocity':
                await motion.handle_jog_velocity(data)
            
            elif message_type == 'jog_increment':
                await motion.handle_jog_increment(data)
            
            elif message_type == 'moveJ':
                await motion.handle_moveJ(data)
            
            elif message_type == 'moveL':
                await motion.handle_moveL(data)
            
            elif message_type == 'emergency_stop':
                await motion.handle_emergency_stop()
            
            else:
                print(f"Unknown message type: {message_type}")
                sys.stdout.flush()
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        sys.stdout.flush()
    
    finally:

        if websocket in motion.active_connections:
            motion.active_connections.remove(websocket)
        print(f"WebSocket connection closed. Active connections: {len(motion.active_connections)}")
        sys.stdout.flush()


@app.get("/")
def read_root():
    return {"message": "Robotic Arm Control API"}


@app.get("/api/joint_positions")
def get_joint_positions():
    return motion.current_joint_positions

@app.get("/api/ee_position")
def get_ee_position():
    return motion.current_ee_position

@app.post("/api/jog_start")
async def api_jog_start(command: motion.JogCommand, background_tasks: BackgroundTasks):
    await motion.handle_jog_start(command.dict())
    
    # Start background task if not already running
    if motion.jog_state['active']:
        background_tasks.add_task(motion.jog_motion_control, background_tasks)
    
    return {"success": True}

@app.post("/api/jog_stop")
async def api_jog_stop():
    await motion.handle_jog_stop()
    return {"success": True}

@app.post("/api/jog_velocity")
async def api_jog_velocity(command: motion.JogVelocity):
    await motion.handle_jog_velocity(command.dict())
    return {"success": True}

@app.post("/api/emergency_stop")
async def api_emergency_stop():
    await motion.handle_emergency_stop()
    return {"success": True}

@app.post("/api/save_position")
async def api_save_position(request: programs.SavePositionRequest):
    return await programs.api_save_position(request)

@app.get("/api/saved_positions")
def api_get_saved_positions():
    return programs.api_get_saved_positions()

@app.delete("/api/saved_positions/{position_id}")
def api_delete_position(position_id: str):
    return programs.api_delete_position(position_id)

@app.post("/api/home")
async def api_home():
    return await motion.api_home()

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str, request: Request):

    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "build")


    file_path = os.path.join(frontend_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    

    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="File not found")

@app.on_event("startup")
async def startup_event():

    programs.saved_positions = programs.load_data_from_file("saved_positions.json", {})
    programs.programs = programs.load_data_from_file("programs.json", {})
    
    print("Application startup: saved positions and programs loaded")
    sys.stdout.flush()
