// Main JavaScript for Robot Arm Control Pendant

// Socket.io connection
let socket;
let connected = false;

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.IO server
    const socket = io();
    
    // Global variables
    let currentJointPositions = {
        'base_rotation': 0,
        'shoulder_rotation': 0,
        'prismatic_extension': 0,
        'elbow_rotation': 0,
        'wrist_rotation': 0,
        'end_effector_rotation': 0
    };

    let currentEEPosition = {
        'x': 0,
        'y': 0,
        'z': 0,
        'roll': 0,
        'pitch': 0,
        'yaw': 0
    };

    let savedPositions = [];
    let programSequence = [];
    let isConnected = false;
    let isProgramRunning = false;

    // DOM Elements
    const statusIndicator = document.getElementById('connection-status');
    const jointPositionElements = {
        'base_rotation': document.getElementById('joint-base-rotation'),
        'shoulder_rotation': document.getElementById('joint-shoulder-rotation'),
        'prismatic_extension': document.getElementById('joint-prismatic-extension'),
        'elbow_rotation': document.getElementById('joint-elbow-rotation'),
        'wrist_rotation': document.getElementById('joint-wrist-rotation'),
        'end_effector_rotation': document.getElementById('joint-end-effector-rotation')
    };

    const eePositionElements = {
        'x': document.getElementById('ee-x'),
        'y': document.getElementById('ee-y'),
        'z': document.getElementById('ee-z'),
        'roll': document.getElementById('ee-roll'),
        'pitch': document.getElementById('ee-pitch'),
        'yaw': document.getElementById('ee-yaw')
    };

    // Socket.IO event handlers
    socket.on('connect', () => {
        console.log('Connected to server');
        isConnected = true;
        updateConnectionStatus(true);
        
        // Request initial data
        fetch('/api/joint_positions')
            .then(response => response.json())
            .then(data => {
                updateJointPositions(data);
            });
            
        fetch('/api/ee_position')
            .then(response => response.json())
            .then(data => {
                updateEEPosition(data);
            });
            
        // Get saved positions
        fetchSavedPositions();
        
        // Get saved programs
        fetchPrograms();
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        isConnected = false;
        updateConnectionStatus(false);
    });

    socket.on('joint_positions_update', (data) => {
        updateJointPositions(data);
    });

    socket.on('ee_position_update', (data) => {
        updateEEPosition(data);
    });

    socket.on('saved_positions_update', (data) => {
        savedPositions = data;
        renderSavedPositions();
    });

    socket.on('program_sequences_update', (data) => {
        renderPrograms(data);
    });

    socket.on('program_status', (data) => {
        updateProgramStatus(data);
    });

    // Update functions
    function updateConnectionStatus(connected) {
        if (statusIndicator) {
            statusIndicator.textContent = connected ? 'Connected' : 'Disconnected';
            statusIndicator.className = connected ? 'connected' : 'disconnected';
        }
    }

    function updateJointPositions(positions) {
        currentJointPositions = positions;
        
        // Update the displayed values
        for (const [joint, value] of Object.entries(positions)) {
            const elementId = joint.replace(/_/g, '-');
            const element = document.getElementById(`joint-${elementId}`);
            if (element) {
                element.textContent = parseFloat(value).toFixed(2);
            } else {
                console.warn(`Element with ID joint-${elementId} not found`);
            }
        }
        
        // Log the updated positions for debugging
        console.log("Updated joint positions:", positions);
    }

    function updateEEPosition(position) {
        currentEEPosition = position;
        
        // Update the displayed values
        for (const [axis, value] of Object.entries(position)) {
            const element = document.getElementById(`ee-${axis}`);
            if (element) {
                element.textContent = parseFloat(value).toFixed(2);
            } else {
                console.warn(`Element with ID ee-${axis} not found`);
            }
        }
        
        // Log the updated positions for debugging
        console.log("Updated EE position:", position);
    }

    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Add active class to clicked tab
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Jogging controls
    document.querySelectorAll('.jog-btn').forEach(button => {
        button.addEventListener('click', function() {
            const joint = this.getAttribute('data-joint');
            const increment = parseFloat(this.getAttribute('data-increment'));
            
            // Calculate the new value
            const currentValue = currentJointPositions[joint] || 0;
            const newValue = currentValue + increment;
            
            console.log(`Jogging ${joint} by ${increment} to ${newValue}`);
            
            // Send the updated joint position to the server
            const data = {};
            data[joint] = newValue;
            
            fetch('/api/moveJ', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Jog command sent successfully');
                } else {
                    console.error('Error sending jog command:', data.message);
                }
            })
            .catch(error => {
                console.error('Error sending jog command:', error);
            });
        });
    });

    // Emergency stop
    const emergencyStopButton = document.getElementById('emergency-stop');
    if (emergencyStopButton) {
        emergencyStopButton.addEventListener('click', function() {
            fetch('/api/emergency_stop', {
                method: 'POST'
            });
        });
    }

    // Save position functionality
    const savePositionButton = document.getElementById('save-position');
    if (savePositionButton) {
        savePositionButton.addEventListener('click', function() {
            const positionName = prompt('Enter a name for this position:');
            if (positionName) {
                savePosition(positionName);
            }
        });
    }

    function savePosition(name) {
        fetch('/api/save_position', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Position saved successfully!', 'success');
                fetchSavedPositions();
            } else {
                showNotification('Error saving position: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Error saving position: ' + error, 'error');
        });
    }

    function fetchSavedPositions() {
        fetch('/api/get_saved_positions')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    savedPositions = data.positions;
                    renderSavedPositions();
                }
            })
            .catch(error => {
                console.error('Error fetching saved positions:', error);
            });
    }

    function renderSavedPositions() {
        const positionsList = document.getElementById('positions-list');
        if (!positionsList) return;
        
        if (savedPositions.length === 0) {
            positionsList.innerHTML = `
                <div class="empty-state">
                    <p>No positions saved yet. Use the Jogging tab to move the robot and save positions.</p>
                </div>
            `;
            return;
        }
        
        positionsList.innerHTML = '';
        
        savedPositions.forEach(position => {
            const positionItem = document.createElement('div');
            positionItem.className = 'position-item';
            positionItem.innerHTML = `
                <div class="position-info">
                    <div class="position-name">${position.name}</div>
                    <div class="position-coordinates">
                        X: ${position.ee_position.x.toFixed(2)}, 
                        Y: ${position.ee_position.y.toFixed(2)}, 
                        Z: ${position.ee_position.z.toFixed(2)}
                    </div>
                </div>
                <div class="position-actions">
                    <button class="add-to-sequence" data-id="${position.id}" title="Add to Sequence">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="move-to-position" data-id="${position.id}" title="Move to Position">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="delete-position" data-id="${position.id}" title="Delete Position">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            positionsList.appendChild(positionItem);
        });
        
        // Add event listeners to the buttons
        document.querySelectorAll('.add-to-sequence').forEach(button => {
            button.addEventListener('click', function() {
                const positionId = this.getAttribute('data-id');
                addToSequence(positionId);
            });
        });
        
        document.querySelectorAll('.move-to-position').forEach(button => {
            button.addEventListener('click', function() {
                const positionId = this.getAttribute('data-id');
                moveToPosition(positionId);
            });
        });
        
        document.querySelectorAll('.delete-position').forEach(button => {
            button.addEventListener('click', function() {
                const positionId = this.getAttribute('data-id');
                deletePosition(positionId);
            });
        });
    }

    function addToSequence(positionId) {
        const position = savedPositions.find(p => p.id === positionId);
        if (!position) return;
        
        programSequence.push(positionId);
        renderSequence();
    }

    function moveToPosition(positionId) {
        const position = savedPositions.find(p => p.id === positionId);
        if (!position) return;
        
        // Move to the joint positions
        fetch('/api/moveJ', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(position.joint_positions)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Moving to position: ' + position.name, 'info');
            }
        });
    }

    function deletePosition(positionId) {
        if (confirm('Are you sure you want to delete this position?')) {
            fetch(`/api/delete_position/${positionId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('Position deleted successfully!', 'success');
                    fetchSavedPositions();
                    
                    // Remove from sequence if present
                    programSequence = programSequence.filter(id => id !== positionId);
                    renderSequence();
                } else {
                    showNotification('Error deleting position: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('Error deleting position: ' + error, 'error');
            });
        }
    }

    function renderSequence() {
        const sequenceList = document.getElementById('sequence-list');
        if (!sequenceList) return;
        
        if (programSequence.length === 0) {
            sequenceList.innerHTML = `
                <div class="empty-state">
                    <p>No sequence created yet. Add saved positions to create a program.</p>
                </div>
            `;
            return;
        }
        
        sequenceList.innerHTML = '';
        
        programSequence.forEach((positionId, index) => {
            const position = savedPositions.find(p => p.id === positionId);
            if (!position) return;
            
            const sequenceItem = document.createElement('div');
            sequenceItem.className = 'sequence-item';
            sequenceItem.innerHTML = `
                <div class="sequence-info">
                    <div class="sequence-name">${index + 1}. ${position.name}</div>
                    <div class="sequence-coordinates">
                        X: ${position.ee_position.x.toFixed(2)}, 
                        Y: ${position.ee_position.y.toFixed(2)}, 
                        Z: ${position.ee_position.z.toFixed(2)}
                    </div>
                </div>
                <div class="sequence-actions">
                    <button class="move-up-sequence" data-index="${index}" title="Move Up" ${index === 0 ? 'disabled' : ''}>
                        <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="move-down-sequence" data-index="${index}" title="Move Down" ${index === programSequence.length - 1 ? 'disabled' : ''}>
                        <i class="fas fa-arrow-down"></i>
                    </button>
                    <button class="remove-from-sequence" data-index="${index}" title="Remove from Sequence">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            sequenceList.appendChild(sequenceItem);
        });
        
        // Add event listeners to the buttons
        document.querySelectorAll('.move-up-sequence').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                if (index > 0) {
                    // Swap with the previous item
                    [programSequence[index], programSequence[index - 1]] = [programSequence[index - 1], programSequence[index]];
                    renderSequence();
                }
            });
        });
        
        document.querySelectorAll('.move-down-sequence').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                if (index < programSequence.length - 1) {
                    // Swap with the next item
                    [programSequence[index], programSequence[index + 1]] = [programSequence[index + 1], programSequence[index]];
                    renderSequence();
                }
            });
        });
        
        document.querySelectorAll('.remove-from-sequence').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                programSequence.splice(index, 1);
                renderSequence();
            });
        });
    }

    // Program execution controls
    const runProgramButton = document.getElementById('run-program');
    if (runProgramButton) {
        runProgramButton.addEventListener('click', function() {
            if (programSequence.length === 0) {
                showNotification('Cannot run an empty program. Add positions to the sequence first.', 'error');
                return;
            }
            
            // Use a default name for temporary program execution
            const programName = "temp_program_" + new Date().getTime();
            
            // Create and run the program
            createAndRunProgram(programName);
        });
    }

    const stopProgramButton = document.getElementById('stop-program');
    if (stopProgramButton) {
        stopProgramButton.addEventListener('click', function() {
            fetch('/api/stop_program', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('Program stopped', 'info');
                    isProgramRunning = false;
                    updateProgramControls();
                }
            });
        });
    }

    const saveProgramButton = document.getElementById('save-program');
    if (saveProgramButton) {
        saveProgramButton.addEventListener('click', function() {
            if (programSequence.length === 0) {
                showNotification('Cannot save an empty program. Add positions to the sequence first.', 'error');
                return;
            }
            
            const programName = prompt('Enter a name for this program:');
            if (!programName) return;
            
            // Save the program
            saveProgram(programName);
        });
    }

    function createAndRunProgram(name) {
        // Create the program
        fetch('/api/create_program', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                position_ids: programSequence,
                settings: {
                    speed: document.getElementById('movement-speed').value,
                    repeat_count: document.getElementById('repeat-count').value
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Run the program
                runProgram(data.program.id);
            } else {
                showNotification('Error creating program: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Error creating program: ' + error, 'error');
        });
    }

    function saveProgram(name) {
        fetch('/api/create_program', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                position_ids: programSequence,
                settings: {
                    speed: document.getElementById('movement-speed').value,
                    repeat_count: document.getElementById('repeat-count').value
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Program saved successfully!', 'success');
                fetchPrograms();
            } else {
                showNotification('Error saving program: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Error saving program: ' + error, 'error');
        });
    }

    function runProgram(programId) {
        fetch(`/api/run_program/${programId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Program started', 'info');
                isProgramRunning = true;
                updateProgramControls();
            } else {
                showNotification('Error running program: ' + data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Error running program: ' + error, 'error');
        });
    }

    function fetchPrograms() {
        fetch('/api/get_programs')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderPrograms(data.programs);
                }
            })
            .catch(error => {
                console.error('Error fetching programs:', error);
            });
    }

    function renderPrograms(programs) {
        // This would be used to display a list of saved programs
        // Not implemented in the current UI
    }

    function updateProgramStatus(status) {
        if (status.status === 'running') {
            isProgramRunning = true;
            // Update UI to show program progress
            showNotification(`Running program: ${status.position_name || ''}`, 'info');
        } else if (status.status === 'completed' || status.status === 'stopped' || status.status === 'error') {
            isProgramRunning = false;
            // Update UI to show program completion
            showNotification(`Program ${status.status}${status.message ? ': ' + status.message : ''}`, 
                status.status === 'completed' ? 'success' : status.status === 'error' ? 'error' : 'info');
        }
        
        updateProgramControls();
    }

    function updateProgramControls() {
        const runButton = document.getElementById('run-program');
        const stopButton = document.getElementById('stop-program');
        const saveButton = document.getElementById('save-program');
        
        if (runButton && stopButton && saveButton) {
            if (isProgramRunning) {
                runButton.disabled = true;
                stopButton.disabled = false;
                saveButton.disabled = true;
            } else {
                runButton.disabled = false;
                stopButton.disabled = true;
                saveButton.disabled = false;
            }
        }
    }

    // Helper functions
    function showNotification(message, type = 'info') {
        // Create a notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add it to the document
        document.body.appendChild(notification);
        
        // Remove it after a delay
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 3000);
    }

    // Initialize the UI
    updateProgramControls();
});
