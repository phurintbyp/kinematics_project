import React from 'react';
import './PositionDisplay.css';

const PositionDisplay = ({ jointPositions, eePosition }) => {
  // Format number to 2 decimal places
  const formatNumber = (num) => {
    return Number(num).toFixed(2);
  };

  return (
    <div className="position-display">
      <h2>Current Position</h2>
      
      <div className="position-section">
        <h3>Joint Positions</h3>
        <table className="position-table">
          <tbody>
            <tr>
              <td>Base Rotation:</td>
              <td>{formatNumber(jointPositions.base_rotation)}°</td>
            </tr>
            <tr>
              <td>Shoulder Rotation:</td>
              <td>{formatNumber(jointPositions.shoulder_rotation)}°</td>
            </tr>
            <tr>
              <td>Prismatic Extension:</td>
              <td>{formatNumber(jointPositions.prismatic_extension)} mm</td>
            </tr>
            <tr>
              <td>Elbow Rotation:</td>
              <td>{formatNumber(jointPositions.elbow_rotation)}°</td>
            </tr>
            <tr>
              <td>Elbow2 Rotation:</td>
              <td>{formatNumber(jointPositions.elbow2_rotation)}°</td>
            </tr>
            <tr>
              <td>End Effector Rotation:</td>
              <td>{formatNumber(jointPositions.end_effector_rotation)}°</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div className="position-section">
        <h3>End Effector Position</h3>
        <table className="position-table">
          <tbody>
            <tr>
              <td>X:</td>
              <td>{formatNumber(eePosition.x)} mm</td>
            </tr>
            <tr>
              <td>Y:</td>
              <td>{formatNumber(eePosition.y)} mm</td>
            </tr>
            <tr>
              <td>Z:</td>
              <td>{formatNumber(eePosition.z)} mm</td>
            </tr>
            <tr>
              <td>Roll:</td>
              <td>{formatNumber(eePosition.roll)}°</td>
            </tr>
            <tr>
              <td>Pitch:</td>
              <td>{formatNumber(eePosition.pitch)}°</td>
            </tr>
            <tr>
              <td>Yaw:</td>
              <td>{formatNumber(eePosition.yaw)}°</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PositionDisplay;
