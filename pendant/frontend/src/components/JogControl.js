import React, { useState, useEffect, useRef } from 'react';
import ReactSlider from 'react-slider';
import './JogControl.css';

const JogControl = ({ sendWebSocketMessage, homingInProgress, setHomingInProgress }) => {
  const [mode, setMode] = useState('joint'); // 'joint' or 'cartesian'
  const [incrementSize, setIncrementSize] = useState(5); // Default increment size
  const [pendantConnected, setPendantConnected] = useState(false);
  const [activeJointIndex, setActiveJointIndex] = useState(0); // For pendant joint selection
  const [controlMode, setControlMode] = useState('keyboard'); // 'keyboard' or 'pendant'

  // References to track pendant state
  const pendantRef = useRef(null);
  const requestRef = useRef(null);
  const previousButtonsRef = useRef({});
  const joystickDeadzone = 0.15; // Deadzone for joystick to prevent drift

  const joints = {
    base_rotation: 'Base',
    shoulder_rotation: 'Shoulder',
    prismatic_extension: 'Extension',
    elbow_rotation: 'Elbow',
    elbow2_rotation: 'Elbow2'
  };

  const axes = {
    x: 'X',
    y: 'Y',
    z: 'Z',
    roll: 'Roll',
    pitch: 'Pitch',
    yaw: 'Yaw'
  };

  // Handle keyboard controls
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Only handle keys if no input element is focused
      if (document.activeElement.tagName === 'INPUT' || 
          document.activeElement.tagName === 'TEXTAREA' || 
          document.activeElement.tagName === 'SELECT') {
        return;
      }
      
      // Switch control mode
      if (e.key === 'g') setControlMode('pendant');
      if (e.key === 'k') setControlMode('keyboard');
      
      // Mode switching
      if (e.key === 'j') setMode('joint');
      if (e.key === 'c') setMode('cartesian');
      
      // Increment size presets
      if (e.key === '1') setIncrementSize(0.1); // Ultra Fine
      if (e.key === '2') setIncrementSize(1);   // Fine
      if (e.key === '3') setIncrementSize(5);   // Medium
      if (e.key === '4') setIncrementSize(10);  // Coarse
      if (e.key === '5') setIncrementSize(50);  // X-Large
      
      // Joint controls
      if (mode === 'joint') {
        const jointMap = {
          'q': { joint: 'base_rotation', direction: 1 },
          'a': { joint: 'base_rotation', direction: -1 },
          'w': { joint: 'shoulder_rotation', direction: 1 },
          's': { joint: 'shoulder_rotation', direction: -1 },
          'e': { joint: 'prismatic_extension', direction: 1 },
          'd': { joint: 'prismatic_extension', direction: -1 },
          'r': { joint: 'elbow_rotation', direction: 1 },
          'f': { joint: 'elbow_rotation', direction: -1 },
          't': { joint: 'elbow2_rotation', direction: 1 },
          'h': { joint: 'elbow2_rotation', direction: -1 }
        };
        
        if (jointMap[e.key]) {
          const { joint, direction } = jointMap[e.key];
          jogIncrement(joint, direction);
        }
      }
      
      // Cartesian controls
      if (mode === 'cartesian') {
        const cartesianMap = {
          'ArrowRight': { axis: 'x', direction: 1 },
          'ArrowLeft': { axis: 'x', direction: -1 },
          'ArrowUp': { axis: 'y', direction: 1 },
          'ArrowDown': { axis: 'y', direction: -1 },
          'PageUp': { axis: 'z', direction: 1 },
          'PageDown': { axis: 'z', direction: -1 },
          'u': { axis: 'roll', direction: 1 },
          'j': { axis: 'roll', direction: -1 },
          'i': { axis: 'pitch', direction: 1 },
          'k': { axis: 'pitch', direction: -1 },
          'o': { axis: 'yaw', direction: 1 },
          'l': { axis: 'yaw', direction: -1 },
        };
        
        if (cartesianMap[e.key]) {
          const { axis, direction } = cartesianMap[e.key];
          jogIncrement(axis, direction);
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [mode, incrementSize, sendWebSocketMessage]);

  // Send jog command via WebSocket
  const jogIncrement = (input, direction, intensity = 1) => {
    const jogData = {
      type: 'jog_increment',
      mode: mode,
      direction: direction,
      increment: incrementSize * intensity,
    };
    
    if (mode === 'joint') {
      jogData.joint = input;
    } else {
      jogData.axis = input;
    }
    
    console.log('Sending jog command:', jogData);
    sendWebSocketMessage(jogData);
  };
  
  // Update increment size and ensure it's one of the standard values
  const updateIncrementSize = (value) => {
    // Standard increment values
    const standardIncrements = [0.1, 1, 5, 10, 50];
    
    // Find the closest standard increment
    let closestIncrement = standardIncrements.reduce((prev, curr) => {
      return (Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev);
    });
    
    setIncrementSize(closestIncrement);
  };

  // Pendant detection and handling
  useEffect(() => {
    const detectPendant = () => {
      const pendants = navigator.getGamepads ? navigator.getGamepads() : [];
      for (let i = 0; i < pendants.length; i++) {
        if (pendants[i]) {
          pendantRef.current = pendants[i];
          setPendantConnected(true);
          setControlMode('pendant');
          console.log('Pendant connected:', pendants[i].id);
          return;
        }
      }
      pendantRef.current = null;
      setPendantConnected(false);
    };

    const handlePendantConnected = (e) => {
      console.log(`Pendant connected at index ${e.gamepad.index}: ${e.gamepad.id}`);
      pendantRef.current = e.gamepad;
      setPendantConnected(true);
      setControlMode('pendant');
    };

    const handlePendantDisconnected = (e) => {
      console.log(`Pendant disconnected at index ${e.gamepad.index}: ${e.gamepad.id}`);
      pendantRef.current = null;
      setPendantConnected(false);
      setControlMode('keyboard');
    };

    window.addEventListener('gamepadconnected', handlePendantConnected);
    window.addEventListener('gamepaddisconnected', handlePendantDisconnected);

    // Initial detection
    detectPendant();

    return () => {
      window.removeEventListener('gamepadconnected', handlePendantConnected);
      window.removeEventListener('gamepaddisconnected', handlePendantDisconnected);
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, []);

  // Pendant polling
  useEffect(() => {
    if (!pendantConnected || controlMode !== 'pendant') {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = null;
      }
      return;
    }

    const jointKeys = Object.keys(joints);
    
    const pollPendant = () => {
      const pendants = navigator.getGamepads ? navigator.getGamepads() : [];
      const pendant = pendants[pendantRef.current?.index || 0];
      
      if (!pendant) {
        requestRef.current = requestAnimationFrame(pollPendant);
        return;
      }

      // Initialize previous buttons state if it doesn't exist
      if (!previousButtonsRef.current) {
        previousButtonsRef.current = pendant.buttons.map(b => b.pressed);
      }

      // D-pad for joint selection in joint mode
      if (pendant.buttons[12].pressed && !previousButtonsRef.current[12]) { // D-pad Up
        if (mode === 'joint') {
          setActiveJointIndex(prev => (prev > 0 ? prev - 1 : 0));
        }
      }
      if (pendant.buttons[13].pressed && !previousButtonsRef.current[13]) { // D-pad Down
        if (mode === 'joint') {
          setActiveJointIndex(prev => (prev < jointKeys.length - 1 ? prev + 1 : jointKeys.length - 1));
        }
      }

      // Mode switching (Button X - typically button 2)
      if (pendant.buttons[2].pressed && !previousButtonsRef.current[2]) {
        setMode(prev => prev === 'joint' ? 'cartesian' : 'joint');
      }

      // Increment size switching (Button Y - typically button the 3)
      if (pendant.buttons[3].pressed && !previousButtonsRef.current[3]) {
        const standardIncrements = [0.1, 1, 5, 10, 50];
        const currentIndex = standardIncrements.indexOf(incrementSize);
        const nextIndex = (currentIndex + 1) % standardIncrements.length;
        setIncrementSize(standardIncrements[nextIndex]);
      }

      // Joint controls using joysticks
      if (mode === 'joint') {
        // Left joystick Y-axis for active joint control
        const leftYAxis = -pendant.axes[1];
        const intensity = (Math.abs(leftYAxis) - joystickDeadzone) / (1 - joystickDeadzone);
        if (Math.abs(leftYAxis) > joystickDeadzone) {
          const activeJoint = jointKeys[activeJointIndex];
          const intensity = (Math.abs(leftYAxis) - joystickDeadzone) / (1 - joystickDeadzone);
          jogIncrement(activeJoint, Math.sign(leftYAxis), intensity);
        }        
      } else { // Cartesian mode
        // Left joystick for X/Y movement
        const leftXAxis = pendant.axes[0];
        const leftYAxis = -pendant.axes[1]; // Invert so that up is positive
        
        if (Math.abs(leftXAxis) > joystickDeadzone) {
          jogIncrement('x', Math.sign(leftXAxis));
        }
        
        if (Math.abs(leftYAxis) > joystickDeadzone) {
          jogIncrement('y', Math.sign(leftYAxis));
        }
        
        // Right joystick for Z and rotation
        const rightXAxis = pendant.axes[2]; 
        const rightYAxis = -pendant.axes[3]; // Invert so that up is positive
        
        if (Math.abs(rightYAxis) > joystickDeadzone) {
          jogIncrement('z', Math.sign(rightYAxis));
        }
        
        if (Math.abs(rightXAxis) > joystickDeadzone) {
          jogIncrement('yaw', Math.sign(rightXAxis));
        }
        
        // Shoulder buttons for roll/pitch
        if (pendant.buttons[4].pressed) { // Left shoulder
          jogIncrement('roll', -1);
        }
        if (pendant.buttons[5].pressed) { // Right shoulder
          jogIncrement('roll', 1);
        }
        if (pendant.buttons[6].pressed) { // Left trigger as button
          jogIncrement('pitch', -1);
        }
        if (pendant.buttons[7].pressed) { // Right trigger as button
          jogIncrement('pitch', 1);
        }
      }

      // Update previous buttons state
      previousButtonsRef.current = pendant.buttons.map(b => b.pressed);

      // Continue polling
      requestRef.current = requestAnimationFrame(pollPendant);
    };

    requestRef.current = requestAnimationFrame(pollPendant);

    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [pendantConnected, controlMode, mode, incrementSize, activeJointIndex, sendWebSocketMessage]);

  // Add function to handle home button click
  const handleHomeClick = async () => {
    if (homingInProgress) return; // Prevent multiple clicks during homing
    
    setHomingInProgress(true);
    
    try {
      // Get the backend URL
      const backendHost = window.location.hostname;
      const backendPort = '8080'; // Backend runs on port 8080
      const baseUrl = `http://${backendHost}:${backendPort}`;
      
      // Call the home API endpoint
      const response = await fetch(`${baseUrl}/api/home`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('Home command sent successfully');
        // Don't set homingInProgress to false here, it will be set by the WebSocket event
      } else {
        console.error('Failed to send home command');
        setHomingInProgress(false); // Reset state in case of error
      }
    } catch (error) {
      console.error('Error homing robot:', error);
      setHomingInProgress(false); // Reset state in case of error
    }
  };
  
  return (
    <div className="jog-control">
      <div className="control-header">
        <h2>Machine Movement {pendantConnected && <span className="pendant-connected">(Pendant Connected)</span>}</h2>
        <div className="control-selector">
          <div className="mode-selector">
            <button 
              className={`mode-button ${mode === 'joint' ? 'active' : ''}`}
              onClick={() => setMode('joint')}
            >
              Joint
            </button>
            <button 
              className={`mode-button ${mode === 'cartesian' ? 'active' : ''}`}
              onClick={() => setMode('cartesian')}
            >
              Cartesian
            </button>
          </div>
          <div className="control-mode-selector">
            <button 
              className={`control-mode-button ${controlMode === 'keyboard' ? 'active' : ''}`}
              onClick={() => setControlMode('keyboard')}
            >
              Keyboard
            </button>
            <button 
              className={`control-mode-button ${controlMode === 'pendant' ? 'active' : ''}`}
              onClick={() => setControlMode('pendant')}
              disabled={!pendantConnected}
            >
              Pendant
            </button>
          </div>
        </div>
      </div>
      
      {/* Add Home button in the control actions section */}
      <div className="control-actions">
        <button 
          className={`action-button home-all ${homingInProgress ? 'in-progress' : ''}`}
          onClick={handleHomeClick}
          disabled={homingInProgress}
        >
          {homingInProgress ? 'HOMING...' : 'HOME ALL'}
        </button>
      </div>
      
      <div className="velocity-control">
        <h3>Increment Size</h3>
        <div className="increment-display">
          <span className="increment-value">{incrementSize}</span>
          <span className="increment-unit">{mode === 'joint' ? 'deg' : 'mm'}</span>
        </div>
        
        <ReactSlider
          className="horizontal-slider"
          thumbClassName="slider-thumb"
          trackClassName="slider-track"
          min={0}
          max={4}
          marks
          renderMark={() => null}
          value={[0.1, 1, 5, 10, 50].indexOf(incrementSize)}
          onChange={(index) => {
            const values = [0.1, 1, 5, 10, 50];
            setIncrementSize(values[index]);
          }}
        />
        
        <div className="increment-presets">
          <button 
            className={incrementSize === 0.1 ? 'active-preset' : ''}
            onClick={() => updateIncrementSize(0.1)}
          >
            0.1
          </button>
          <button 
            className={incrementSize === 1 ? 'active-preset' : ''}
            onClick={() => updateIncrementSize(1)}
          >
            1
          </button>
          <button 
            className={incrementSize === 5 ? 'active-preset' : ''}
            onClick={() => updateIncrementSize(5)}
          >
            5
          </button>
          <button 
            className={incrementSize === 10 ? 'active-preset' : ''}
            onClick={() => updateIncrementSize(10)}
          >
            10
          </button>
          <button 
            className={incrementSize === 50 ? 'active-preset' : ''}
            onClick={() => updateIncrementSize(50)}
          >
            50
          </button>
        </div>
      </div>
      
      <div className="controls-container">
        {mode === 'joint' ? (
          <div className="joint-controls">
            <h3>Joint Controls</h3>
            <div className="joint-buttons">
              {Object.entries(joints).slice(0, 3).map(([joint, label]) => (
                <div key={joint} className="joint-control-row">
                  <span className="joint-label">{label}</span>
                  <button
                    className="jog-button negative"
                    onClick={() => jogIncrement(joint, -1)}
                  >
                    -
                  </button>
                  <button
                    className="jog-button positive"
                    onClick={() => jogIncrement(joint, 1)}
                  >
                    +
                  </button>
                </div>
              ))}
              {Object.entries(joints).slice(3).map(([joint, label]) => (
                <div key={joint} className="joint-control-row">
                  <span className="joint-label">{label}</span>
                  <button
                    className="jog-button negative"
                    onClick={() => jogIncrement(joint, -1)}
                  >
                    -
                  </button>
                  <button
                    className="jog-button positive"
                    onClick={() => jogIncrement(joint, 1)}
                  >
                    +
                  </button>
                </div>
              ))}
            </div>
            
            <div className="keyboard-controls">
              <h3>{controlMode === 'keyboard' ? 'Keyboard Shortcuts' : 'Pendant Controls'}</h3>
              {controlMode === 'keyboard' ? (
                <>
                  <p>Base: Q/A</p>
                  <p>Shoulder: W/S</p>
                  <p>Extension: E/D</p>
                  <p>Elbow: R/F</p>
                  <p>Elbow2: T/H</p>
                  <p>Mode: J (Joint) / C (Cartesian)</p>
                  <p>Switch to Pendant: G</p>
                </>
              ) : (
                <>
                  <p>Active Joint: {joints[Object.keys(joints)[activeJointIndex]]}</p>
                  <p>D-Pad Up/Down: Select Joint</p>
                  <p>Left Stick: Move Active Joint</p>
                  <p>Button X: Switch Mode</p>
                  <p>Button Y: Change Increment</p>
                  <p>Switch to Keyboard: K</p>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="cartesian-controls">
            <h3>Cartesian Controls</h3>
            <div className="cartesian-buttons">
              {Object.entries(axes).slice(0, 3).map(([axis, label]) => (
                <div key={axis} className="cartesian-control-row">
                  <span className="axis-label">{label}</span>
                  <button
                    className="jog-button negative"
                    onClick={() => jogIncrement(axis, -1)}
                  >
                    -
                  </button>
                  <button
                    className="jog-button positive"
                    onClick={() => jogIncrement(axis, 1)}
                  >
                    +
                  </button>
                </div>
              ))}
              {Object.entries(axes).slice(3).map(([axis, label]) => (
                <div key={axis} className="cartesian-control-row">
                  <span className="axis-label">{label}</span>
                  <button
                    className="jog-button negative"
                    onClick={() => jogIncrement(axis, -1)}
                  >
                    -
                  </button>
                  <button
                    className="jog-button positive"
                    onClick={() => jogIncrement(axis, 1)}
                  >
                    +
                  </button>
                </div>
              ))}
            </div>
            
            <div className="keyboard-controls">
              <h3>{controlMode === 'keyboard' ? 'Keyboard Shortcuts' : 'Pendant Controls'}</h3>
              {controlMode === 'keyboard' ? (
                <>
                  <p>X: Right/Left</p>
                  <p>Y: Up/Down</p>
                  <p>Z: PgUp/PgDn</p>
                  <p>Roll: U/J</p>
                  <p>Pitch: I/K</p>
                  <p>Yaw: O/L</p>
                  <p>Mode: J (Joint) / C (Cartesian)</p>
                  <p>Switch to Pendant: G</p>
                </>
              ) : (
                <>
                  <p>Left Stick: X/Y Movement</p>
                  <p>Right Stick Y: Z Movement</p>
                  <p>Right Stick X: Yaw Rotation</p>
                  <p>L1/R1 Shoulders: Roll -/+</p>
                  <p>L2/R2 Triggers: Pitch -/+</p>
                  <p>Button X: Switch Mode</p>
                  <p>Button Y: Change Increment</p>
                  <p>Switch to Keyboard: K</p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JogControl;
