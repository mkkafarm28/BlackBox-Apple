import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserSession:
    """Represents a user session with authentication state"""
    telegram_user_id: int
    username: Optional[str] = None
    is_authenticated: bool = False
    awaiting_password: bool = False
    awaiting_2fa: bool = False
    temp_username: Optional[str] = None
    temp_password: Optional[str] = None
    last_activity: str = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()


class UserSessionManager:
    """Manages user sessions for the Telegram bot"""
    
    def __init__(self, session_file: str = "user_sessions.json"):
        self.session_file = Path(session_file)
        self.sessions: Dict[int, UserSession] = {}
        self.lock = asyncio.Lock()
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    for user_id_str, session_data in data.items():
                        user_id = int(user_id_str)
                        self.sessions[user_id] = UserSession(**session_data)
            except Exception as e:
                print(f"Error loading sessions: {e}")
    
    async def _save_sessions(self):
        """Save sessions to file"""
        async with self.lock:
            try:
                data = {
                    str(user_id): asdict(session)
                    for user_id, session in self.sessions.items()
                }
                with open(self.session_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error saving sessions: {e}")
    
    async def get_session(self, telegram_user_id: int) -> UserSession:
        """Get or create a user session"""
        if telegram_user_id not in self.sessions:
            self.sessions[telegram_user_id] = UserSession(telegram_user_id=telegram_user_id)
            await self._save_sessions()
        return self.sessions[telegram_user_id]
    
    async def update_session(self, telegram_user_id: int, **kwargs):
        """Update a user session"""
        session = await self.get_session(telegram_user_id)
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.last_activity = datetime.now().isoformat()
        await self._save_sessions()
    
    async def clear_session(self, telegram_user_id: int):
        """Clear a user session (logout)"""
        if telegram_user_id in self.sessions:
            self.sessions[telegram_user_id] = UserSession(telegram_user_id=telegram_user_id)
            await self._save_sessions()
    
    async def is_authenticated(self, telegram_user_id: int) -> bool:
        """Check if user is authenticated"""
        session = await self.get_session(telegram_user_id)
        return session.is_authenticated
    
    async def set_authenticated(self, telegram_user_id: int, username: str):
        """Mark user as authenticated"""
        await self.update_session(
            telegram_user_id,
            username=username,
            is_authenticated=True,
            awaiting_password=False,
            awaiting_2fa=False,
            temp_username=None,
            temp_password=None
        )
    
    async def start_login(self, telegram_user_id: int, username: str):
        """Start login process"""
        await self.update_session(
            telegram_user_id,
            temp_username=username,
            awaiting_password=True,
            awaiting_2fa=False
        )
    
    async def set_password(self, telegram_user_id: int, password: str):
        """Set password and prepare for 2FA if needed"""
        await self.update_session(
            telegram_user_id,
            temp_password=password,
            awaiting_password=False
        )
    
    async def set_awaiting_2fa(self, telegram_user_id: int):
        """Mark user as awaiting 2FA code"""
        await self.update_session(
            telegram_user_id,
            awaiting_2fa=True
        )
