import React, { useState, useEffect } from 'react';
import './ProgramEditor.css';

const ProgramEditor = ({ websocket }) => {
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [programName, setProgramName] = useState('');
  const [programDesc, setProgramDesc] = useState('');
  const [savedPositions, setSavedPositions] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [newStepType, setNewStepType] = useState('moveJ');
  const [newWaitTime, setNewWaitTime] = useState(1);
  const [editingStep, setEditingStep] = useState(null);
  const [backendBaseUrl, setBackendBaseUrl] = useState('');

  // Set up backend URL
  useEffect(() => {
    const backendHost = window.location.hostname;
    const backendPort = '8080';
    setBackendBaseUrl(`http://${backendHost}:${backendPort}`);
  }, []);

  // Load programs and saved positions on component mount
  useEffect(() => {
    if (backendBaseUrl) {
      fetchPrograms();
      fetchSavedPositions();
    }

    // Set up WebSocket listener for program execution updates
    if (websocket) {
      const handleMessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'program_execution') {
          if (data.status === 'started') {
            setIsExecuting(true);
          } else if (data.status === 'completed' || data.status === 'failed') {
            setIsExecuting(false);
            setCurrentStep(null);
          } else if (data.status === 'step_started') {
            setCurrentStep(data.step_index);
          }
        }
      };

      websocket.addEventListener('message', handleMessage);
      return () => {
        websocket.removeEventListener('message', handleMessage);
      };
    }
  }, [websocket, backendBaseUrl]);

  const fetchPrograms = async () => {
    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/programs`);
      const data = await response.json();
      setPrograms(data.programs || []);
    } catch (error) {
      console.error('Error fetching programs:', error);
    }
  };

  const fetchSavedPositions = async () => {
    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/saved_positions`);
      const data = await response.json();
      setSavedPositions(data.positions || []);
    } catch (error) {
      console.error('Error fetching saved positions:', error);
    }
  };

  const createNewProgram = async () => {
    if (!programName) return;

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/programs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: programName,
          description: programDesc
        })
      });
      const data = await response.json();
      if (data.success) {
        fetchPrograms();
        setSelectedProgram(data.program);
        setProgramName('');
        setProgramDesc('');
      }
    } catch (error) {
      console.error('Error creating program:', error);
    }
  };

  const saveProgram = async () => {
    if (!selectedProgram) return;

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/programs/${selectedProgram.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: selectedProgram.name,
          description: selectedProgram.description,
          steps: selectedProgram.steps
        })
      });
      const data = await response.json();
      if (data.success) {
        fetchPrograms();
      }
    } catch (error) {
      console.error('Error saving program:', error);
    }
  };

  const deleteProgram = async () => {
    if (!selectedProgram) return;
    if (!window.confirm(`Are you sure you want to delete the program "${selectedProgram.name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/programs/${selectedProgram.id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        fetchPrograms();
        setSelectedProgram(null);
      }
    } catch (error) {
      console.error('Error deleting program:', error);
    }
  };

  const executeProgram = async () => {
    if (!selectedProgram || isExecuting) return;

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/programs/${selectedProgram.id}/execute`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setIsExecuting(true);
      }
    } catch (error) {
      console.error('Error executing program:', error);
    }
  };

  const saveCurrentPosition = async () => {
    const name = prompt('Enter a name for this position:');
    if (!name) return;

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/save_position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      const data = await response.json();
      if (data.success) {
        fetchSavedPositions();
      }
    } catch (error) {
      console.error('Error saving position:', error);
    }
  };

  const deletePosition = async (positionId) => {
    if (!window.confirm('Are you sure you want to delete this position?')) {
      return;
    }

    try {
      const response = await fetch(`${backendBaseUrl}/api/programs/saved_positions/${positionId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        fetchSavedPositions();
        if (selectedPosition && selectedPosition.id === positionId) {
          setSelectedPosition(null);
        }
      }
    } catch (error) {
      console.error('Error deleting position:', error);
    }
  };

  const updateProgramStep = (index, updatedStep) => {
    if (!selectedProgram) return;

    const updatedSteps = [...selectedProgram.steps];
    updatedSteps[index] = updatedStep;

    setSelectedProgram({
      ...selectedProgram,
      steps: updatedSteps
    });
  };

  const addStep = () => {
    if (!selectedProgram) return;

    let newStep = {
      type: newStepType,
      data: {}
    };

    // Configure step data based on type
    if (newStepType === 'moveJ' || newStepType === 'moveL') {
      if (!selectedPosition) {
        alert('Please select a position first.');
        return;
      }
      
      if (newStepType === 'moveJ') {
        newStep.data = {
          joint_positions: selectedPosition.joint_positions,
          velocity: 50
        };
      } else {
        newStep.data = {
          position: selectedPosition.ee_position,
          velocity: 50
        };
      }
    } else if (newStepType === 'wait') {
      newStep.data = {
        time: parseFloat(newWaitTime)
      };
    } else if (newStepType === 'io') {
      // Placeholder for IO operations
      newStep.data = {
        action: 'set',
        pin: 13,
        value: 1
      };
    }

    // If editing an existing step, replace it
    if (editingStep !== null) {
      updateProgramStep(editingStep, newStep);
      setEditingStep(null);
    } else {
      // Otherwise add a new step
      const updatedSteps = [...(selectedProgram.steps || []), newStep];
      setSelectedProgram({
        ...selectedProgram,
        steps: updatedSteps
      });
    }

    // Reset step form
    setNewStepType('moveJ');
    setNewWaitTime(1);
  };

  const removeStep = (index) => {
    if (!selectedProgram) return;

    const updatedSteps = [...selectedProgram.steps];
    updatedSteps.splice(index, 1);

    setSelectedProgram({
      ...selectedProgram,
      steps: updatedSteps
    });
  };

  const editStep = (index) => {
    if (!selectedProgram || !selectedProgram.steps[index]) return;

    const step = selectedProgram.steps[index];
    setEditingStep(index);
    setNewStepType(step.type);

    if (step.type === 'wait') {
      setNewWaitTime(step.data.time || 1);
    }
  };

  const moveStep = (index, direction) => {
    if (!selectedProgram) return;
    if (
      (direction < 0 && index === 0) || 
      (direction > 0 && index === selectedProgram.steps.length - 1)
    ) {
      return;
    }

    const updatedSteps = [...selectedProgram.steps];
    const temp = updatedSteps[index];
    updatedSteps[index] = updatedSteps[index + direction];
    updatedSteps[index + direction] = temp;

    setSelectedProgram({
      ...selectedProgram,
      steps: updatedSteps
    });
  };

  // Render step information
  const renderStepInfo = (step, index) => {
    if (step.type === 'moveJ') {
      return (
        <div className="step-info">
          <span className="step-number">{index + 1}</span>
          <span className="step-type">MoveJ</span>
          <span className="step-data">
            {step.data.joint_positions ? 
              `Joint positions (deg): ${Object.entries(step.data.joint_positions)
                .filter(([key]) => key !== 'prismatic_extension')
                .map(([key, val]) => `${key.split('_')[0]}: ${val.toFixed(1)}`)
                .join(', ')}` +
              `, Extension (mm): ${step.data.joint_positions.prismatic_extension?.toFixed(1) || '0'}`
              : 'Invalid joint data'}
          </span>
        </div>
      );
    } else if (step.type === 'moveL') {
      return (
        <div className="step-info">
          <span className="step-number">{index + 1}</span>
          <span className="step-type">MoveL</span>
          <span className="step-data">
            {step.data.position ? 
              `Position (mm): X:${step.data.position.x?.toFixed(1) || '0'}, Y:${step.data.position.y?.toFixed(1) || '0'}, Z:${step.data.position.z?.toFixed(1) || '0'}` 
              : 'Invalid position data'}
          </span>
        </div>
      );
    } else if (step.type === 'wait') {
      return (
        <div className="step-info">
          <span className="step-number">{index + 1}</span>
          <span className="step-type">Wait</span>
          <span className="step-data">{step.data.time} seconds</span>
        </div>
      );
    } else if (step.type === 'io') {
      return (
        <div className="step-info">
          <span className="step-number">{index + 1}</span>
          <span className="step-type">I/O</span>
          <span className="step-data">
            {`${step.data.action} pin ${step.data.pin} to ${step.data.value}`}
          </span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="program-editor">
      <h2>Robot Programming</h2>
      
      <div className="program-editor-layout">
        <div className="program-list-panel">
          <div className="panel-header">
            <h3>Programs</h3>
          </div>
          
          <div className="program-list">
            {programs.map(program => (
              <div 
                key={program.id} 
                className={`program-item ${selectedProgram && selectedProgram.id === program.id ? 'selected' : ''}`}
                onClick={() => setSelectedProgram(program)}
              >
                <div className="program-name">{program.name}</div>
                <div className="program-steps-count">{program.steps ? program.steps.length : 0} steps</div>
              </div>
            ))}
          </div>
          
          <div className="new-program-form">
            <input
              type="text"
              placeholder="Program Name"
              value={programName}
              onChange={(e) => setProgramName(e.target.value)}
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={programDesc}
              onChange={(e) => setProgramDesc(e.target.value)}
            />
            <button onClick={createNewProgram}>Create New Program</button>
          </div>
        </div>
        
        <div className="program-editor-panel">
          {selectedProgram ? (
            <>
              <div className="panel-header">
                <h3>Editing: {selectedProgram.name}</h3>
                <div className="program-actions">
                  <button 
                    onClick={saveProgram} 
                    className="save-btn"
                    disabled={isExecuting}
                  >
                    Save
                  </button>
                  <button 
                    onClick={executeProgram} 
                    className="execute-btn"
                    disabled={isExecuting || !selectedProgram.steps || selectedProgram.steps.length === 0}
                  >
                    {isExecuting ? 'Running...' : 'Run Program'}
                  </button>
                  <button 
                    onClick={deleteProgram} 
                    className="delete-btn"
                    disabled={isExecuting}
                  >
                    Delete
                  </button>
                </div>
              </div>
              
              <div className="steps-list">
                {selectedProgram.steps && selectedProgram.steps.length > 0 ? (
                  selectedProgram.steps.map((step, index) => (
                    <div 
                      key={index} 
                      className={`step-item ${currentStep === index + 1 ? 'executing' : ''}`}
                    >
                      {renderStepInfo(step, index)}
                      <div className="step-actions">
                        <button onClick={() => moveStep(index, -1)} disabled={index === 0 || isExecuting}>↑</button>
                        <button onClick={() => moveStep(index, 1)} disabled={index === selectedProgram.steps.length - 1 || isExecuting}>↓</button>
                        <button onClick={() => editStep(index)} disabled={isExecuting}>Edit</button>
                        <button onClick={() => removeStep(index)} disabled={isExecuting}>Remove</button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-steps">No steps added yet. Use the form below to add steps.</div>
                )}
              </div>
              
              <div className="add-step-form">
                <h4>{editingStep !== null ? 'Edit Step' : 'Add New Step'}</h4>
                
                <div className="form-group">
                  <label>Step Type:</label>
                  <select 
                    value={newStepType} 
                    onChange={(e) => setNewStepType(e.target.value)}
                    disabled={isExecuting}
                  >
                    <option value="moveJ">MoveJ (Joint Movement)</option>
                    <option value="moveL">MoveL (Linear Movement)</option>
                    <option value="wait">Wait</option>
                    <option value="io">I/O Operation</option>
                  </select>
                </div>
                
                {newStepType === 'wait' && (
                  <div className="form-group">
                    <label>Wait Time (seconds):</label>
                    <input 
                      type="number" 
                      min="0.1" 
                      step="0.1" 
                      value={newWaitTime} 
                      onChange={(e) => setNewWaitTime(e.target.value)}
                      disabled={isExecuting}
                    />
                  </div>
                )}
                
                {(newStepType === 'moveJ' || newStepType === 'moveL') && (
                  <div className="form-group">
                    <label>Target Position:</label>
                    <select 
                      value={selectedPosition ? selectedPosition.id : ''}
                      onChange={(e) => {
                        const position = savedPositions.find(pos => pos.id === e.target.value);
                        setSelectedPosition(position);
                      }}
                      disabled={isExecuting}
                    >
                      <option value="">Select a saved position</option>
                      {savedPositions.map(position => (
                        <option key={position.id} value={position.id}>{position.name}</option>
                      ))}
                    </select>
                  </div>
                )}
                
                <div className="form-actions">
                  <button 
                    onClick={addStep} 
                    disabled={isExecuting || 
                      ((newStepType === 'moveJ' || newStepType === 'moveL') && !selectedPosition)}
                  >
                    {editingStep !== null ? 'Update Step' : 'Add Step'}
                  </button>
                  
                  {editingStep !== null && (
                    <button 
                      onClick={() => {
                        setEditingStep(null);
                        setNewStepType('moveJ');
                        setNewWaitTime(1);
                      }}
                      disabled={isExecuting}
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="no-program-selected">
              <p>Select a program from the list or create a new one to begin.</p>
            </div>
          )}
        </div>
        
        <div className="positions-panel">
          <div className="panel-header">
            <h3>Saved Positions</h3>
            <button 
              onClick={saveCurrentPosition} 
              className="save-position-btn"
              disabled={isExecuting}
            >
              Save Current Position
            </button>
          </div>
          
          <div className="positions-list">
            {savedPositions.length > 0 ? (
              savedPositions.map(position => (
                <div 
                  key={position.id} 
                  className={`position-item ${selectedPosition && selectedPosition.id === position.id ? 'selected' : ''}`}
                  onClick={() => setSelectedPosition(position)}
                >
                  <div className="position-name">{position.name}</div>
                  <div className="position-info">
                    <div>X: {position.ee_position.x.toFixed(1)} mm</div>
                    <div>Y: {position.ee_position.y.toFixed(1)} mm</div>
                    <div>Z: {position.ee_position.z.toFixed(1)} mm</div>
                  </div>
                  <button 
                    className="delete-position-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePosition(position.id);
                    }}
                    disabled={isExecuting}
                  >
                    Delete
                  </button>
                </div>
              ))
            ) : (
              <div className="empty-positions">No positions saved. Use the button above to save the current robot position.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgramEditor;
