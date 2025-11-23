"""Flask backend API for Now-Next Board."""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import uuid
import os

from models import Schedule, Activity, ScheduleStore

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

# Initialize schedule store
store = ScheduleStore()


def get_current_and_next_activities() -> Tuple[Optional[Activity], Optional[Activity], Optional[Dict[str, Any]]]:
    """Get the current and next activities based on current time."""
    schedule = store.get_active_schedule()
    if not schedule:
        return None, None, None

    now = datetime.now().time()
    current_activity = None
    next_activity = None
    time_info = None

    # Sort activities by start time
    sorted_activities = sorted(schedule.activities,
                              key=lambda a: datetime.strptime(a.start_time, "%H:%M").time())

    for i, activity in enumerate(sorted_activities):
        start = datetime.strptime(activity.start_time, "%H:%M").time()
        end = activity.get_end_time()

        # Check if current activity
        if start <= now < end:
            current_activity = activity
            # Get next activity if exists
            if i + 1 < len(sorted_activities):
                next_activity = sorted_activities[i + 1]

            # Calculate time remaining
            now_dt = datetime.combine(datetime.today(), now)
            end_dt = datetime.combine(datetime.today(), end)
            if end_dt < now_dt:  # Activity spans midnight
                end_dt += timedelta(days=1)

            total_seconds = activity.duration_minutes * 60
            elapsed_dt = now_dt - datetime.combine(datetime.today(), start)
            elapsed_seconds = elapsed_dt.total_seconds()
            remaining_seconds = total_seconds - elapsed_seconds

            time_info = {
                'elapsed_seconds': int(elapsed_seconds),
                'remaining_seconds': int(remaining_seconds),
                'total_seconds': total_seconds,
                'progress_percent': (elapsed_seconds / total_seconds) * 100 if total_seconds > 0 else 0
            }
            break

    # If no current activity found, find the next upcoming one
    if not current_activity:
        for activity in sorted_activities:
            start = datetime.strptime(activity.start_time, "%H:%M").time()
            if start > now:
                next_activity = activity
                break

    return current_activity, next_activity, time_info


# API Routes

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules."""
    schedules = store.load_schedules()
    return jsonify([s.to_dict() for s in schedules])


@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create a new schedule."""
    data = request.json

    schedule = Schedule(
        id=str(uuid.uuid4()),
        name=data['name'],
        activities=[Activity.from_dict(a) for a in data['activities']],
        active=data.get('active', False)
    )

    store.add_schedule(schedule)
    return jsonify(schedule.to_dict()), 201


@app.route('/api/schedules/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Get a specific schedule."""
    schedule = store.get_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    return jsonify(schedule.to_dict())


@app.route('/api/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update a schedule."""
    data = request.json

    schedule = Schedule(
        id=schedule_id,
        name=data['name'],
        activities=[Activity.from_dict(a) for a in data['activities']],
        active=data.get('active', False)
    )

    store.update_schedule(schedule)
    return jsonify(schedule.to_dict())


@app.route('/api/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a schedule."""
    store.delete_schedule(schedule_id)
    return '', 204


@app.route('/api/schedules/<schedule_id>/activate', methods=['POST'])
def activate_schedule(schedule_id):
    """Set a schedule as active."""
    store.set_active_schedule(schedule_id)
    return jsonify({'success': True})


@app.route('/api/current', methods=['GET'])
def get_current():
    """Get current and next activities."""
    current, next_act, time_info = get_current_and_next_activities()

    return jsonify({
        'current': current.to_dict() if current else None,
        'next': next_act.to_dict() if next_act else None,
        'time_info': time_info
    })


# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
