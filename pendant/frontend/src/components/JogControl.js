import React, { useState, useEffect } from 'react';
import ReactSlider from 'react-slider';
import './JogControl.css';

const JogControl = ({ sendWebSocketMessage }) => {
  const [mode, setMode] = useState('joint'); // 'joint' or 'cartesian'
  const [incrementSize, setIncrementSize] = useState(5); // Default increment size
  
  const joints = {
    base_rotation: 'Base',
    shoulder_rotation: 'Shoulder',
    prismatic_extension: 'Extension',
    elbow_rotation: 'Elbow',
    elbow2_rotation: 'Elbow2',
    end_effector_rotation: 'End Effector'
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
          'g': { joint: 'elbow2_rotation', direction: -1 },
          'y': { joint: 'end_effector_rotation', direction: 1 },
          'h': { joint: 'end_effector_rotation', direction: -1 },
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
  const jogIncrement = (input, direction) => {
    const jogData = {
      type: 'jog_increment',
      mode: mode,
      direction: direction,
      increment: incrementSize
    };
    
    // Use 'joint' parameter for joint mode, 'axis' parameter for cartesian mode
    if (mode === 'joint') {
      jogData.joint = input;
    } else { // cartesian mode
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
  
  return (
    <div className="jog-control">
      <div className="control-header">
        <h2>Machine Movement</h2>
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
              <h3>Keyboard Shortcuts</h3>
              <p>Base: Q/A</p>
              <p>Shoulder: W/S</p>
              <p>Extension: E/D</p>
              <p>Elbow: R/F</p>
              <p>Elbow2: T/G</p>
              <p>End Effector: Y/H</p>
              <p>Mode: J (Joint)</p>
              <p>Mode: C (Cartesian)</p>
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
              <h3>Keyboard Shortcuts</h3>
              <p>X: Right/Left</p>
              <p>Y: Up/Down</p>
              <p>Z: PgUp/PgDn</p>
              <p>Roll: U/J</p>
              <p>Pitch: I/K</p>
              <p>Yaw: O/L</p>
              <p>Mode: J (Joint)</p>
              <p>Mode: C (Cartesian)</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JogControl;
