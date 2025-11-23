"""Data models for schedule management."""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Activity:
    """Represents a single activity in the schedule."""
    id: str
    name: str
    start_time: str  # HH:MM format
    duration_minutes: int
    color: str  # Hex color code
    icon: Optional[str] = None  # Icon name or emoji
    background_image: Optional[str] = None  # URL or path to background image

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """Create from dictionary."""
        # Handle activities that don't have background_image field
        if 'background_image' not in data:
            data['background_image'] = None
        return cls(**data)

    def get_end_time(self) -> time:
        """Calculate end time based on start time and duration."""
        from datetime import datetime, timedelta
        start = datetime.strptime(self.start_time, "%H:%M")
        end = start + timedelta(minutes=self.duration_minutes)
        return end.time()


@dataclass
class Schedule:
    """Represents a daily schedule."""
    id: str
    name: str
    activities: List[Activity]
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'activities': [a.to_dict() for a in self.activities],
            'active': self.active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """Create from dictionary."""
        activities = [Activity.from_dict(a) for a in data['activities']]
        return cls(
            id=data['id'],
            name=data['name'],
            activities=activities,
            active=data.get('active', True)
        )


class ScheduleStore:
    """Handles persistence of schedules to JSON file."""

    def __init__(self, data_path: str = "data/schedules.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create the data file if it doesn't exist."""
        if not self.data_path.exists():
            self.data_path.write_text(json.dumps([], indent=2))

    def load_schedules(self) -> List[Schedule]:
        """Load all schedules from file."""
        try:
            data = json.loads(self.data_path.read_text())
            return [Schedule.from_dict(s) for s in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_schedules(self, schedules: List[Schedule]):
        """Save all schedules to file."""
        data = [s.to_dict() for s in schedules]
        self.data_path.write_text(json.dumps(data, indent=2))

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a specific schedule by ID."""
        schedules = self.load_schedules()
        for schedule in schedules:
            if schedule.id == schedule_id:
                return schedule
        return None

    def get_active_schedule(self) -> Optional[Schedule]:
        """Get the currently active schedule."""
        schedules = self.load_schedules()
        for schedule in schedules:
            if schedule.active:
                return schedule
        return None

    def add_schedule(self, schedule: Schedule):
        """Add a new schedule."""
        schedules = self.load_schedules()
        schedules.append(schedule)
        self.save_schedules(schedules)

    def update_schedule(self, schedule: Schedule):
        """Update an existing schedule."""
        schedules = self.load_schedules()
        for i, s in enumerate(schedules):
            if s.id == schedule.id:
                schedules[i] = schedule
                break
        self.save_schedules(schedules)

    def delete_schedule(self, schedule_id: str):
        """Delete a schedule."""
        schedules = self.load_schedules()
        schedules = [s for s in schedules if s.id != schedule_id]
        self.save_schedules(schedules)

    def set_active_schedule(self, schedule_id: str):
        """Set a schedule as active (and deactivate others)."""
        schedules = self.load_schedules()
        for schedule in schedules:
            schedule.active = (schedule.id == schedule_id)
        self.save_schedules(schedules)
