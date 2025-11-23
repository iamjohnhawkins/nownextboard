import React, { useState, useEffect } from 'react';
import './App.css';
import ScheduleList from './components/ScheduleList';
import ScheduleEditor from './components/ScheduleEditor';

function App() {
  const [schedules, setSchedules] = useState([]);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      const response = await fetch('/api/schedules');
      const data = await response.json();
      setSchedules(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch schedules:', error);
      setLoading(false);
    }
  };

  const handleCreateSchedule = () => {
    setSelectedSchedule(null);
    setIsCreating(true);
  };

  const handleEditSchedule = (schedule) => {
    setSelectedSchedule(schedule);
    setIsCreating(true);
  };

  const handleSaveSchedule = async (schedule) => {
    try {
      if (schedule.id) {
        // Update existing
        await fetch(`/api/schedules/${schedule.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(schedule),
        });
      } else {
        // Create new
        await fetch('/api/schedules', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(schedule),
        });
      }
      fetchSchedules();
      setIsCreating(false);
      setSelectedSchedule(null);
    } catch (error) {
      console.error('Failed to save schedule:', error);
      alert('Failed to save schedule');
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      await fetch(`/api/schedules/${scheduleId}`, {
        method: 'DELETE',
      });
      fetchSchedules();
    } catch (error) {
      console.error('Failed to delete schedule:', error);
      alert('Failed to delete schedule');
    }
  };

  const handleActivateSchedule = async (scheduleId) => {
    try {
      await fetch(`/api/schedules/${scheduleId}/activate`, {
        method: 'POST',
      });
      fetchSchedules();
    } catch (error) {
      console.error('Failed to activate schedule:', error);
      alert('Failed to activate schedule');
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setSelectedSchedule(null);
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Now-Next Board</h1>
        <p>Schedule Manager</p>
      </header>

      <main className="App-main">
        {isCreating ? (
          <ScheduleEditor
            schedule={selectedSchedule}
            onSave={handleSaveSchedule}
            onCancel={handleCancel}
          />
        ) : (
          <ScheduleList
            schedules={schedules}
            onCreateSchedule={handleCreateSchedule}
            onEditSchedule={handleEditSchedule}
            onDeleteSchedule={handleDeleteSchedule}
            onActivateSchedule={handleActivateSchedule}
          />
        )}
      </main>
    </div>
  );
}

export default App;
