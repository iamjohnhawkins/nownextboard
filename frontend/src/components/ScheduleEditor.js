import React, { useState } from 'react';
import './ScheduleEditor.css';

function ScheduleEditor({ schedule, onSave, onCancel }) {
  const [name, setName] = useState(schedule?.name || '');
  const [activities, setActivities] = useState(schedule?.activities || []);

  const handleAddActivity = () => {
    const newActivity = {
      id: `activity-${Date.now()}`,
      name: '',
      start_time: '08:00',
      duration_minutes: 30,
      color: '#667eea',
      icon: '📌',
    };
    setActivities([...activities, newActivity]);
  };

  const handleUpdateActivity = (index, field, value) => {
    const updated = [...activities];
    updated[index] = { ...updated[index], [field]: value };
    setActivities(updated);
  };

  const handleDeleteActivity = (index) => {
    setActivities(activities.filter((_, i) => i !== index));
  };

  const handleMoveActivity = (index, direction) => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === activities.length - 1)
    ) {
      return;
    }

    const newActivities = [...activities];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newActivities[index], newActivities[targetIndex]] = [
      newActivities[targetIndex],
      newActivities[index],
    ];
    setActivities(newActivities);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!name.trim()) {
      alert('Please enter a schedule name');
      return;
    }

    if (activities.length === 0) {
      alert('Please add at least one activity');
      return;
    }

    // Validate activities
    for (const activity of activities) {
      if (!activity.name.trim()) {
        alert('Please fill in all activity names');
        return;
      }
    }

    const scheduleData = {
      id: schedule?.id,
      name: name.trim(),
      activities,
      active: schedule?.active || false,
    };

    onSave(scheduleData);
  };

  return (
    <div className="schedule-editor">
      <div className="editor-header">
        <h2>{schedule ? 'Edit Schedule' : 'Create Schedule'}</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Schedule Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Weekday Morning Routine"
            required
          />
        </div>

        <div className="activities-section">
          <div className="activities-header">
            <h3>Activities</h3>
            <button type="button" onClick={handleAddActivity}>
              Add Activity
            </button>
          </div>

          {activities.length === 0 ? (
            <div className="no-activities">
              <p>No activities yet. Click "Add Activity" to get started.</p>
            </div>
          ) : (
            <div className="activities-list">
              {activities.map((activity, index) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-order">
                    <button
                      type="button"
                      onClick={() => handleMoveActivity(index, 'up')}
                      disabled={index === 0}
                    >
                      ▲
                    </button>
                    <span>{index + 1}</span>
                    <button
                      type="button"
                      onClick={() => handleMoveActivity(index, 'down')}
                      disabled={index === activities.length - 1}
                    >
                      ▼
                    </button>
                  </div>

                  <div className="activity-fields">
                    <div className="form-row">
                      <div className="form-group flex-2">
                        <label>Activity Name</label>
                        <input
                          type="text"
                          value={activity.name}
                          onChange={(e) =>
                            handleUpdateActivity(index, 'name', e.target.value)
                          }
                          placeholder="e.g., Breakfast"
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label>Icon/Emoji</label>
                        <input
                          type="text"
                          value={activity.icon || ''}
                          onChange={(e) =>
                            handleUpdateActivity(index, 'icon', e.target.value)
                          }
                          placeholder="📌"
                          maxLength="4"
                        />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>Start Time</label>
                        <input
                          type="time"
                          value={activity.start_time}
                          onChange={(e) =>
                            handleUpdateActivity(index, 'start_time', e.target.value)
                          }
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label>Duration (minutes)</label>
                        <input
                          type="number"
                          value={activity.duration_minutes}
                          onChange={(e) =>
                            handleUpdateActivity(
                              index,
                              'duration_minutes',
                              parseInt(e.target.value)
                            )
                          }
                          min="1"
                          max="480"
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label>Color</label>
                        <input
                          type="color"
                          value={activity.color}
                          onChange={(e) =>
                            handleUpdateActivity(index, 'color', e.target.value)
                          }
                        />
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="delete-activity danger"
                    onClick={() => handleDeleteActivity(index)}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit">Save Schedule</button>
        </div>
      </form>
    </div>
  );
}

export default ScheduleEditor;
