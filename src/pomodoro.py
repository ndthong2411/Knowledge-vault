"""
Pomodoro Timer for Knowledge Vault
Helps users stay focused while working on notes
"""
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class PomodoroState(Enum):
    """Pomodoro timer states"""
    IDLE = "idle"
    WORKING = "working"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"


@dataclass
class PomodoroSession:
    """A single pomodoro session"""
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    session_type: PomodoroState
    note_id: Optional[int] = None
    task_description: Optional[str] = None
    completed: bool = False


class PomodoroTimer:
    """
    Pomodoro Timer implementation

    Default settings:
    - Work session: 25 minutes
    - Short break: 5 minutes
    - Long break: 15 minutes
    - Long break after: 4 pomodoros
    """

    def __init__(self,
                 work_duration: int = 25,
                 short_break: int = 5,
                 long_break: int = 15,
                 sessions_until_long_break: int = 4):
        """
        Initialize Pomodoro Timer

        Args:
            work_duration: Work session length in minutes
            short_break: Short break length in minutes
            long_break: Long break length in minutes
            sessions_until_long_break: Number of work sessions before long break
        """
        self.work_duration = work_duration
        self.short_break = short_break
        self.long_break = long_break
        self.sessions_until_long_break = sessions_until_long_break

        # Current state
        self.state = PomodoroState.IDLE
        self.current_session: Optional[PomodoroSession] = None
        self.sessions_completed = 0
        self.total_work_time = 0  # in minutes

        # History
        self.session_history: List[PomodoroSession] = []

        # Timer tracking
        self.start_time: Optional[datetime] = None
        self.pause_time: Optional[datetime] = None
        self.remaining_seconds: Optional[int] = None

    def start_work_session(self, note_id: Optional[int] = None,
                          task_description: Optional[str] = None):
        """Start a work session"""
        if self.state != PomodoroState.IDLE:
            raise ValueError("Cannot start new session while timer is running")

        self.state = PomodoroState.WORKING
        self.start_time = datetime.now()

        self.current_session = PomodoroSession(
            start_time=self.start_time,
            end_time=None,
            duration_minutes=self.work_duration,
            session_type=PomodoroState.WORKING,
            note_id=note_id,
            task_description=task_description,
            completed=False
        )

        self.remaining_seconds = self.work_duration * 60

    def start_break(self):
        """Start a break session (short or long based on sessions completed)"""
        if self.state != PomodoroState.IDLE:
            raise ValueError("Cannot start break while timer is running")

        # Determine break type
        if self.sessions_completed % self.sessions_until_long_break == 0 and self.sessions_completed > 0:
            self.state = PomodoroState.LONG_BREAK
            duration = self.long_break
        else:
            self.state = PomodoroState.SHORT_BREAK
            duration = self.short_break

        self.start_time = datetime.now()

        self.current_session = PomodoroSession(
            start_time=self.start_time,
            end_time=None,
            duration_minutes=duration,
            session_type=self.state,
            completed=False
        )

        self.remaining_seconds = duration * 60

    def pause(self):
        """Pause the current session"""
        if self.state not in [PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            raise ValueError("Cannot pause when not running")

        self.pause_time = datetime.now()
        self.state = PomodoroState.PAUSED

    def resume(self):
        """Resume from pause"""
        if self.state != PomodoroState.PAUSED:
            raise ValueError("Cannot resume when not paused")

        if self.pause_time and self.start_time:
            # Adjust start time to account for pause duration
            pause_duration = datetime.now() - self.pause_time
            self.start_time += pause_duration

        # Restore previous state
        if self.current_session:
            self.state = self.current_session.session_type

        self.pause_time = None

    def stop(self, completed: bool = True):
        """Stop the current session"""
        if self.state == PomodoroState.IDLE:
            return

        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.completed = completed

            # Add to history
            self.session_history.append(self.current_session)

            # Update stats if work session completed
            if completed and self.current_session.session_type == PomodoroState.WORKING:
                self.sessions_completed += 1
                self.total_work_time += self.current_session.duration_minutes

        # Reset state
        self.state = PomodoroState.IDLE
        self.current_session = None
        self.start_time = None
        self.pause_time = None
        self.remaining_seconds = None

    def get_remaining_time(self) -> int:
        """Get remaining seconds in current session"""
        if self.state == PomodoroState.IDLE:
            return 0

        if self.state == PomodoroState.PAUSED:
            return self.remaining_seconds or 0

        if not self.start_time or not self.current_session:
            return 0

        elapsed = (datetime.now() - self.start_time).total_seconds()
        total_seconds = self.current_session.duration_minutes * 60
        remaining = int(total_seconds - elapsed)

        return max(0, remaining)

    def is_finished(self) -> bool:
        """Check if current session is finished"""
        if self.state == PomodoroState.IDLE:
            return False

        return self.get_remaining_time() <= 0

    def auto_complete_and_suggest_next(self) -> str:
        """
        Auto-complete current session and suggest next action
        Returns suggestion message
        """
        if not self.is_finished():
            return "Session not finished yet"

        if self.state == PomodoroState.WORKING:
            self.stop(completed=True)

            # Check if long break
            if self.sessions_completed % self.sessions_until_long_break == 0:
                return f"🎉 Great work! You completed {self.sessions_completed} pomodoros. Time for a {self.long_break}-minute long break!"
            else:
                return f"✅ Pomodoro completed! Take a {self.short_break}-minute break."

        elif self.state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            self.stop(completed=True)
            return "🍅 Break finished! Ready for another pomodoro?"

        return "Session complete!"

    def get_progress_percentage(self) -> float:
        """Get progress percentage of current session"""
        if self.state == PomodoroState.IDLE or not self.current_session:
            return 0.0

        total_seconds = self.current_session.duration_minutes * 60
        remaining = self.get_remaining_time()
        elapsed = total_seconds - remaining

        return min(100.0, (elapsed / total_seconds) * 100)

    def format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def get_today_stats(self) -> Dict:
        """Get statistics for today"""
        today = datetime.now().date()

        today_sessions = [
            s for s in self.session_history
            if s.start_time.date() == today and s.session_type == PomodoroState.WORKING
        ]

        completed = len([s for s in today_sessions if s.completed])
        total_minutes = sum(s.duration_minutes for s in today_sessions if s.completed)

        return {
            'date': today.isoformat(),
            'sessions_completed': completed,
            'total_work_minutes': total_minutes,
            'total_work_hours': round(total_minutes / 60, 1),
            'current_streak': self.sessions_completed
        }

    def get_week_stats(self) -> List[Dict]:
        """Get statistics for the past 7 days"""
        today = datetime.now().date()
        week_stats = []

        for i in range(7):
            day = today - timedelta(days=i)

            day_sessions = [
                s for s in self.session_history
                if s.start_time.date() == day and
                   s.session_type == PomodoroState.WORKING and
                   s.completed
            ]

            week_stats.append({
                'date': day.isoformat(),
                'day_name': day.strftime('%A'),
                'sessions': len(day_sessions),
                'minutes': sum(s.duration_minutes for s in day_sessions)
            })

        return list(reversed(week_stats))

    def export_session_history(self) -> str:
        """Export session history as markdown"""
        lines = ["# Pomodoro Session History\n"]

        for session in self.session_history:
            status = "✅" if session.completed else "❌"
            session_type = session.session_type.value

            lines.append(f"## {status} {session_type.title()}")
            lines.append(f"- Start: {session.start_time.strftime('%Y-%m-%d %H:%M')}")
            if session.end_time:
                lines.append(f"- End: {session.end_time.strftime('%Y-%m-%d %H:%M')}")
            lines.append(f"- Duration: {session.duration_minutes} minutes")

            if session.task_description:
                lines.append(f"- Task: {session.task_description}")

            if session.note_id:
                lines.append(f"- Note ID: {session.note_id}")

            lines.append("")

        return "\n".join(lines)


class PomodoroPresets:
    """Pre-configured pomodoro timer settings"""

    CLASSIC = {
        'name': 'Classic Pomodoro',
        'work': 25,
        'short_break': 5,
        'long_break': 15,
        'sessions': 4
    }

    EXTENDED = {
        'name': 'Extended Focus',
        'work': 50,
        'short_break': 10,
        'long_break': 30,
        'sessions': 3
    }

    SHORT = {
        'name': 'Quick Sessions',
        'work': 15,
        'short_break': 3,
        'long_break': 10,
        'sessions': 4
    }

    CUSTOM = {
        'name': 'Custom',
        'work': 25,
        'short_break': 5,
        'long_break': 15,
        'sessions': 4
    }

    @classmethod
    def get_all_presets(cls) -> Dict[str, Dict]:
        """Get all preset configurations"""
        return {
            'classic': cls.CLASSIC,
            'extended': cls.EXTENDED,
            'short': cls.SHORT,
            'custom': cls.CUSTOM
        }

    @classmethod
    def create_timer_from_preset(cls, preset_name: str) -> PomodoroTimer:
        """Create a timer from preset"""
        presets = cls.get_all_presets()
        preset = presets.get(preset_name.lower(), cls.CLASSIC)

        return PomodoroTimer(
            work_duration=preset['work'],
            short_break=preset['short_break'],
            long_break=preset['long_break'],
            sessions_until_long_break=preset['sessions']
        )
