"""State management for the Fretboard Trainer application."""

from typing import List, Optional, Dict
from dataclasses import dataclass
from config import NATURAL_NOTES, FRETBOARD

@dataclass
class TrainingState:
    """Represents the current state of the training session."""
    
    # Current challenge state
    current_note: Optional[str] = None
    current_string: Optional[str] = None
    previous_note: Optional[str] = None
    start_time: Optional[float] = None
    
    # Performance tracking
    times: List[float] = None
    stable_note_counter: int = 0
    
    # Settings
    show_all_notes: bool = False
    difficulty: str = "Natural Notes Only"
    selected_strings: Dict[str, bool] = None
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.times is None:
            self.times = []
        if self.selected_strings is None:
            self.selected_strings = {
                'E': True, 'A': True, 'D': False,
                'G': False, 'B': False, 'e': False
            }
    
    def get_enabled_strings(self) -> List[str]:
        """Get list of currently enabled strings."""
        return [s for s, v in self.selected_strings.items() if v]
    
    def get_available_notes(self) -> List[str]:
        """Get list of available notes based on current difficulty."""
        if not self.current_string:
            return []
            
        if self.difficulty == "Natural Notes Only":
            return NATURAL_NOTES
        return list(FRETBOARD[self.current_string].keys())
    
    def reset_challenge(self):
        """Reset the current challenge state."""
        self.current_note = None
        self.current_string = None
        self.previous_note = None
        self.start_time = None
        self.stable_note_counter = 0
    
    def start_challenge(self, note: str, string: str):
        """Start a new challenge with the given note and string."""
        self.current_note = note
        self.current_string = string
        self.previous_note = note
        self.start_time = None
        self.stable_note_counter = 0
    
    def record_time(self, elapsed: float):
        """Record the time taken for the current challenge."""
        self.times.append(elapsed)
    
    def get_average_time(self) -> float:
        """Calculate the average time taken for challenges."""
        if not self.times:
            return 0.0
        return sum(self.times) / len(self.times)
    
    def increment_stable_counter(self):
        """Increment the counter for stable note detection."""
        self.stable_note_counter += 1
    
    def reset_stable_counter(self):
        """Reset the counter for stable note detection."""
        self.stable_note_counter = 0
    
    def is_stable(self, required_frames: int) -> bool:
        """Check if the note has been stable for enough frames."""
        return self.stable_note_counter >= required_frames 