"""Music theory calculations and utilities for the Fretboard Trainer."""

import numpy as np
import librosa
from typing import Optional, Tuple, List
from config import (
    NOTES, NOTE_TO_SEMITONE, SEMITONE_TO_NOTE,
    A4_FREQUENCY, MAGNITUDE_THRESHOLD
)

class MusicTheory:
    @staticmethod
    def freq_to_note_name(freq: float) -> Optional[str]:
        """Convert a frequency to its corresponding note name.
        
        Args:
            freq: The frequency in Hz
            
        Returns:
            The note name (e.g., 'C', 'F#') or None if frequency is invalid
        """
        if freq <= 0:
            return None
            
        n = int(round(12 * np.log2(freq / A4_FREQUENCY)))
        note_index = (n + 9) % 12  # Shift so A=0
        return NOTES[note_index] if 0 <= note_index < len(NOTES) else None

    @staticmethod
    def detect_pitch(y: np.ndarray, sr: int) -> float:
        """Detect the fundamental frequency of an audio signal.
        
        Args:
            y: The audio signal
            sr: The sample rate
            
        Returns:
            The detected frequency in Hz, or 0 if no pitch detected
        """
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            index = magnitudes.argmax()
            pitch = pitches[index // pitches.shape[1], index % pitches.shape[1]]
            mag = magnitudes[index // pitches.shape[1], index % pitches.shape[1]]
            if pitch == 0 or mag < MAGNITUDE_THRESHOLD:
                return 0
            return pitch
        except Exception:
            return 0

    @staticmethod
    def calculate_intervals(root_note: str) -> Tuple[str, str]:
        """Calculate the major third and perfect fifth for a given root note.
        
        Args:
            root_note: The root note (e.g., 'C', 'F#')
            
        Returns:
            Tuple of (major_third, perfect_fifth) note names
        """
        root_semitone = NOTE_TO_SEMITONE[root_note]
        major_third_semitone = (root_semitone + 4) % 12
        perfect_fifth_semitone = (root_semitone + 7) % 12
        
        return (
            SEMITONE_TO_NOTE[major_third_semitone],
            SEMITONE_TO_NOTE[perfect_fifth_semitone]
        )

    @staticmethod
    def get_note_positions(note: str, string: str) -> List[int]:
        """Get all fret positions for a given note on a string.
        
        Args:
            note: The note to find (e.g., 'C', 'F#')
            string: The string to search on (e.g., 'E', 'A')
            
        Returns:
            List of fret positions where the note appears
        """
        from config import FRETBOARD
        return [fret for n, fret in FRETBOARD[string].items() 
                if NOTE_TO_SEMITONE[n] == NOTE_TO_SEMITONE[note]]

    @staticmethod
    def find_best_position(note: str, string: str, reference_fret: int) -> Optional[int]:
        """Find the best fret position for a note relative to a reference position.
        
        Args:
            note: The note to find
            string: The string to search on
            reference_fret: The reference fret position
            
        Returns:
            The best fret position or None if not found
        """
        positions = MusicTheory.get_note_positions(note, string)
        if not positions:
            return None
            
        best_fret = min(positions, key=lambda f: abs(f - reference_fret))
        
        # Try octave adjustments if position is too far
        if abs(best_fret - reference_fret) > 4:
            if best_fret > reference_fret and best_fret - 12 >= 0:
                best_fret -= 12
            elif best_fret < reference_fret and best_fret + 12 <= 12:
                best_fret += 12
                
        return best_fret 