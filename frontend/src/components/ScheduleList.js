import React from 'react';
import './ScheduleList.css';

function ScheduleList({ schedules, onCreateSchedule, onEditSchedule, onDeleteSchedule, onActivateSchedule }) {
  return (
    <div className="schedule-list">
      <div className="schedule-list-header">
        <h2>Schedules</h2>
        <button onClick={onCreateSchedule}>Create New Schedule</button>
      </div>

      {schedules.length === 0 ? (
        <div className="empty-state">
          <p>No schedules yet. Create your first schedule to get started!</p>
        </div>
      ) : (
        <div className="schedule-cards">
          {schedules.map((schedule) => (
            <div key={schedule.id} className={`schedule-card ${schedule.active ? 'active' : ''}`}>
              <div className="schedule-card-header">
                <h3>{schedule.name}</h3>
                {schedule.active && <span className="active-badge">Active</span>}
              </div>

              <div className="schedule-card-activities">
                <p className="activity-count">
                  {schedule.activities.length} {schedule.activities.length === 1 ? 'activity' : 'activities'}
                </p>
                <div className="activity-list">
                  {schedule.activities.slice(0, 3).map((activity) => (
                    <div key={activity.id} className="activity-preview">
                      <span className="activity-icon">{activity.icon || '📌'}</span>
                      <span className="activity-name">{activity.name}</span>
                      <span className="activity-time">{activity.start_time}</span>
                    </div>
                  ))}
                  {schedule.activities.length > 3 && (
                    <p className="more-activities">+{schedule.activities.length - 3} more...</p>
                  )}
                </div>
              </div>

              <div className="schedule-card-actions">
                {!schedule.active && (
                  <button
                    className="success"
                    onClick={() => onActivateSchedule(schedule.id)}
                  >
                    Activate
                  </button>
                )}
                <button
                  className="secondary"
                  onClick={() => onEditSchedule(schedule)}
                >
                  Edit
                </button>
                <button
                  className="danger"
                  onClick={() => onDeleteSchedule(schedule.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ScheduleList;
