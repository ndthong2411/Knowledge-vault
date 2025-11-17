#!/usr/bin/env python3
"""
🍅 Knowledge Vault Pomodoro Desktop App
A beautiful standalone desktop Pomodoro timer

Features:
- Modern UI with animations
- Multiple presets
- Statistics tracking
- Session history
- System tray support
- Notifications
- Customizable themes

Run: python pomodoro_desktop.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, Menu
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pomodoro import PomodoroTimer, PomodoroState, PomodoroPresets

# Optional: Desktop notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False


class ModernPomodoroApp:
    """Modern Pomodoro Desktop Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("🍅 Pomodoro Timer - Knowledge Vault")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # Initialize timer
        self.timer = PomodoroTimer()
        self.is_running = False

        # Theme colors
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'primary': '#f38ba8',
            'secondary': '#89b4fa',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'surface': '#313244',
            'surface_alt': '#45475a',
        }

        # Apply theme
        self.setup_theme()

        # Create UI
        self.create_widgets()

        # Start update loop
        self.update_timer_display()

        # Center window
        self.center_window()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_theme(self):
        """Setup modern dark theme"""
        self.root.configure(bg=self.colors['bg'])

        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['primary'], foreground='white',
                       borderwidth=0, focuscolor='none', padding=10)
        style.map('TButton',
                 background=[('active', self.colors['secondary'])])

        style.configure('Success.TButton', background=self.colors['success'])
        style.configure('Warning.TButton', background=self.colors['warning'])

    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_frame)

        # Timer display
        self.create_timer_display(main_frame)

        # Progress bar
        self.create_progress_bar(main_frame)

        # Control buttons
        self.create_control_buttons(main_frame)

        # Task input
        self.create_task_input(main_frame)

        # Stats
        self.create_stats(main_frame)

        # Settings
        self.create_settings(main_frame)

    def create_header(self, parent):
        """Create header with status"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title = tk.Label(header_frame, text="🍅 Pomodoro Timer",
                        font=('Helvetica', 24, 'bold'),
                        bg=self.colors['bg'], fg=self.colors['primary'])
        title.pack()

        # Status
        self.status_label = tk.Label(header_frame, text="Ready to Focus",
                                     font=('Helvetica', 14),
                                     bg=self.colors['bg'], fg=self.colors['fg'])
        self.status_label.pack()

    def create_timer_display(self, parent):
        """Create large timer display"""
        timer_frame = ttk.Frame(parent)
        timer_frame.pack(fill=tk.X, pady=20)

        # Timer text
        self.timer_label = tk.Label(timer_frame, text="25:00",
                                    font=('Helvetica', 72, 'bold'),
                                    bg=self.colors['bg'], fg=self.colors['primary'])
        self.timer_label.pack()

        # Session info
        self.session_label = tk.Label(timer_frame, text="",
                                      font=('Helvetica', 12),
                                      bg=self.colors['bg'], fg=self.colors['fg'])
        self.session_label.pack()

    def create_progress_bar(self, parent):
        """Create progress bar"""
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=10)

        # Create custom progress bar
        self.progress_canvas = tk.Canvas(progress_frame, height=20,
                                        bg=self.colors['surface'],
                                        highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X)

        # Progress rectangle
        self.progress_rect = self.progress_canvas.create_rectangle(
            0, 0, 0, 20, fill=self.colors['primary'], outline=''
        )

    def create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=20)

        # Button container for centering
        btn_container = ttk.Frame(button_frame)
        btn_container.pack()

        # Start/Pause button
        self.start_btn = tk.Button(btn_container, text="▶️ Start Work",
                                   font=('Helvetica', 14, 'bold'),
                                   bg=self.colors['primary'], fg='white',
                                   bd=0, padx=20, pady=10,
                                   cursor='hand2',
                                   command=self.start_work)
        self.start_btn.grid(row=0, column=0, padx=5)

        # Break button
        self.break_btn = tk.Button(btn_container, text="☕ Break",
                                   font=('Helvetica', 14),
                                   bg=self.colors['secondary'], fg='white',
                                   bd=0, padx=20, pady=10,
                                   cursor='hand2',
                                   command=self.start_break)
        self.break_btn.grid(row=0, column=1, padx=5)

        # Stop button
        self.stop_btn = tk.Button(btn_container, text="⏹️ Stop",
                                  font=('Helvetica', 14),
                                  bg=self.colors['surface_alt'], fg='white',
                                  bd=0, padx=20, pady=10,
                                  cursor='hand2',
                                  state=tk.DISABLED,
                                  command=self.stop_timer)
        self.stop_btn.grid(row=0, column=2, padx=5)

    def create_task_input(self, parent):
        """Create task input field"""
        task_frame = ttk.Frame(parent)
        task_frame.pack(fill=tk.X, pady=10)

        label = tk.Label(task_frame, text="What are you working on?",
                        font=('Helvetica', 10),
                        bg=self.colors['bg'], fg=self.colors['fg'])
        label.pack(anchor=tk.W)

        self.task_entry = tk.Entry(task_frame,
                                   font=('Helvetica', 12),
                                   bg=self.colors['surface'],
                                   fg=self.colors['fg'],
                                   insertbackground=self.colors['fg'],
                                   bd=0,
                                   highlightthickness=1,
                                   highlightcolor=self.colors['primary'])
        self.task_entry.pack(fill=tk.X, ipady=8)

    def create_stats(self, parent):
        """Create statistics display"""
        stats_frame = tk.LabelFrame(parent, text="📊 Today's Stats",
                                   font=('Helvetica', 12, 'bold'),
                                   bg=self.colors['surface'],
                                   fg=self.colors['fg'],
                                   bd=2,
                                   relief=tk.FLAT)
        stats_frame.pack(fill=tk.X, pady=20)

        # Stats container
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.X, padx=10, pady=10)

        # Pomodoros
        self.pomodoros_label = tk.Label(stats_container, text="0 🍅",
                                       font=('Helvetica', 18, 'bold'),
                                       bg=self.colors['surface'],
                                       fg=self.colors['success'])
        self.pomodoros_label.grid(row=0, column=0, padx=20)

        # Work time
        self.time_label = tk.Label(stats_container, text="0h 0m",
                                  font=('Helvetica', 18, 'bold'),
                                  bg=self.colors['surface'],
                                  fg=self.colors['secondary'])
        self.time_label.grid(row=0, column=1, padx=20)

        # Labels
        tk.Label(stats_container, text="Completed",
                font=('Helvetica', 9),
                bg=self.colors['surface'],
                fg=self.colors['fg']).grid(row=1, column=0)

        tk.Label(stats_container, text="Work Time",
                font=('Helvetica', 9),
                bg=self.colors['surface'],
                fg=self.colors['fg']).grid(row=1, column=1)

    def create_settings(self, parent):
        """Create settings panel"""
        settings_frame = tk.LabelFrame(parent, text="⚙️ Settings",
                                      font=('Helvetica', 12, 'bold'),
                                      bg=self.colors['surface'],
                                      fg=self.colors['fg'],
                                      bd=2,
                                      relief=tk.FLAT)
        settings_frame.pack(fill=tk.X, pady=10)

        settings_container = ttk.Frame(settings_frame)
        settings_container.pack(fill=tk.X, padx=10, pady=10)

        # Preset selection
        tk.Label(settings_container, text="Preset:",
                font=('Helvetica', 10),
                bg=self.colors['surface'],
                fg=self.colors['fg']).grid(row=0, column=0, sticky=tk.W)

        self.preset_var = tk.StringVar(value="classic")
        presets = ["classic", "extended", "short"]
        preset_menu = ttk.Combobox(settings_container,
                                   textvariable=self.preset_var,
                                   values=presets,
                                   state='readonly',
                                   width=15)
        preset_menu.grid(row=0, column=1, sticky=tk.W, padx=5)
        preset_menu.bind('<<ComboboxSelected>>', self.apply_preset)

        # Apply button
        apply_btn = tk.Button(settings_container, text="Apply",
                             bg=self.colors['success'], fg='white',
                             bd=0, padx=15, pady=5,
                             cursor='hand2',
                             command=self.apply_preset)
        apply_btn.grid(row=0, column=2, padx=5)

    def start_work(self):
        """Start work session"""
        if self.timer.state == PomodoroState.IDLE:
            task = self.task_entry.get()
            self.timer.start_work_session(
                task_description=task if task else None
            )
            self.is_running = True
            self.update_button_states()
            self.status_label.config(text="🔥 Focus Time!", fg=self.colors['primary'])

        elif self.timer.state == PomodoroState.PAUSED:
            self.timer.resume()
            self.is_running = True
            self.start_btn.config(text="⏸️ Pause")

        elif self.timer.state == PomodoroState.WORKING:
            self.timer.pause()
            self.is_running = False
            self.start_btn.config(text="▶️ Resume")
            self.status_label.config(text="⏸️ Paused")

    def start_break(self):
        """Start break session"""
        if self.timer.state == PomodoroState.IDLE:
            self.timer.start_break()
            self.is_running = True
            self.update_button_states()

            if self.timer.state == PomodoroState.LONG_BREAK:
                self.status_label.config(text="🌴 Long Break", fg=self.colors['success'])
            else:
                self.status_label.config(text="☕ Short Break", fg=self.colors['secondary'])

    def stop_timer(self):
        """Stop current session"""
        if messagebox.askyesno("Stop Session", "Stop current session?"):
            self.timer.stop(completed=False)
            self.is_running = False
            self.update_button_states()
            self.status_label.config(text="Ready to Focus", fg=self.colors['fg'])
            self.update_stats()

    def update_button_states(self):
        """Update button states based on timer state"""
        if self.timer.state == PomodoroState.IDLE:
            self.start_btn.config(text="▶️ Start Work", state=tk.NORMAL)
            self.break_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        else:
            if self.timer.state == PomodoroState.PAUSED:
                self.start_btn.config(text="▶️ Resume")
            elif self.timer.state == PomodoroState.WORKING:
                self.start_btn.config(text="⏸️ Pause")
            else:
                self.start_btn.config(text="⏸️ Pause")

            self.break_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def update_timer_display(self):
        """Update timer display"""
        if self.timer.state != PomodoroState.IDLE:
            remaining = self.timer.get_remaining_time()
            formatted = self.timer.format_time(remaining)
            self.timer_label.config(text=formatted)

            # Update progress bar
            progress = self.timer.get_progress_percentage()
            canvas_width = self.progress_canvas.winfo_width()
            progress_width = (canvas_width * progress) / 100
            self.progress_canvas.coords(self.progress_rect, 0, 0, progress_width, 20)

            # Check if finished
            if self.timer.is_finished():
                self.handle_session_complete()

            # Update session info
            if self.timer.state == PomodoroState.WORKING:
                self.session_label.config(
                    text=f"Pomodoro {self.timer.sessions_completed + 1}"
                )
            elif self.timer.state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
                break_type = "Long Break" if self.timer.state == PomodoroState.LONG_BREAK else "Short Break"
                self.session_label.config(text=break_type)
        else:
            # Show default time
            self.timer_label.config(text=f"{self.timer.work_duration}:00")
            self.session_label.config(text="")
            self.progress_canvas.coords(self.progress_rect, 0, 0, 0, 20)

        # Schedule next update
        self.root.after(1000, self.update_timer_display)

    def handle_session_complete(self):
        """Handle session completion"""
        suggestion = self.timer.auto_complete_and_suggest_next()

        # Send desktop notification
        self.send_notification("🎉 Session Complete!", suggestion)

        # Also show dialog
        messagebox.showinfo("🎉 Session Complete!", suggestion)

        self.is_running = False
        self.update_button_states()
        self.update_stats()

        # Flash window
        self.flash_window()

    def send_notification(self, title, message):
        """Send desktop notification"""
        if NOTIFICATIONS_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Pomodoro Timer',
                    timeout=10
                )
            except Exception as e:
                print(f"Notification failed: {e}")

    def flash_window(self):
        """Flash window to get attention"""
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.bell()

    def update_stats(self):
        """Update statistics display"""
        stats = self.timer.get_today_stats()

        self.pomodoros_label.config(text=f"{stats['sessions_completed']} 🍅")
        hours = int(stats['total_work_minutes'] // 60)
        minutes = int(stats['total_work_minutes'] % 60)
        self.time_label.config(text=f"{hours}h {minutes}m")

    def apply_preset(self, event=None):
        """Apply selected preset"""
        if self.timer.state != PomodoroState.IDLE:
            messagebox.showwarning("Cannot Change",
                                  "Stop timer before changing settings")
            return

        preset_name = self.preset_var.get()
        self.timer = PomodoroPresets.create_timer_from_preset(preset_name)

        preset_info = PomodoroPresets.get_all_presets()[preset_name]
        messagebox.showinfo("Settings Applied",
                           f"{preset_info['name']} preset applied!\n"
                           f"Work: {preset_info['work']} min\n"
                           f"Break: {preset_info['short_break']} min")

        self.timer_label.config(text=f"{self.timer.work_duration}:00")

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def on_closing(self):
        """Handle window close"""
        if self.timer.state != PomodoroState.IDLE:
            if messagebox.askyesno("Exit", "Timer is running. Exit anyway?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()

    # Try to set icon (optional)
    try:
        # If you have an icon file
        # root.iconbitmap('pomodoro_icon.ico')
        pass
    except:
        pass

    app = ModernPomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
