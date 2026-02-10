"""
Session Management

Manages focused reading sessions with timer functionality.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import uuid


@dataclass
class Session:
    """Represents a focused reading session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platforms: List[str] = field(default_factory=list)
    duration: int = 30  # minutes
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    posts_read: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    is_focus_mode: bool = False
    is_active: bool = True
    
    def get_elapsed_minutes(self) -> int:
        """Get elapsed time since session start in minutes."""
        if not self.start_time:
            return 0
        elapsed = datetime.now(timezone.utc) - self.start_time
        return int(elapsed.total_seconds() / 60)
    
    def get_time_remaining(self) -> int:
        """Get remaining time in minutes."""
        if not self.start_time:
            return self.duration
        elapsed = self.get_elapsed_minutes()
        return max(0, self.duration - elapsed)
    
    def get_progress_percentage(self) -> float:
        """Get session progress as a percentage."""
        if self.duration == 0:
            return 100.0
        elapsed = self.get_elapsed_minutes()
        return min(100.0, (elapsed / self.duration) * 100)
    
    def add_post(self, post_id: str) -> None:
        """Add a post to the session."""
        if post_id not in self.posts_read:
            self.posts_read.append(post_id)
    
    def add_note(self, note: str) -> None:
        """Add a note to the session."""
        self.notes.append(note)
    
    def end(self) -> None:
        """End the session."""
        self.end_time = datetime.now(timezone.utc)
        self.is_active = False
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "platforms": self.platforms,
            "duration": self.duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "posts_read": self.posts_read,
            "notes": self.notes,
            "is_focus_mode": self.is_focus_mode,
            "is_active": self.is_active,
            "elapsed_minutes": self.get_elapsed_minutes(),
            "time_remaining": self.get_time_remaining(),
            "progress_percentage": self.get_progress_percentage()
        }


class SessionManager:
    """Manages focused reading sessions."""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.current_session: Optional[Session] = None
        self.session_history: List[Session] = []
        self._session_task: Optional[asyncio.Task] = None
    
    async def start_session(
        self,
        platforms: List[str],
        duration: int,
        is_focus_mode: bool = False
    ) -> Session:
        """
        Start a new reading session.
        
        Args:
            platforms: List of platform names to include
            duration: Session duration in minutes
            is_focus_mode: Whether this is a distraction-free focus session
        
        Returns:
            The created session
        """
        # End any existing session
        if self.current_session and self.current_session.is_active:
            await self.end_session()
        
        session = Session(
            platforms=platforms,
            duration=duration,
            start_time=datetime.now(timezone.utc),
            is_focus_mode=is_focus_mode
        )
        
        self.current_session = session
        
        # Start background task for session tracking
        self._session_task = asyncio.create_task(self._track_session(session))
        
        return session
    
    async def start_focus_session(self, duration: int = 30) -> Session:
        """
        Start a distraction-free focus session.
        
        Args:
            duration: Session duration in minutes
        
        Returns:
            The created focus session
        """
        # Get all enabled platforms
        platforms = self.config.platforms.get_enabled_platforms()
        
        return await self.start_session(platforms, duration, is_focus_mode=True)
    
    async def end_session(self) -> Optional[Session]:
        """
        End the current session.
        
        Returns:
            The ended session or None if no active session
        """
        if not self.current_session:
            return None
        
        # Cancel tracking task
        if self._session_task:
            self._session_task.cancel()
            try:
                await self._session_task
            except asyncio.CancelledError:
                pass
        
        # End session
        self.current_session.end()
        
        # Add to history
        self.session_history.append(self.current_session)
        
        ended_session = self.current_session
        self.current_session = None
        
        return ended_session
    
    async def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        return self.current_session
    
    async def add_post_to_session(self, post_id: str) -> None:
        """Add a post to the current session."""
        if self.current_session:
            self.current_session.add_post(post_id)
    
    async def add_note_to_session(self, note: str) -> None:
        """Add a note to the current session."""
        if self.current_session:
            self.current_session.add_note(note)
    
    def get_session_history(self, limit: int = 10) -> List[Session]:
        """Get recent session history."""
        return self.session_history[-limit:]
    
    async def _track_session(self, session: Session) -> None:
        """Background task to track session progress."""
        try:
            while session.is_active and session.get_time_remaining() > 0:
                await asyncio.sleep(60)  # Check every minute
                
                # Session will auto-end when time is up
                if session.get_time_remaining() <= 0:
                    session.end()
                    
        except asyncio.CancelledError:
            pass
    
    async def pause_session(self) -> None:
        """Pause the current session."""
        if self.current_session:
            self.current_session.is_active = False
    
    async def resume_session(self) -> None:
        """Resume a paused session."""
        if self.current_session:
            self.current_session.is_active = True
            self._session_task = asyncio.create_task(
                self._track_session(self.current_session)
            )
    
    def get_statistics(self) -> Dict:
        """Get session statistics."""
        if not self.session_history:
            return {
                "total_sessions": 0,
                "total_time_minutes": 0,
                "total_posts_read": 0,
                "average_session_length": 0,
                "focus_mode_sessions": 0
            }
        
        total_time = sum(s.get_elapsed_minutes() for s in self.session_history)
        total_posts = sum(len(s.posts_read) for s in self.session_history)
        focus_sessions = sum(1 for s in self.session_history if s.is_focus_mode)
        
        return {
            "total_sessions": len(self.session_history),
            "total_time_minutes": total_time,
            "total_posts_read": total_posts,
            "average_session_length": total_time // len(self.session_history) if self.session_history else 0,
            "focus_mode_sessions": focus_sessions
        }


# Forward reference
from socialai.config import Config
