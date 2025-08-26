"""
Rate limiting utility for API endpoints.
"""
import time
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    A simple rate limiter that tracks requests per user.
    
    This implementation uses a sliding window algorithm to track requests
    and enforce rate limits per user.
    """
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        # Store request timestamps per user
        self.user_requests: Dict[int, Deque[float]] = defaultdict(deque)
        self.lock = None  # Would use a proper lock in production
        
    def allow_request(self, user_id: int) -> bool:
        """
        Check if a user is allowed to make a request.
        
        Args:
            user_id: The ID of the user making the request
            
        Returns:
            bool: True if the request is allowed, False if rate limited
        """
        current_time = time.time()
        
        # Clean up old requests (outside the time window)
        while (self.user_requests[user_id] and 
               current_time - self.user_requests[user_id][0] > self.time_window):
            self.user_requests[user_id].popleft()
        
        # Check if under rate limit
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(current_time)
            return True
            
        return False
    
    def get_retry_after(self, user_id: int) -> int:
        """
        Get the number of seconds until the next request is allowed.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            int: Number of seconds until the next request is allowed
        """
        current_time = time.time()
        
        # Clean up old requests
        while (self.user_requests[user_id] and 
               current_time - self.user_requests[user_id][0] > self.time_window):
            self.user_requests[user_id].popleft()
        
        if not self.user_requests[user_id]:
            return 0
            
        # Calculate time until the oldest request falls out of the window
        oldest_request = self.user_requests[user_id][0]
        time_elapsed = current_time - oldest_request
        retry_after = max(0, self.time_window - time_elapsed + 1)  # Add 1s buffer
        
        return int(retry_after)
    
    def get_remaining_requests(self, user_id: int) -> int:
        """
        Get the number of remaining requests for a user in the current time window.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            int: Number of remaining requests
        """
        current_time = time.time()
        
        # Clean up old requests
        while (self.user_requests[user_id] and 
               current_time - self.user_requests[user_id][0] > self.time_window):
            self.user_requests[user_id].popleft()
            
        return max(0, self.max_requests - len(self.user_requests[user_id]))
    
    def reset(self, user_id: Optional[int] = None):
        """
        Reset the rate limiter for a specific user or all users.
        
        Args:
            user_id: Optional user ID to reset. If None, resets all users.
        """
        if user_id is not None:
            if user_id in self.user_requests:
                self.user_requests[user_id].clear()
        else:
            self.user_requests.clear()
