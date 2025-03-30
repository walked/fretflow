"""
FretFlow - Interactive Guitar Fretboard Trainer
Copyright (c) 2024 Francis Setash

A modern application for learning and practicing note positions on the guitar fretboard.
Features real-time audio detection, visual feedback, and interactive learning tools.

This program is licensed under the MIT License. See the LICENSE file for details.
"""

import tkinter as tk
import random
import time
import threading
import numpy as np
import sounddevice as sd
import librosa
import queue
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (
    WINDOW_TITLE, WINDOW_SIZE, PADDING, COLORS, FONTS,
    NATURAL_NOTES, FRETBOARD, VOLUME_THRESHOLD,
    MAGNITUDE_THRESHOLD, REQUIRED_STABLE_FRAMES
)
from music_theory import MusicTheory
from ui_components import VolumeIndicator
import os

# Map of string names to natural notes and their fret locations
NATURAL_NOTES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
FRETBOARD = {
    'E': {  # Low E string
        'E': 0,
        'F': 1,
        'F#': 2,
        'G': 3,
        'G#': 4,
        'A': 5,
        'A#': 6,
        'B': 7,
        'C': 8,
        'C#': 9,
        'D': 10,
        'D#': 11,
    },
    'A': {
        'A': 0,
        'A#': 1,
        'B': 2,
        'C': 3,
        'C#': 4,
        'D': 5,
        'D#': 6,
        'E': 7,
        'F': 8,
        'F#': 9,
        'G': 10,
        'G#': 11,
    },
    'D': {
        'D': 0,
        'D#': 1,
        'E': 2,
        'F': 3,
        'F#': 4,
        'G': 5,
        'G#': 6,
        'A': 7,
        'A#': 8,
        'B': 9,
        'C': 10,
        'C#': 11,
    },
    'G': {
        'G': 0,
        'G#': 1,
        'A': 2,
        'A#': 3,
        'B': 4,
        'C': 5,
        'C#': 6,
        'D': 7,
        'D#': 8,
        'E': 9,
        'F': 10,
        'F#': 11,
    },
    'B': {
        'B': 0,
        'C': 1,
        'C#': 2,
        'D': 3,
        'D#': 4,
        'E': 5,
        'F': 6,
        'F#': 7,
        'G': 8,
        'G#': 9,
        'A': 10,
        'A#': 11,
    },
    'e': {  # High E string
        'E': 0,
        'F': 1,
        'F#': 2,
        'G': 3,
        'G#': 4,
        'A': 5,
        'A#': 6,
        'B': 7,
        'C': 8,
        'C#': 9,
        'D': 10,
        'D#': 11,
    }
}

class FretboardDiagram(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas with minimum size and pack configuration
        self.canvas = tk.Canvas(self, height=180, width=600, bg='#2b3e50')  # Increased height
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Bind resize event to redraw
        self.canvas.bind('<Configure>', self._on_resize)
        self.draw_empty_fretboard()  # Draw initial empty fretboard
    
    def _on_resize(self, event):
        if hasattr(self, 'last_root_note') and hasattr(self, 'last_root_string'):
            self.draw_fretboard(self.last_root_note, self.last_root_string)
        else:
            self.draw_empty_fretboard()
    
    def draw_empty_fretboard(self, show_all_notes=False):
        """Draw the fretboard without any notes"""
        self.canvas.delete('all')
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Draw strings (reversed order so low E is at bottom)
        string_positions = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}
        string_spacing = (height - 40) / 6  # Reduced height to leave room for circles
        fret_spacing = (width - 45) / 13  # Increased left margin for circles
        fret_start_x = 45  # Increased start position to accommodate circles
        
        # Calculate the starting Y position to center the fretboard
        start_y = 20  # Padding at top
        
        # Draw string labels first
        for string, pos in string_positions.items():
            y = start_y + (pos + 0.5) * string_spacing
            # Add string names to the left of the fretboard
            self.canvas.create_text(20, y, text=string, fill='#adb5bd', 
                                  font=('Segoe UI', 8))
        
        # Draw fret markers first (so they appear behind the strings and frets)
        marker_positions = [3, 5, 7, 9, 12]  # Traditional fret marker positions
        marker_color = '#495057'  # Subtle gray color for markers
        marker_size = 6  # Size of the marker dots
        
        for fret in marker_positions:
            x = fret_start_x + ((fret - 0.5) * fret_spacing)  # Center between frets
            if fret == 12:  # Double dot at the 12th fret
                y1 = start_y + (1.5 * string_spacing)  # Position between 2nd and 3rd strings
                y2 = start_y + (4.5 * string_spacing)  # Position between 4th and 5th strings
                self.canvas.create_oval(x-marker_size, y1-marker_size, 
                                     x+marker_size, y1+marker_size, 
                                     fill=marker_color, outline=marker_color)
                self.canvas.create_oval(x-marker_size, y2-marker_size, 
                                     x+marker_size, y2+marker_size, 
                                     fill=marker_color, outline=marker_color)
            else:  # Single dot for other positions
                y = start_y + (3 * string_spacing)  # Center between strings
                self.canvas.create_oval(x-marker_size, y-marker_size, 
                                     x+marker_size, y+marker_size, 
                                     fill=marker_color, outline=marker_color)
        
        # Draw frets
        for i in range(13):
            x = fret_start_x + (i * fret_spacing)
            self.canvas.create_line(x, start_y, x, start_y + 6 * string_spacing, 
                                  fill='#495057')  # Lighter gray for frets
            
            # Add fret numbers
            if i > 0:  # Don't show 0 for the nut
                self.canvas.create_text(x - fret_spacing/2, height - 15, 
                                      text=str(i), fill='#adb5bd', font=('Segoe UI', 8))
        
        # Draw strings
        for string, pos in string_positions.items():
            y = start_y + (pos + 0.5) * string_spacing
            self.canvas.create_line(fret_start_x, y, width - 20, y, fill='#adb5bd')  # Lighter gray for strings
            
            # If show_all_notes is enabled, draw all notes for this string
            if show_all_notes:
                for note, fret in FRETBOARD[string].items():
                    x = fret_start_x + (fret - 0.5) * fret_spacing
                    # Draw a smaller, more subtle circle for reference notes
                    self.canvas.create_oval(x-8, y-8, x+8, y+8,
                                         fill='#495057', outline='#343a40')
                    self.canvas.create_text(x, y, text=note,
                                         fill='#adb5bd', font=('Segoe UI', 8))

    def draw_fretboard(self, root_note, root_string, show_all_notes=False, show_target=True):
        self.last_root_note = root_note
        self.last_root_string = root_string
        
        # Draw the basic fretboard first
        self.draw_empty_fretboard(show_all_notes)
        
        # If we're showing all notes or not showing target, return here
        if show_all_notes or not show_target:
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        string_positions = {'e': 0, 'B': 1, 'G': 2, 'D': 3, 'A': 4, 'E': 5}  # Reversed order
        string_spacing = (height - 40) / 6  # Reduced height to leave room for circles
        fret_spacing = (width - 45) / 13  # Increased left margin for circles
        fret_start_x = 45  # Increased start position to accommodate circles
        start_y = 20  # Padding at top
        
        # Convert note names to semitones (C = 0)
        NOTE_TO_SEMITONE = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        SEMITONE_TO_NOTE = {v: k for k, v in NOTE_TO_SEMITONE.items()}
        
        # Calculate intervals
        root_semitone = NOTE_TO_SEMITONE[root_note]
        major_third_semitone = (root_semitone + 4) % 12
        perfect_fifth_semitone = (root_semitone + 7) % 12
        
        major_third = SEMITONE_TO_NOTE[major_third_semitone]
        perfect_fifth = SEMITONE_TO_NOTE[perfect_fifth_semitone]
        
        # Get the root note position
        root_string_pos = string_positions[root_string]
        root_fret = FRETBOARD[root_string][root_note]
        
        # Draw the root note
        root_y = start_y + (root_string_pos + 0.5) * string_spacing
        root_x = fret_start_x + (root_fret - 0.5) * fret_spacing  # Adjusted to center between frets
        self.canvas.create_oval(root_x-12, root_y-12, root_x+12, root_y+12, 
                              fill='#28a745', outline='#1e7e34')
        self.canvas.create_text(root_x, root_y, text=root_note, 
                              fill='white', font=('Segoe UI', 10, 'bold'))
        
        # Function to find the best position for an interval on adjacent strings
        def find_interval_position(interval_note, string):
            # Find all occurrences of the interval note on this string
            interval_positions = []
            for note, fret in FRETBOARD[string].items():
                if NOTE_TO_SEMITONE[note] == NOTE_TO_SEMITONE[interval_note]:
                    interval_positions.append(fret)
            
            if not interval_positions:
                return None
            
            # Find the position closest to the root note
            best_fret = min(interval_positions, key=lambda f: abs(f - root_fret))
            
            # If the best position is too far, try octave adjustments
            if abs(best_fret - root_fret) > 4:
                if best_fret > root_fret and best_fret - 12 >= 0:
                    best_fret -= 12
                elif best_fret < root_fret and best_fret + 12 <= 12:
                    best_fret += 12
            
            y = start_y + (string_positions[string] + 0.5) * string_spacing
            x = fret_start_x + (best_fret - 0.5) * fret_spacing
            return (best_fret, x, y)
        
        # Get adjacent strings
        all_strings = list(string_positions.keys())
        root_index = all_strings.index(root_string)
        
        possible_strings = []
        if root_index > 0:
            possible_strings.append(all_strings[root_index - 1])
        if root_index < len(all_strings) - 1:
            possible_strings.append(all_strings[root_index + 1])
        
        # Draw intervals on adjacent strings
        for string in possible_strings:
            # Try to find major third
            third_pos = find_interval_position(major_third, string)
            if third_pos:
                fret, x, y = third_pos
                self.canvas.create_oval(x-12, y-12, x+12, y+12, 
                                     fill='#17a2b8', outline='#138496')
                self.canvas.create_text(x, y, text="3", 
                                     fill='white', font=('Segoe UI', 10, 'bold'))
            
            # Try to find perfect fifth
            fifth_pos = find_interval_position(perfect_fifth, string)
            if fifth_pos:
                fret, x, y = fifth_pos
                self.canvas.create_oval(x-12, y-12, x+12, y+12, 
                                     fill='#ffc107', outline='#d39e00')
                self.canvas.create_text(x, y, text="5", 
                                     fill='black', font=('Segoe UI', 10, 'bold'))

class FretTrainer:
    def __init__(self, master):
        self.master = master
        master.title(WINDOW_TITLE)
        master.geometry(WINDOW_SIZE)
        
        # Configure modern style with dark theme
        self.style = ttk.Style()
        self.style.configure("TFrame", background=COLORS['background'])
        self.style.configure("TLabel", 
                           font=FONTS['default'],
                           background=COLORS['background'],
                           foreground=COLORS['text'])
        self.style.configure("Title.TLabel",
                           font=FONTS['title'],
                           background=COLORS['background'],
                           foreground=COLORS['text'])
        self.style.configure("Info.TLabel",
                           font=FONTS['info'],
                           background=COLORS['background'],
                           foreground=COLORS['text_secondary'])
        self.style.configure("Error.TLabel",
                           font=FONTS['info'],
                           background=COLORS['background'],
                           foreground='#dc3545')  # Bootstrap danger color
        self.style.configure("Success.TLabel",
                           font=FONTS['info'],
                           background=COLORS['background'],
                           foreground='#28a745')  # Bootstrap success color
        self.style.configure("Prompt.TLabel",
                           font=FONTS['prompt'],
                           background=COLORS['background'],
                           foreground=COLORS['text'])
        
        # Main container with padding and background
        self.main_frame = ttk.Frame(master, padding=PADDING)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add fretboard diagram at the top
        self.fretboard_diagram = FretboardDiagram(self.main_frame)
        self.fretboard_diagram.pack(fill=tk.X, expand=False, pady=(20, 30))  # Increased padding

        # Learning controls
        self.learning_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.learning_frame.pack(fill=tk.X, pady=(0, 30))  # Increased padding
        
        # Show all notes toggle
        self.show_all_notes = tk.BooleanVar(value=False)
        self.show_notes_cb = ttk.Checkbutton(self.learning_frame,
                                           text="Show All Notes",
                                           variable=self.show_all_notes,
                                           command=self.toggle_show_notes,
                                           style="Modern.TCheckbutton")
        self.show_notes_cb.pack(side=tk.LEFT, padx=10)
        
        # Difficulty selector
        self.difficulty_var = tk.StringVar(value="Natural Notes Only")
        self.difficulty_label = ttk.Label(self.learning_frame,
                                       text="Difficulty:",
                                       style="Modern.TLabel")
        self.difficulty_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.difficulty_combo = ttk.Combobox(self.learning_frame,
                                          values=["Natural Notes Only", "All Notes"],
                                          textvariable=self.difficulty_var,
                                          state="readonly",
                                          width=15)
        self.difficulty_combo.pack(side=tk.LEFT, padx=5)
        self.difficulty_combo.set("Natural Notes Only")
        
        # Hint button
        self.hint_button = ttk.Button(self.learning_frame,
                                   text="Show Hint",
                                   command=self.show_hint,
                                   style="Modern.TButton")
        self.hint_button.pack(side=tk.RIGHT, padx=10)
        self.hint_button.configure(state='disabled')  # Disabled until session starts

        # Last note info section
        self.last_note_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.last_note_frame.pack(fill=tk.X, pady=(0, 40))  # Increased padding
        
        # Create a separator line above the last note info
        ttk.Separator(self.last_note_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Last note info labels in a centered container
        note_info_container = ttk.Frame(self.last_note_frame, style="TFrame")
        note_info_container.pack(expand=True)
        
        self.last_note_label = ttk.Label(note_info_container,
                                       text="Last Note: --",
                                       style="Info.TLabel")
        self.last_note_label.pack(side=tk.LEFT, padx=20)
        
        self.last_third_label = ttk.Label(note_info_container,
                                        text="Major Third: --",
                                        style="Info.TLabel")
        self.last_third_label.pack(side=tk.LEFT, padx=20)
        
        self.last_fifth_label = ttk.Label(note_info_container,
                                        text="Perfect Fifth: --",
                                        style="Info.TLabel")
        self.last_fifth_label.pack(side=tk.LEFT, padx=20)
        
        # Create a separator line below the last note info
        ttk.Separator(self.last_note_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Challenge section
        self.challenge_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.challenge_frame.pack(fill=tk.BOTH, expand=True)  # Changed to fill both and expand

        # Create a container for the centered content and volume indicator
        content_container = ttk.Frame(self.challenge_frame, style="TFrame")
        content_container.pack(fill=tk.BOTH, expand=True)  # Changed to fill both and expand

        # Container for centered content
        centered_container = ttk.Frame(content_container, style="TFrame")
        centered_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)  # Added fill=tk.BOTH

        # Title with modern styling
        self.prompt_label = ttk.Label(centered_container, 
                                    text="Click Start to Begin", 
                                    style="Prompt.TLabel")
        self.prompt_label.pack(pady=(0, 20))  # Reduced padding

        # String selection with modern styling
        self.checkboxes_frame = ttk.Frame(centered_container, style="Modern.TFrame")
        self.checkboxes_frame.pack(pady=15)  # Reduced padding
        
        self.selected_strings = {}
        for string in ['E', 'A', 'D', 'G', 'B', 'e']:
            var = tk.BooleanVar(value=True if string in ['E', 'A'] else False)
            cb = ttk.Checkbutton(self.checkboxes_frame, 
                               text=string, 
                               variable=var,
                               style="Modern.TCheckbutton")
            cb.pack(side=tk.LEFT, padx=8)
            self.selected_strings[string] = var

        # Modern start button
        self.start_button = ttk.Button(centered_container, 
                                     text="Start Session", 
                                     command=self.start_session,
                                     style="Modern.TButton")
        self.start_button.pack(pady=15)  # Reduced padding

        # Result area with modern styling
        self.result_label = ttk.Label(centered_container, 
                                    text="", 
                                    style="Result.TLabel",
                                    wraplength=400,  # Allow text to wrap if needed
                                    justify="center")  # Center-align the text
        self.result_label.pack(pady=15, padx=20, fill=tk.X)  # Reduced padding

        # Volume indicator with modern styling
        self.volume_frame = ttk.Frame(content_container, style="TFrame")
        self.volume_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Volume indicator
        self.volume_indicator = VolumeIndicator(self.volume_frame)
        self.volume_indicator.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar with modern styling
        self.status_bar = ttk.Label(self.main_frame,
                                  text="Ready",
                                  style="Modern.TLabel",
                                  font=FONTS['status'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Initialize other variables
        self.current_note = None
        self.current_string = None
        self.previous_note = None
        self.last_successful_note = None
        self.last_successful_string = None
        self.start_time = None
        self.audio_queue = queue.Queue()
        self.volume_threshold = VOLUME_THRESHOLD
        self.magnitude_threshold = MAGNITUDE_THRESHOLD
        self.stable_note_counter = 0
        self.required_stable_frames = REQUIRED_STABLE_FRAMES

    def toggle_show_notes(self):
        """Toggle the display of all notes on the fretboard"""
        if self.show_all_notes.get():
            # When showing all notes, just show the empty fretboard with reference notes
            self.fretboard_diagram.draw_empty_fretboard(show_all_notes=True)
        else:
            # When hiding all notes, show the last successful note and its relationships
            if self.last_successful_note and self.last_successful_string:
                self.fretboard_diagram.draw_fretboard(
                    self.last_successful_note,
                    self.last_successful_string,
                    show_all_notes=False,
                    show_target=True
                )
            else:
                # If no successful note yet, just show empty fretboard
                self.fretboard_diagram.draw_empty_fretboard(show_all_notes=False)
    
    def show_hint(self):
        """Show a hint for finding the current note"""
        if not self.current_note or not self.current_string:
            return
            
        # Get the fret position of the current note
        fret = FRETBOARD[self.current_string][self.current_note]
        
        # Create hint message
        hint_message = f"Hint: {self.current_note} on the {self.current_string} string is at fret {fret}"
        
        # If it's an open string (fret 0), make it clear
        if fret == 0:
            hint_message = f"Hint: {self.current_note} is an open {self.current_string} string"
            
        # Show the hint
        self.result_label.configure(text=hint_message, style="Info.TLabel")
    
    def start_session(self):
        self.start_button.config(state=tk.DISABLED)
        self.hint_button.configure(state='normal')  # Enable hint button when session starts
        self.next_prompt()
    
    def next_prompt(self):
        # Clear the result text but keep the fretboard display from the previous note
        self.result_label.config(text="")
        self.stable_note_counter = 0
        self.hint_button.configure(state='normal')  # Enable hint button for new prompt

        enabled_strings = [s for s, v in self.selected_strings.items() if v.get()]
        if not enabled_strings:
            messagebox.showwarning("No Strings Selected", "Please select at least one string to drill.")
            self.start_button.config(state=tk.NORMAL)
            self.hint_button.configure(state='disabled')
            return

        self.current_string = random.choice(enabled_strings)

        # Choose notes based on difficulty
        if self.difficulty_var.get() == "Natural Notes Only":
            available_notes = NATURAL_NOTES
        else:
            available_notes = list(FRETBOARD[self.current_string].keys())

        new_note = random.choice(available_notes)
        while new_note == self.previous_note:
            new_note = random.choice(available_notes)
        self.current_note = new_note
        self.previous_note = new_note

        # Update the prompt for the new note
        self.prompt_label.config(text=f"Find: {self.current_note} on {self.current_string} string")
        self.start_time = time.time()
        
        # Start listening for the new note
        threading.Thread(target=self.listen_for_note, daemon=True).start()

    def listen_for_note(self):
        duration = 0.1  # Back to 0.1 seconds for better responsiveness
        samplerate = 22050
        blocksize = int(duration * samplerate)

        def callback(indata, frames, time_info, status):
            volume = np.sqrt(np.mean(indata**2))
            self.audio_queue.put((indata.copy(), volume))

        with sd.InputStream(callback=callback, channels=1, samplerate=samplerate, blocksize=blocksize):
            last_note = None
            last_volume = 0
            consecutive_silence = 0
            required_silence_frames = 2  # Back to 2 for quicker recovery
            
            while True:
                if not self.audio_queue.empty():
                    audio, volume = self.audio_queue.get()
                    self.master.after(0, self.update_volume_bar, volume)
                    
                    # Check for significant volume change
                    volume_change = abs(volume - last_volume)
                    last_volume = volume
                    
                    # If volume is too low, increment silence counter
                    if volume < self.volume_threshold:
                        consecutive_silence += 1
                        if consecutive_silence >= required_silence_frames:
                            self.stable_note_counter = 0
                            last_note = None
                    else:
                        consecutive_silence = 0
                    
                    # Only process audio if volume is above threshold and there's a significant change
                    if volume >= self.volume_threshold and volume_change > self.volume_threshold * 0.15:  # Back to 0.15 for better sensitivity
                        audio = audio.flatten()
                        frequency = self.detect_pitch(audio, samplerate)
                        note = self.freq_to_note_name(frequency)
                        
                        if note:
                            if note == self.current_note:
                                if last_note == note:
                                    self.stable_note_counter += 1
                                else:
                                    self.stable_note_counter = 1
                                last_note = note

                                if self.stable_note_counter >= self.required_stable_frames:
                                    elapsed = time.time() - self.start_time
                                    self.master.after(0, lambda: self.display_result(True, elapsed))
                                    break
                            elif note:
                                # Reset counter if wrong note is detected
                                self.stable_note_counter = 0
                                self.master.after(0, lambda: self.result_label.configure(
                                    text=f"Heard: {note} ❌", 
                                    style="Error.TLabel"
                                ))

    def update_volume_bar(self, volume):
        """Update the volume indicator with the current volume level."""
        self.volume_indicator.update(volume)

    def detect_pitch(self, y, sr):
        try:
            # Use a more robust pitch detection algorithm with adjusted parameters
            pitches, magnitudes = librosa.piptrack(
                y=y, 
                sr=sr,
                hop_length=32,  # Reduced from 64 for maximum responsiveness
                fmin=50,  # Minimum frequency (about G1)
                fmax=1000,  # Maximum frequency (about B5)
                threshold=0.05  # Keep this low for sensitivity
            )
            
            # Get the maximum magnitude and its corresponding pitch
            index = magnitudes.argmax()
            pitch = pitches[index // pitches.shape[1], index % pitches.shape[1]]
            mag = magnitudes[index // magnitudes.shape[1], index % magnitudes.shape[1]]
            
            # Only return pitch if magnitude is above threshold
            if pitch == 0 or mag < self.magnitude_threshold:
                return 0
                
            # Apply a simple moving average to smooth pitch detection
            if hasattr(self, '_last_pitches'):
                self._last_pitches.append(pitch)
                if len(self._last_pitches) > 2:  # Keep at 2 for minimal smoothing
                    self._last_pitches.pop(0)
                pitch = sum(self._last_pitches) / len(self._last_pitches)
            else:
                self._last_pitches = [pitch]
                
            return pitch
            
        except Exception as e:
            print(f"Pitch detection error: {e}")
            return 0

    def display_result(self, correct, elapsed):
        if correct:
            self.result_label.configure(text=f"Correct! ⏱️ {elapsed:.2f}s", style="Success.TLabel")
            
            # Calculate intervals for the current note
            major_third, perfect_fifth = MusicTheory.calculate_intervals(self.current_note)
            
            # Update last note info
            self.last_note_label.configure(text=f"Last Note: {self.current_note} on {self.current_string}")
            self.last_third_label.configure(text=f"Major Third: {major_third}")
            self.last_fifth_label.configure(text=f"Perfect Fifth: {perfect_fifth}")
            
            # Store the successful note and string
            self.last_successful_note = self.current_note
            self.last_successful_string = self.current_string
            
            # Show the note and its relationships on the fretboard
            self.fretboard_diagram.draw_fretboard(
                self.current_note, 
                self.current_string,
                show_all_notes=self.show_all_notes.get(),
                show_target=not self.show_all_notes.get()
            )
            
            # Schedule the next prompt after a short delay
            self.master.after(1000, self.next_prompt)

    def freq_to_note_name(self, freq):
        if freq <= 0: return None
        A4 = 440
        NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        n = int(round(12 * np.log2(freq / A4)))
        note_index = (n + 9) % 12  # Shift so A=0
        return NOTES[note_index] if 0 <= note_index < len(NOTES) else None

if __name__ == "__main__":
    # Create the main window with ttkbootstrap
    root = ttk.Window(themename="darkly")
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_SIZE)
    
    # Set the window icon
    if os.path.exists("icon.ico"):
        root.iconbitmap("icon.ico")
    
    # Create and run the application
    app = FretTrainer(root)
    root.mainloop()
