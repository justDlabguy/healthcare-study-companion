from datetime import datetime, timedelta
from typing import Tuple

def calculate_next_review(
    ease_factor: float,
    interval: int,
    review_quality: int,
    review_count: int
) -> Tuple[float, int, datetime]:
    """
    Calculate the next review parameters using the SM-2 spaced repetition algorithm.
    
    Args:
        ease_factor: Current ease factor (default: 2.5)
        interval: Current interval in days
        review_quality: Quality of the review (0-5)
        review_count: Number of times the card has been reviewed
        
    Returns:
        Tuple containing (new_ease_factor, new_interval, next_review_date)
    """
    # Clamp review quality to 0-5 range
    review_quality = max(0, min(5, review_quality))
    
    if review_quality >= 3:  # Correct response
        if review_count == 0:
            interval = 1
        elif review_count == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)
        
        # Update ease factor based on response quality (SM-2 formula)
        ease_factor = ease_factor + (0.1 - (5 - review_quality) * (0.08 + (5 - review_quality) * 0.02))
    else:  # Incorrect response
        interval = 1
        # Reset ease factor to minimum but don't let it go below 1.3
        ease_factor = max(1.3, ease_factor - 0.2)
    
    # Clamp ease factor to minimum of 1.3 (no maximum limit in SM-2)
    ease_factor = max(1.3, ease_factor)
    
    # Calculate next review date
    next_review_date = datetime.utcnow() + timedelta(days=interval)
    
    return ease_factor, interval, next_review_date
