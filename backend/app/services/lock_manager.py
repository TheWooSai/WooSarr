"""Lock manager for concurrency control."""

import threading
from typing import Dict, Optional


class LockManager:
    """Manages locks for concurrency control."""

    def __init__(self):
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def get_lock(self, key: str) -> threading.Lock:
        """Get or create a lock for a given key."""
        with self._global_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]

    def acquire_user_lock(self, user_id: str) -> threading.Lock:
        """Acquire a lock for a specific user."""
        return self.get_lock(f"user:{user_id}")

    def acquire_global_lock(self) -> threading.Lock:
        """Acquire the global lock."""
        return self._global_lock


# Global lock manager instance
lock_manager = LockManager()