"""UI components for the Fretboard Trainer application."""

import tkinter as tk
import ttkbootstrap as ttk
from typing import Optional, Callable
from config import COLORS, FONTS

class BaseComponent(ttk.Frame):
    """Base class for all UI components."""
    
    def __init__(self, parent: ttk.Frame, **kwargs):
        """Initialize the base component.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments to pass to the Frame
        """
        super().__init__(parent, **kwargs)
        self.style = ttk.Style()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup component-specific styles."""
        pass
    
    def update(self, *args, **kwargs):
        """Update the component's state and appearance."""
        pass

class LearningControls(BaseComponent):
    """Controls for learning settings."""
    
    def __init__(self, parent: ttk.Frame, on_difficulty_change: Callable[[str], None],
                 on_show_notes_change: Callable[[bool], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_difficulty_change = on_difficulty_change
        self.on_show_notes_change = on_show_notes_change
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the control widgets."""
        # Show all notes toggle
        self.show_all_notes = tk.BooleanVar(value=False)
        self.show_notes_cb = ttk.Checkbutton(
            self,
            text="Show All Notes",
            variable=self.show_all_notes,
            command=lambda: self.on_show_notes_change(self.show_all_notes.get())
        )
        self.show_notes_cb.pack(side=tk.LEFT, padx=10)
        
        # Difficulty selector
        self.difficulty_var = tk.StringVar(value="Natural Notes Only")
        ttk.Label(self, text="Difficulty:", style="Modern.TLabel").pack(
            side=tk.LEFT, padx=(20, 5)
        )
        
        self.difficulty_combo = ttk.Combobox(
            self,
            values=["Natural Notes Only", "All Notes"],
            textvariable=self.difficulty_var,
            state="readonly",
            width=15
        )
        self.difficulty_combo.pack(side=tk.LEFT, padx=5)
        self.difficulty_combo.bind('<<ComboboxSelected>>', 
                                 lambda e: self.on_difficulty_change(self.difficulty_var.get()))

class NoteInfoDisplay(BaseComponent):
    """Display for note information."""
    
    def __init__(self, parent: ttk.Frame, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the info display widgets."""
        # Create a separator line
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Info container
        note_info_container = ttk.Frame(self, style="TFrame")
        note_info_container.pack(expand=True)
        
        # Info labels
        self.last_note_label = ttk.Label(
            note_info_container,
            text="Last Note: --",
            style="Info.TLabel"
        )
        self.last_note_label.pack(side=tk.LEFT, padx=20)
        
        self.last_third_label = ttk.Label(
            note_info_container,
            text="Major Third: --",
            style="Info.TLabel"
        )
        self.last_third_label.pack(side=tk.LEFT, padx=20)
        
        self.last_fifth_label = ttk.Label(
            note_info_container,
            text="Perfect Fifth: --",
            style="Info.TLabel"
        )
        self.last_fifth_label.pack(side=tk.LEFT, padx=20)
        
        # Bottom separator
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, pady=5)
    
    def update(self, note: str, string: str, major_third: str, perfect_fifth: str):
        """Update the displayed note information."""
        self.last_note_label.configure(text=f"Last Note: {note} on {string}")
        self.last_third_label.configure(text=f"Major Third: {major_third}")
        self.last_fifth_label.configure(text=f"Perfect Fifth: {perfect_fifth}")

class VolumeIndicator(BaseComponent):
    """Volume level indicator."""
    
    def __init__(self, parent: ttk.Frame, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the volume indicator widgets."""
        # Container for vertical layout
        container = ttk.Frame(self, style="TFrame")
        container.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Audio icon (using a simple text symbol)
        self.icon_label = ttk.Label(
            container,
            text="🔊",
            style="Modern.TLabel",
            font=("Segoe UI", 12)
        )
        self.icon_label.pack(side=tk.TOP, pady=(5, 0))
        
        # Vertical progress bar
        self.volume_bar = ttk.Progressbar(
            container,
            length=100,  # Height of the bar
            mode='determinate',
            orient='vertical',
            style="Modern.Vertical.TProgressbar"
        )
        self.volume_bar.pack(side=tk.TOP, pady=5, fill=tk.Y)
    
    def update(self, volume: float):
        """Update the volume bar value."""
        self.volume_bar['value'] = min(volume * 100, 100)

class StatusBar(BaseComponent):
    """Status bar for displaying application state."""
    
    def __init__(self, parent: ttk.Frame, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the status bar widget."""
        self.status_label = ttk.Label(
            self,
            text="Ready",
            style="Modern.TLabel",
            font=FONTS['status']
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    def update(self, message: str):
        """Update the status message."""
        self.status_label.configure(text=message) 