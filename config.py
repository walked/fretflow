"""Configuration constants for the Fretboard Trainer application."""

# Music theory constants
NATURAL_NOTES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
A4_FREQUENCY = 440

# Note to semitone mapping (C = 0)
NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
SEMITONE_TO_NOTE = {v: k for k, v in NOTE_TO_SEMITONE.items()}

# Fretboard mapping
FRETBOARD = {
    'E': {  # Low E string
        'E': 0, 'F': 1, 'F#': 2, 'G': 3, 'G#': 4, 'A': 5,
        'A#': 6, 'B': 7, 'C': 8, 'C#': 9, 'D': 10, 'D#': 11,
    },
    'A': {
        'A': 0, 'A#': 1, 'B': 2, 'C': 3, 'C#': 4, 'D': 5,
        'D#': 6, 'E': 7, 'F': 8, 'F#': 9, 'G': 10, 'G#': 11,
    },
    'D': {
        'D': 0, 'D#': 1, 'E': 2, 'F': 3, 'F#': 4, 'G': 5,
        'G#': 6, 'A': 7, 'A#': 8, 'B': 9, 'C': 10, 'C#': 11,
    },
    'G': {
        'G': 0, 'G#': 1, 'A': 2, 'A#': 3, 'B': 4, 'C': 5,
        'C#': 6, 'D': 7, 'D#': 8, 'E': 9, 'F': 10, 'F#': 11,
    },
    'B': {
        'B': 0, 'C': 1, 'C#': 2, 'D': 3, 'D#': 4, 'E': 5,
        'F': 6, 'F#': 7, 'G': 8, 'G#': 9, 'A': 10, 'A#': 11,
    },
    'e': {  # High E string
        'E': 0, 'F': 1, 'F#': 2, 'G': 3, 'G#': 4, 'A': 5,
        'A#': 6, 'B': 7, 'C': 8, 'C#': 9, 'D': 10, 'D#': 11,
    }
}

# Audio processing constants
VOLUME_THRESHOLD = 0.02
MAGNITUDE_THRESHOLD = 0.1
REQUIRED_STABLE_FRAMES = 3
SAMPLE_RATE = 22050
BLOCK_SIZE = int(0.5 * SAMPLE_RATE)  # 0.5 seconds per block

# UI constants
WINDOW_TITLE = "FretFlow - Fretboard Trainer"
WINDOW_SIZE = "900x700"
PADDING = "10"

# Colors
COLORS = {
    'background': '#2b3e50',
    'text': 'white',
    'text_secondary': '#adb5bd',
    'fret': '#495057',
    'marker': '#495057',
    'root_note': '#28a745',
    'root_note_outline': '#1e7e34',
    'third_note': '#17a2b8',
    'third_note_outline': '#138496',
    'fifth_note': '#ffc107',
    'fifth_note_outline': '#d39e00',
}

# Fonts
FONTS = {
    'default': ('Segoe UI', 12),
    'title': ('Segoe UI', 32, 'bold'),
    'info': ('Segoe UI', 14),
    'prompt': ('Segoe UI', 24, 'bold'),
    'status': ('Segoe UI', 10),
} 