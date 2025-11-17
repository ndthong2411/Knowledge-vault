# 🍅 Pomodoro Desktop App - User Guide

**A beautiful standalone desktop Pomodoro timer for Knowledge Vault**

---

## ✨ Features

### Core Functionality
- ⏰ **Full Pomodoro Timer** - 25-minute work sessions with breaks
- ⏸️ **Pause/Resume** - Flexible session control
- 📊 **Statistics Tracking** - Track daily completed sessions and work time
- 🎨 **Beautiful Dark UI** - Modern Catppuccin-inspired theme
- 🔔 **Desktop Notifications** - Get notified when sessions complete
- ⚙️ **Multiple Presets** - Classic, Extended, Short work modes
- 📝 **Task Description** - Track what you're working on
- 🎯 **Session Counter** - Know which Pomodoro you're on

### Visual Design
- **Large Timer Display** - Easy-to-read 72pt timer
- **Progress Bar** - Visual progress indicator
- **Color-Coded States** - Different colors for work/break/paused
- **Responsive Buttons** - Clear, intuitive controls
- **Clean Layout** - Distraction-free interface

---

## 🚀 Installation

### Prerequisites

**Python 3.9+** with tkinter support

#### Check if tkinter is installed:
```bash
python -c "import tkinter; print('✅ tkinter is installed')"
```

#### Install tkinter if missing:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
# Usually included with Python
# If missing, reinstall Python from python.org
```

**Windows:**
```bash
# Usually included with Python
# If missing, reinstall Python from python.org
```

### Install Dependencies

```bash
# Option 1: Install desktop-specific requirements
pip install -r requirements_desktop.txt

# Option 2: Install all requirements (includes Streamlit)
pip install -r requirements.txt
```

**Required packages:**
- `plyer` - Desktop notifications
- `pillow` - Image handling
- `sentence-transformers` - For Knowledge Vault integration
- `yake` - For Knowledge Vault integration

---

## 📖 Usage

### Starting the App

```bash
# Navigate to project directory
cd Knowledge-vault

# Run the desktop app
python pomodoro_desktop.py
```

**The app window will open centered on your screen.**

---

## 🎯 How to Use

### Basic Workflow

1. **Enter Task** (optional)
   - Type what you're working on in the "What are you working on?" field
   - Example: "Write documentation", "Study Python", "Review code"

2. **Start Work Session**
   - Click "▶️ Start Work" button
   - Timer starts at 25 minutes (default)
   - Status shows "🔥 Focus Time!"
   - Progress bar fills as time passes

3. **During Work Session**
   - ⏸️ **Pause**: Click "⏸️ Pause" to pause timer
   - ▶️ **Resume**: Click "▶️ Resume" to continue
   - ⏹️ **Stop**: Click "⏹️ Stop" to cancel session

4. **Session Complete**
   - Desktop notification appears
   - Dialog shows completion message
   - Window flashes to get attention
   - Suggestion for next action (work/break)

5. **Take Break**
   - Click "☕ Break" to start break
   - Short break (5 min) after sessions 1-3
   - Long break (15 min) after 4 sessions
   - Status shows "☕ Short Break" or "🌴 Long Break"

6. **Repeat**
   - After break, start next work session
   - Cycle continues: Work → Break → Work → Break...

---

## ⚙️ Settings

### Presets

Choose from 3 built-in presets:

#### 1. **Classic** (Default)
- Work: 25 minutes
- Short break: 5 minutes
- Long break: 15 minutes
- Sessions until long break: 4
- **Best for**: Traditional Pomodoro technique

#### 2. **Extended**
- Work: 50 minutes
- Short break: 10 minutes
- Long break: 30 minutes
- Sessions until long break: 3
- **Best for**: Deep work, complex tasks

#### 3. **Short**
- Work: 15 minutes
- Short break: 3 minutes
- Long break: 10 minutes
- Sessions until long break: 4
- **Best for**: Quick tasks, beginners

### Changing Presets

1. At bottom of window, find "⚙️ Settings" panel
2. Select preset from dropdown menu
3. Click "Apply" button
4. **Note**: Must stop timer before changing settings

---

## 📊 Statistics

### Today's Stats Panel

Shows real-time statistics for current day:

- **🍅 Completed**: Number of completed Pomodoros
- **⏰ Work Time**: Total work time (hours and minutes)

### Statistics Reset

- Statistics reset at midnight
- Stored in SQLite database (`data/knowledge.db`)
- History available through Knowledge Vault app

---

## 🎨 UI Elements

### Timer Display
- **Large Numbers**: Current time remaining (MM:SS)
- **Session Info**: Current Pomodoro number or break type
- **Color Coding**:
  - 🔴 Red (Primary): Work session
  - 🔵 Blue (Secondary): Short break
  - 🟢 Green (Success): Long break

### Progress Bar
- Visual indicator of session progress
- Fills from left to right
- Color matches current state

### Control Buttons

| Button | Function | When Available |
|--------|----------|----------------|
| ▶️ Start Work | Start work session | When idle |
| ⏸️ Pause | Pause current session | During work/break |
| ▶️ Resume | Resume paused session | When paused |
| ☕ Break | Start break | When idle |
| ⏹️ Stop | Cancel session | During work/break |

### Status Messages

- "Ready to Focus" - Idle, ready to start
- "🔥 Focus Time!" - Work session active
- "⏸️ Paused" - Session paused
- "☕ Short Break" - Short break active
- "🌴 Long Break" - Long break active

---

## 🔔 Notifications

### Desktop Notifications

**Requirements:**
- `plyer` package installed (`pip install plyer`)
- System notification support enabled

**Notification Triggers:**
- ✅ Work session completed
- ✅ Break session completed
- ✅ Automatic next step suggestion

**Notification Content:**
- Title: "🎉 Session Complete!"
- Message: Suggestion for next action
- Duration: 10 seconds

**Example Messages:**
- "Great work! Time for a 5-minute break."
- "Break's over! Ready for Pomodoro 2?"
- "Awesome! You've earned a 15-minute long break!"

---

## 🎹 Keyboard Shortcuts

Currently, all controls are button-based.

**Future planned shortcuts:**
- `Space` - Start/Pause
- `S` - Stop
- `B` - Break
- `Esc` - Close/Minimize

---

## 💡 Tips for Effective Use

### Best Practices

1. **Plan Before Starting**
   - Write task description before starting
   - Break large tasks into Pomodoro-sized chunks
   - Be specific: "Write intro section" vs "Write report"

2. **Minimize Distractions**
   - Close unnecessary apps
   - Put phone on silent
   - Use "Do Not Disturb" mode

3. **Use Breaks Wisely**
   - Stand up and stretch
   - Look away from screen (20-20-20 rule)
   - Hydrate
   - Avoid screens during breaks

4. **Don't Skip Breaks**
   - Breaks are essential for productivity
   - Long breaks prevent burnout
   - Use timer for breaks too

5. **Track Your Work**
   - Check "Today's Stats" regularly
   - Celebrate completed Pomodoros
   - Aim for consistent daily goals

### Recommended Daily Goals

- **Beginner**: 4-6 Pomodoros/day
- **Intermediate**: 8-10 Pomodoros/day
- **Advanced**: 12-16 Pomodoros/day

**Note**: More isn't always better. Quality > Quantity.

---

## 🔧 Troubleshooting

### App Won't Start

**Issue**: `ModuleNotFoundError: No module named 'tkinter'`

**Solution**: Install tkinter:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS/Windows - Reinstall Python
```

**Issue**: `ModuleNotFoundError: No module named 'plyer'`

**Solution**: Install dependencies:
```bash
pip install -r requirements_desktop.txt
```

### Notifications Not Working

**Possible causes:**
1. `plyer` not installed
2. System notifications disabled
3. Running in headless environment

**Solution**:
```bash
# Install plyer
pip install plyer

# Check system notification settings
# Enable notifications for Python apps
```

**Fallback**: App still shows dialog boxes even if notifications fail.

### Timer Stops Unexpectedly

**Issue**: Timer pauses when switching windows

**Solution**: This is intentional. Use Stop button to cancel, not minimize.

### Stats Not Updating

**Issue**: Daily stats show 0

**Possible causes:**
1. Sessions not completed (stopped early)
2. Database connection issue

**Solution**:
- Complete full sessions (don't stop early)
- Check `data/knowledge.db` exists
- Restart app

---

## 🗂️ Integration with Knowledge Vault

### Linking Sessions to Notes

The desktop app uses the same `PomodoroTimer` class as the Streamlit app, so:

- Sessions are saved to same database
- Can view history in Streamlit app
- Can link sessions to notes (when integrated)

### Viewing History

To view detailed Pomodoro history:

1. Run Streamlit app: `streamlit run pomodoro_app.py`
2. Check "Session History" section
3. See all past sessions with timestamps

---

## 📁 File Structure

```
Knowledge-vault/
├── pomodoro_desktop.py       # Desktop app (this)
├── pomodoro_app.py           # Streamlit app
├── requirements_desktop.txt  # Desktop requirements
├── POMODORO_DESKTOP.md       # This guide
├── src/
│   ├── pomodoro.py          # Core timer logic
│   └── pomodoro_ui.py       # Streamlit UI components
└── data/
    └── knowledge.db         # SQLite database
```

---

## 🎨 Customization

### Changing Colors

Edit `pomodoro_desktop.py`, line 46:

```python
self.colors = {
    'bg': '#1e1e2e',        # Background
    'fg': '#cdd6f4',        # Foreground text
    'primary': '#f38ba8',   # Work/primary actions
    'secondary': '#89b4fa', # Breaks/secondary
    'success': '#a6e3a1',   # Success states
    'warning': '#f9e2af',   # Warnings
    'surface': '#313244',   # Panels
    'surface_alt': '#45475a', # Alt panels
}
```

**Color Schemes:**
- Current: Catppuccin Mocha
- Alternative: Nord, Dracula, Gruvbox, Solarized

### Changing Window Size

Edit line 38:
```python
self.root.geometry("500x700")  # width x height
```

### Adding Custom Presets

Edit `src/pomodoro.py` and add to `PomodoroPresets` class.

---

## 🚀 Advanced Features

### Command Line Options (Future)

```bash
# Start with specific preset
python pomodoro_desktop.py --preset extended

# Start minimized to tray
python pomodoro_desktop.py --minimized

# Custom work duration
python pomodoro_desktop.py --work 30
```

### System Tray Support (Future)

- Minimize to system tray
- Quick controls from tray menu
- Tray icon shows timer state

---

## 📊 Comparison: Desktop vs Streamlit

| Feature | Desktop App | Streamlit App |
|---------|-------------|---------------|
| **Interface** | Native tkinter | Web browser |
| **Performance** | Faster, native | Requires server |
| **Notifications** | Desktop native | Browser-based |
| **Integration** | Standalone | Full Knowledge Vault |
| **Widgets** | Single window | Sidebar + page |
| **History** | Current day | Full history |
| **Best for** | Focus tool | Knowledge mgmt |

**Use Desktop App when:**
- You want a dedicated focus timer
- Don't need full Knowledge Vault features
- Prefer native desktop apps
- Want minimal resource usage

**Use Streamlit App when:**
- Using Knowledge Vault for notes
- Want to link sessions to notes
- Need detailed history and analytics
- Prefer browser-based apps

---

## 🐛 Known Issues

1. **Window flashing**: On some Linux systems, window flash may not work
2. **Notification icons**: May not show custom icon on all systems
3. **System tray**: Not yet implemented (planned)

---

## 🛣️ Roadmap

### v1.1 (Planned)
- [ ] System tray support
- [ ] Keyboard shortcuts
- [ ] Sound effects (tick, completion)
- [ ] Custom presets UI
- [ ] Session notes/comments

### v1.2 (Future)
- [ ] Multi-language support
- [ ] Themes (light/dark toggle)
- [ ] Weekly/monthly stats
- [ ] Export statistics
- [ ] Integration with calendar apps

---

## 📝 License

MIT License - Part of Knowledge Vault project

---

## 🙏 Credits

- **Pomodoro Technique**: Francesco Cirillo
- **Color Scheme**: Catppuccin Mocha
- **Icons**: Unicode emoji
- **Framework**: Python tkinter

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/ndthong2411/Knowledge-vault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ndthong2411/Knowledge-vault/discussions)

---

**Made with ❤️ for focused, productive work**

**Version**: 1.0.0
**Last Updated**: 2025-11-17
