"""Event queue for debouncing sync triggers."""

import asyncio
import time
from typing import Dict, Set


class EventQueue:
    """Queue for debouncing sync events per user."""

    def __init__(self, debounce_seconds: float = 5.0):
        self._debounce_seconds = debounce_seconds
        self._pending: Dict[str, float] = {}  # user_id -> last_event_time
        self._sync_callbacks = []

    def add_sync_callback(self, callback):
        """Add a callback to be called when sync is triggered."""
        self._sync_callbacks.append(callback)

    def enqueue(self, user_id: str):
        """Enqueue a sync event for a user."""
        self._pending[user_id] = time.time()

    async def process(self):
        """Process pending events, triggering sync for users whose debounce has expired."""
        now = time.time()
        users_to_sync = set()

        for user_id, last_event in self._pending.items():
            if now - last_event >= self._debounce_seconds:
                users_to_sync.add(user_id)

        # Clear processed events
        for user_id in users_to_sync:
            self._pending.pop(user_id, None)

        # Trigger sync for each user
        for user_id in users_to_sync:
            for callback in self._sync_callbacks:
                try:
                    await callback(user_id)
                except Exception as e:
                    print(f"Error in sync callback for {user_id}: {e}")

    def get_pending_users(self) -> Set[str]:
        """Get the set of users with pending sync events."""
        return set(self._pending.keys())