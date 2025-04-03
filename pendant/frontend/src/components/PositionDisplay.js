import React from 'react';
import './PositionDisplay.css';

const PositionDisplay = ({ jointPositions, eePosition, homingInProgress }) => {
  // Format number to 2 decimal places or show waiting indicator
  const formatNumber = (num, unit) => {
    if (homingInProgress) {
      return <span className="waiting-text">waiting...</span>;
    }
    return Number(num).toFixed(2) + unit;
  };

  return (
    <div className="position-display">
      <h2>
        Current Position 
        {homingInProgress && <span className="homing-indicator">Homing in progress</span>}
      </h2>
      
      <div className="position-tables-container">
        <div className="position-section">
          <h3>Joint Positions</h3>
          <table className="position-table">
            <tbody>
              <tr>
                <td>Base Rotation:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(jointPositions.base_rotation, '°')}
                </td>
              </tr>
              <tr>
                <td>Shoulder Rotation:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(jointPositions.shoulder_rotation, '°')}
                </td>
              </tr>
              <tr>
                <td>Prismatic Extension:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(jointPositions.prismatic_extension, ' mm')}
                </td>
              </tr>
              <tr>
                <td>Elbow Rotation:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(jointPositions.elbow_rotation, '°')}
                </td>
              </tr>
              <tr>
                <td>Elbow2 Rotation:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(jointPositions.elbow2_rotation, '°')}
                </td>
              </tr>
              {/* Removed End Effector Rotation row since the robot is RRPRR, not RRPRRR */}
            </tbody>
          </table>
        </div>
        
        <div className="position-section">
          <h3>End Effector Position</h3>
          <table className="position-table">
            <tbody>
              <tr>
                <td>X:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.x, ' mm')}
                </td>
              </tr>
              <tr>
                <td>Y:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.y, ' mm')}
                </td>
              </tr>
              <tr>
                <td>Z:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.z, ' mm')}
                </td>
              </tr>
              <tr>
                <td>Roll:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.roll, '°')}
                </td>
              </tr>
              <tr>
                <td>Pitch:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.pitch, '°')}
                </td>
              </tr>
              <tr>
                <td>Yaw:</td>
                <td className={homingInProgress ? 'waiting-cell' : ''}>
                  {formatNumber(eePosition.yaw, '°')}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PositionDisplay;
