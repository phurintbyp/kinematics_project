import React, { useState, useEffect, useRef } from 'react';
import ReactSlider from 'react-slider';
import './JogControl.css';

const JogControl = ({ sendWebSocketMessage }) => {
  const [mode, setMode] = useState('joint'); // 'joint' or 'cartesian'
  const [incrementSize, setIncrementSize] = useState(5); // Default increment size
  const [gamepadConnected, setGamepadConnected] = useState(false);
  const [activeJointIndex, setActiveJointIndex] = useState(0); // For gamepad joint selection
  const [controlMode, setControlMode] = useState('keyboard'); // 'keyboard' or 'gamepad'
  
  // References to track gamepad state
  const gamepadRef = useRef(null);
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
      if (e.key === 'g') setControlMode('gamepad');
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
          'g': { joint: 'elbow2_rotation', direction: -1 }
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

  // Gamepad detection and handling
  useEffect(() => {
    const detectGamepad = () => {
      const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
      for (let i = 0; i < gamepads.length; i++) {
        if (gamepads[i]) {
          gamepadRef.current = gamepads[i];
          setGamepadConnected(true);
          setControlMode('gamepad');
          console.log('Gamepad connected:', gamepads[i].id);
          return;
        }
      }
      gamepadRef.current = null;
      setGamepadConnected(false);
    };

    const handleGamepadConnected = (e) => {
      console.log(`Gamepad connected at index ${e.gamepad.index}: ${e.gamepad.id}`);
      gamepadRef.current = e.gamepad;
      setGamepadConnected(true);
      setControlMode('gamepad');
    };

    const handleGamepadDisconnected = (e) => {
      console.log(`Gamepad disconnected at index ${e.gamepad.index}: ${e.gamepad.id}`);
      gamepadRef.current = null;
      setGamepadConnected(false);
      setControlMode('keyboard');
    };

    window.addEventListener('gamepadconnected', handleGamepadConnected);
    window.addEventListener('gamepaddisconnected', handleGamepadDisconnected);

    // Initial detection
    detectGamepad();

    return () => {
      window.removeEventListener('gamepadconnected', handleGamepadConnected);
      window.removeEventListener('gamepaddisconnected', handleGamepadDisconnected);
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, []);

  // Gamepad polling
  useEffect(() => {
    if (!gamepadConnected || controlMode !== 'gamepad') {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = null;
      }
      return;
    }

    const jointKeys = Object.keys(joints);
    
    const pollGamepad = () => {
      const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
      const gamepad = gamepads[gamepadRef.current?.index || 0];
      
      if (!gamepad) {
        requestRef.current = requestAnimationFrame(pollGamepad);
        return;
      }

      // Initialize previous buttons state if it doesn't exist
      if (!previousButtonsRef.current) {
        previousButtonsRef.current = gamepad.buttons.map(b => b.pressed);
      }

      // D-pad for joint selection in joint mode
      if (gamepad.buttons[12].pressed && !previousButtonsRef.current[12]) { // D-pad Up
        if (mode === 'joint') {
          setActiveJointIndex(prev => (prev > 0 ? prev - 1 : 0));
        }
      }
      if (gamepad.buttons[13].pressed && !previousButtonsRef.current[13]) { // D-pad Down
        if (mode === 'joint') {
          setActiveJointIndex(prev => (prev < jointKeys.length - 1 ? prev + 1 : jointKeys.length - 1));
        }
      }

      // Mode switching (Button X - typically button 2)
      if (gamepad.buttons[2].pressed && !previousButtonsRef.current[2]) {
        setMode(prev => prev === 'joint' ? 'cartesian' : 'joint');
      }

      // Increment size switching (Button Y - typically button the 3)
      if (gamepad.buttons[3].pressed && !previousButtonsRef.current[3]) {
        const standardIncrements = [0.1, 1, 5, 10, 50];
        const currentIndex = standardIncrements.indexOf(incrementSize);
        const nextIndex = (currentIndex + 1) % standardIncrements.length;
        setIncrementSize(standardIncrements[nextIndex]);
      }

      // Joint controls using joysticks
      if (mode === 'joint') {
        // Left joystick Y-axis for active joint control
        const leftYAxis = -gamepad.axes[1];
        const intensity = (Math.abs(leftYAxis) - joystickDeadzone) / (1 - joystickDeadzone);
        if (Math.abs(leftYAxis) > joystickDeadzone) {
          const activeJoint = jointKeys[activeJointIndex];
          const intensity = (Math.abs(leftYAxis) - joystickDeadzone) / (1 - joystickDeadzone);
          jogIncrement(activeJoint, Math.sign(leftYAxis), intensity);
        }        
      } else { // Cartesian mode
        // Left joystick for X/Y movement
        const leftXAxis = gamepad.axes[0];
        const leftYAxis = -gamepad.axes[1]; // Invert so that up is positive
        
        if (Math.abs(leftXAxis) > joystickDeadzone) {
          jogIncrement('x', Math.sign(leftXAxis));
        }
        
        if (Math.abs(leftYAxis) > joystickDeadzone) {
          jogIncrement('y', Math.sign(leftYAxis));
        }
        
        // Right joystick for Z and rotation
        const rightXAxis = gamepad.axes[2]; 
        const rightYAxis = -gamepad.axes[3]; // Invert so that up is positive
        
        if (Math.abs(rightYAxis) > joystickDeadzone) {
          jogIncrement('z', Math.sign(rightYAxis));
        }
        
        if (Math.abs(rightXAxis) > joystickDeadzone) {
          jogIncrement('yaw', Math.sign(rightXAxis));
        }
        
        // Shoulder buttons for roll/pitch
        if (gamepad.buttons[4].pressed) { // Left shoulder
          jogIncrement('roll', -1);
        }
        if (gamepad.buttons[5].pressed) { // Right shoulder
          jogIncrement('roll', 1);
        }
        if (gamepad.buttons[6].pressed) { // Left trigger as button
          jogIncrement('pitch', -1);
        }
        if (gamepad.buttons[7].pressed) { // Right trigger as button
          jogIncrement('pitch', 1);
        }
      }

      // Update previous buttons state
      previousButtonsRef.current = gamepad.buttons.map(b => b.pressed);

      // Continue polling
      requestRef.current = requestAnimationFrame(pollGamepad);
    };

    requestRef.current = requestAnimationFrame(pollGamepad);

    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [gamepadConnected, controlMode, mode, incrementSize, activeJointIndex, sendWebSocketMessage]);
  
  return (
    <div className="jog-control">
      <div className="control-header">
        <h2>Machine Movement {gamepadConnected && <span className="gamepad-connected">(Gamepad Connected)</span>}</h2>
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
              className={`control-mode-button ${controlMode === 'gamepad' ? 'active' : ''}`}
              onClick={() => setControlMode('gamepad')}
              disabled={!gamepadConnected}
            >
              Gamepad
            </button>
          </div>
        </div>
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
              <h3>{controlMode === 'keyboard' ? 'Keyboard Shortcuts' : 'Gamepad Controls'}</h3>
              {controlMode === 'keyboard' ? (
                <>
                  <p>Base: Q/A</p>
                  <p>Shoulder: W/S</p>
                  <p>Extension: E/D</p>
                  <p>Elbow: R/F</p>
                  <p>Elbow2: T/G</p>
                  <p>Mode: J (Joint) / C (Cartesian)</p>
                  <p>Switch to Gamepad: G</p>
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
              <h3>{controlMode === 'keyboard' ? 'Keyboard Shortcuts' : 'Gamepad Controls'}</h3>
              {controlMode === 'keyboard' ? (
                <>
                  <p>X: Right/Left</p>
                  <p>Y: Up/Down</p>
                  <p>Z: PgUp/PgDn</p>
                  <p>Roll: U/J</p>
                  <p>Pitch: I/K</p>
                  <p>Yaw: O/L</p>
                  <p>Mode: J (Joint) / C (Cartesian)</p>
                  <p>Switch to Gamepad: G</p>
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
