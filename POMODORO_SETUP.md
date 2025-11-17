# 🍅 Pomodoro Timer - Quick Setup Guide

**Two ways to use Pomodoro with Knowledge Vault**

---

## Option 1: Desktop App (Standalone)

**Best for**: Dedicated focus timer, minimal distractions

### Quick Start

```bash
# Install dependencies
pip install -r requirements_desktop.txt

# Run desktop app
python pomodoro_desktop.py
```

**Features:**
- ✅ Native desktop window
- ✅ Desktop notifications
- ✅ Fast and lightweight
- ✅ Beautiful dark UI
- ✅ Keyboard-friendly

📖 **Full guide**: See [POMODORO_DESKTOP.md](POMODORO_DESKTOP.md)

---

## Option 2: Streamlit Web App

**Best for**: Integrated with Knowledge Vault notes

### Quick Start

```bash
# Install all dependencies
pip install -r requirements.txt

# Option A: Standalone Pomodoro app
streamlit run pomodoro_app.py

# Option B: Full Knowledge Vault (includes Pomodoro)
streamlit run app.py
```

**Features:**
- ✅ Link sessions to notes
- ✅ Full session history
- ✅ Analytics and charts
- ✅ Integration with notes
- ✅ Sidebar widget

📖 **Full guide**: See [POMODORO_GUIDE.md](POMODORO_GUIDE.md)

---

## Which One Should I Use?

| Use Case | Recommendation |
|----------|----------------|
| Just want a focus timer | **Desktop App** |
| Taking notes while working | **Streamlit App** |
| Track work on specific notes | **Streamlit App** |
| Minimal resource usage | **Desktop App** |
| Detailed analytics | **Streamlit App** |
| Offline use | **Desktop App** |

**You can use both!** They share the same database.

---

## Installation Troubleshooting

### tkinter missing (Desktop App)

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS/Windows:**
```bash
# Reinstall Python from python.org
```

### Dependencies installation failed

```bash
# Try upgrading pip first
pip install --upgrade pip

# Then install
pip install -r requirements.txt
```

---

## File Overview

```
Knowledge-vault/
├── pomodoro_desktop.py           # Desktop app
├── pomodoro_app.py               # Streamlit standalone
├── app.py                        # Full Knowledge Vault
├── requirements.txt              # All dependencies
├── requirements_desktop.txt      # Desktop only
├── POMODORO_GUIDE.md            # Streamlit guide
├── POMODORO_DESKTOP.md          # Desktop guide
├── POMODORO_SETUP.md            # This file
└── src/
    ├── pomodoro.py              # Core timer logic
    └── pomodoro_ui.py           # Streamlit components
```

---

## Quick Tips

1. **Start with Desktop App** - Simple and fast
2. **Try Streamlit** - When you need note integration
3. **Use Both** - Desktop for focus, Streamlit for review
4. **Enable Notifications** - Never miss session completion
5. **Choose Preset** - Classic (25min), Extended (50min), Short (15min)

---

**Ready to focus? Pick one and start! 🍅**
