import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import JogControl from './components/JogControl';
import PositionDisplay from './components/PositionDisplay';
import ProgramEditor from './components/ProgramEditor';
import './App.css';

const App = () => {
  const [jointPositions, setJointPositions] = useState({
    base_rotation: 0,
    shoulder_rotation: 0,
    prismatic_extension: 0,
    elbow_rotation: 0,
    elbow2_rotation: 0,
    end_effector_rotation: 0
  });
  
  const [eePosition, setEePosition] = useState({
    x: 0,
    y: 0,
    z: 0,
    roll: 0,
    pitch: 0,
    yaw: 0
  });
  
  const [websocket, setWebsocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('control'); // 'control' or 'programming'

  // Create a singleton WebSocket to prevent duplicate connections
  const [wsInstance] = useState(() => {
    // This runs only once during the component's initial render
    return {
      socket: null,
      reconnectAttempts: 0,
      maxReconnectAttempts: 5,
      reconnectTimer: null
    };
  });

  // Initialize WebSocket connection
  useEffect(() => {
    // Skip if we already have an active connection
    if (wsInstance.socket && 
        (wsInstance.socket.readyState === WebSocket.OPEN || 
         wsInstance.socket.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket already connected or connecting');
      return;
    }
    
    const connectWebSocket = () => {
      // When running in Docker, we need to connect to the backend service
      const backendHost = window.location.hostname;
      const backendPort = '8080'; // Backend runs on port 8080
      const wsUrl = `ws://${backendHost}:${backendPort}/ws`;
      
      console.log('Connecting to WebSocket at:', wsUrl);
      return new WebSocket(wsUrl);
    };
    
    // Close any existing connection first
    if (wsInstance.socket) {
      try {
        wsInstance.socket.close();
      } catch (e) {
        console.error('Error closing previous WebSocket:', e);
      }
    }
    
    let ws = connectWebSocket();
    wsInstance.socket = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected successfully');
      setConnected(true);
      setError(null);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received WebSocket message:', data);
      if (data.type === 'position_update') {
        console.log('Updating positions:', data.joint_positions, data.ee_position);
        setJointPositions(data.joint_positions);
        setEePosition(data.ee_position);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Failed to connect to the robot control server');
      setConnected(false);
    };
    
    ws.onclose = (event) => {
      console.log('WebSocket disconnected, code:', event.code);
      setConnected(false);
      
      // Attempt to reconnect if not closed cleanly and not at max attempts
      if (event.code !== 1000 && wsInstance.reconnectAttempts < wsInstance.maxReconnectAttempts) {
        wsInstance.reconnectAttempts++;
        console.log(`Attempting to reconnect (${wsInstance.reconnectAttempts}/${wsInstance.maxReconnectAttempts})...`);
        
        // Exponential backoff for reconnection (1s, 2s, 4s, 8s, 16s)
        const timeout = Math.pow(2, wsInstance.reconnectAttempts - 1) * 1000;
        
        wsInstance.reconnectTimer = setTimeout(() => {
          const newWs = connectWebSocket();
          wsInstance.socket = newWs;
          setWebsocket(newWs);
        }, timeout);
      } else if (wsInstance.reconnectAttempts >= wsInstance.maxReconnectAttempts) {
        setError('Maximum reconnection attempts reached. Please refresh the page.');
      }
    };
    
    setWebsocket(ws);
    
    // Clean up the WebSocket connection when the component unmounts
    return () => {
      // We don't close the socket on cleanup as it might be needed for the next render
      // Instead, we just clear any pending reconnect timers
      if (wsInstance.reconnectTimer) {
        clearTimeout(wsInstance.reconnectTimer);
        wsInstance.reconnectTimer = null;
      }
    };
  }, []);

  // Fetch initial positions from the API
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const backendHost = window.location.hostname;
        const backendPort = '8080';
        const baseUrl = `http://${backendHost}:${backendPort}`;
        
        const [jointRes, eeRes] = await Promise.all([
          axios.get(`${baseUrl}/api/joint_positions`),
          axios.get(`${baseUrl}/api/ee_position`)
        ]);
        
        setJointPositions(jointRes.data);
        setEePosition(eeRes.data);
      } catch (error) {
        console.error('Error fetching positions:', error);
        setError('Failed to fetch robot positions');
      }
    };
    
    fetchPositions();
  }, []);

  // Handle emergency stop
  const handleEmergencyStop = async () => {
    try {
      const backendHost = window.location.hostname;
      const backendPort = '8080';
      const baseUrl = `http://${backendHost}:${backendPort}`;
      
      await axios.post(`${baseUrl}/api/emergency_stop`);
      console.log('Emergency stop activated');
    } catch (error) {
      console.error('Error activating emergency stop:', error);
      setError('Failed to activate emergency stop');
    }
  };

  // Send a message through the WebSocket
  const sendWebSocketMessage = useCallback((message) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      setError('WebSocket is not connected');
    }
  }, [websocket]);

  return (
    <div className="pendant-ui">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo">WorkBee</div>
        <nav className="sidebar-nav">
          <div 
            className={`nav-item ${activeTab === 'control' ? 'active' : ''}`}
            onClick={() => setActiveTab('control')}
          >
            <i className="fas fa-gamepad"></i>
            <span>Control</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'programming' ? 'active' : ''}`}
            onClick={() => setActiveTab('programming')}
          >
            <i className="fas fa-code"></i>
            <span>Jobs</span>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="status-badge">
            <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <h2 className="page-title">
            {activeTab === 'control' ? 'Robot Control' : 'Robot Programming'}
          </h2>
          <button 
            className="emergency-stop-button" 
            onClick={handleEmergencyStop}
          >
            EMERGENCY STOP
          </button>
        </header>

        {/* Error message */}
        {error && (
          <div className="error-banner">
            <i className="fas fa-exclamation-triangle"></i>
            <span>{error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* Content area */}
        <div className="content-area">
          {activeTab === 'control' && (
            <div className="control-section">
              <div className="position-panels">
                <div className="position-panel">
                  <h3 className="panel-title">Machine Position</h3>
                  <div className="position-values">
                    <div className="position-row">
                      <div className="position-label">X</div>
                      <div className="position-value">{eePosition.x.toFixed(3)}</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Y</div>
                      <div className="position-value">{eePosition.y.toFixed(3)}</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Z</div>
                      <div className="position-value">{eePosition.z.toFixed(3)}</div>
                    </div>
                  </div>
                </div>

                <div className="position-panel">
                  <h3 className="panel-title">Joint Positions</h3>
                  <div className="position-values">
                    <div className="position-row">
                      <div className="position-label">Base</div>
                      <div className="position-value">{jointPositions.base_rotation.toFixed(1)}°</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Shoulder</div>
                      <div className="position-value">{jointPositions.shoulder_rotation.toFixed(1)}°</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Extension</div>
                      <div className="position-value">{jointPositions.prismatic_extension.toFixed(1)}mm</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Elbow</div>
                      <div className="position-value">{jointPositions.elbow_rotation.toFixed(1)}°</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">Elbow2</div>
                      <div className="position-value">{jointPositions.elbow2_rotation.toFixed(1)}°</div>
                    </div>
                    <div className="position-row">
                      <div className="position-label">End Effector</div>
                      <div className="position-value">{jointPositions.end_effector_rotation.toFixed(1)}°</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="jog-control-container">
                <JogControl 
                  sendWebSocketMessage={sendWebSocketMessage}
                />
              </div>
            </div>
          )}

          {activeTab === 'programming' && (
            <div className="programming-section">
              <ProgramEditor 
                websocket={websocket}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
