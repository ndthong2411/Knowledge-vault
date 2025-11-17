# 🍅 Pomodoro Timer - User Guide

## What is Pomodoro?

The **Pomodoro Technique** is a time management method that uses a timer to break work into intervals, traditionally 25 minutes in length, separated by short breaks.

## Features

### ⏰ Timer Functions
- **Work Sessions**: Default 25 minutes of focused work
- **Short Breaks**: 5 minutes to recharge
- **Long Breaks**: 15 minutes after completing 4 pomodoros
- **Pause/Resume**: Take control of your time
- **Progress Tracking**: Visual progress bar

### 📊 Statistics
- **Daily Stats**: Track pomodoros completed today
- **Weekly Overview**: See your productivity over 7 days
- **Session History**: Review all completed sessions
- **Export History**: Download your pomodoro log

### 🎨 Presets

#### 1. Classic Pomodoro (Default)
- Work: 25 minutes
- Short Break: 5 minutes
- Long Break: 15 minutes
- Long break after: 4 sessions

#### 2. Extended Focus
- Work: 50 minutes
- Short Break: 10 minutes
- Long Break: 30 minutes
- Long break after: 3 sessions

#### 3. Quick Sessions
- Work: 15 minutes
- Short Break: 3 minutes
- Long Break: 10 minutes
- Long break after: 4 sessions

#### 4. Custom
- Set your own durations!

## How to Use

### In Standalone App

```bash
streamlit run pomodoro_app.py
```

### Features:
1. **Large Timer Display** - See time remaining clearly
2. **Control Buttons** - Start, pause, resume, stop
3. **Task Description** - Optional note for what you're working on
4. **Statistics** - View daily and weekly stats
5. **Settings** - Choose presets or customize
6. **History** - Review and export past sessions

### In Main Knowledge Vault App

The Pomodoro timer is integrated into the sidebar:

1. **Sidebar Widget**: Quick access to timer
2. **Start Work**: Begin a focus session
3. **Take Break**: Rest between sessions
4. **Live Updates**: Timer updates every second

### When Working on Notes

1. Open a note you want to work on
2. Start Pomodoro timer in sidebar
3. Focus on writing/editing
4. Timer reminds you when to take breaks
5. Stats tracked automatically

## Best Practices

### 📝 For Note-Taking
- **Start Pomodoro**: Before beginning a new note
- **Single Focus**: Work on one note per pomodoro
- **Track Progress**: See how long topics take
- **Break Time**: Review what you wrote during breaks

### 🧠 For Learning
- **Study Sessions**: Use 25-min intervals
- **Active Recall**: Review during breaks
- **Spacing**: Use breaks for different topics
- **Track**: Monitor study time per subject

### 📚 For Research
- **Deep Work**: Use extended focus (50 min)
- **Literature Review**: One paper per pomodoro
- **Note-Taking**: Capture insights during session
- **Breaks**: Process and connect ideas

### ✍️ For Writing
- **Writing Sprints**: 25-min focused writing
- **No Editing**: Just write during pomodoro
- **Break Review**: Quick read during break
- **Progress**: Track words/pages per session

## Tips for Success

### 🎯 Before Starting
- [ ] Clear your workspace
- [ ] Set specific goal for session
- [ ] Silence notifications
- [ ] Have materials ready
- [ ] Note what you'll work on

### 🔥 During Work Session
- [ ] Focus on single task
- [ ] Resist distractions
- [ ] If interrupted, reset timer
- [ ] Keep going until timer rings
- [ ] Mark tasks completed

### ☕ During Breaks
- [ ] Step away from screen
- [ ] Stretch or move
- [ ] Hydrate
- [ ] Rest your eyes
- [ ] Don't check work

### 🌴 During Long Breaks
- [ ] Take a walk
- [ ] Eat something
- [ ] Socialize
- [ ] Exercise
- [ ] Reflect on progress

## Statistics Explained

### Daily Stats
- **Sessions Completed**: Pomodoros finished today
- **Total Work Time**: Hours spent in focus mode
- **Focus Minutes**: Sum of all work sessions

### Weekly View
- **7-Day Overview**: Sessions per day
- **Patterns**: Identify productive days
- **Consistency**: Track daily habits

### Session History
- **All Sessions**: Complete log
- **Status**: Completed (✅) or Stopped (❌)
- **Task Notes**: What you worked on
- **Duration**: Time spent
- **Export**: Download as Markdown

## Keyboard Shortcuts (Future)

Coming soon:
- `Ctrl+P` - Start/Pause Pomodoro
- `Ctrl+Shift+P` - Stop Pomodoro
- `Ctrl+B` - Start Break

## Integration with Notes

### Link Pomodoros to Notes
```python
# When starting a session
timer.start_work_session(
    note_id=current_note_id,
    task_description="Writing introduction"
)
```

### Daily Notes Integration
Your pomodoro sessions can automatically appear in daily notes:
```markdown
## Pomodoro Sessions
- 🍅 09:00 - 09:25: Writing blog post (✅)
- ☕ 09:25 - 09:30: Break
- 🍅 09:30 - 09:55: Research topic (✅)
- ☕ 09:55 - 10:00: Break
```

## Troubleshooting

### Timer Not Updating?
- Check if auto-refresh is enabled
- Refresh browser manually (F5)
- Timer updates every second

### Stats Not Showing?
- Complete at least one session
- Stats appear after first pomodoro
- Check session was marked complete

### Sound Not Playing?
- Enable notifications in settings
- Check browser permissions
- Balloons animation = sound enabled

## Advanced Usage

### Custom Workflow
```python
# Create custom timer
from src.pomodoro import PomodoroTimer

timer = PomodoroTimer(
    work_duration=40,      # 40-min work
    short_break=8,         # 8-min break
    long_break=25,         # 25-min long break
    sessions_until_long_break=3  # After 3 sessions
)
```

### Export for Analysis
```python
# Export history
history = timer.export_session_history()

# Analyze in pandas
import pandas as pd
# Convert to DataFrame for analysis
```

### Integration Examples

#### With Task List
```python
tasks = ["Write intro", "Add examples", "Edit"]

for task in tasks:
    timer.start_work_session(task_description=task)
    # Work...
    timer.stop(completed=True)
```

#### With Note Tags
```python
# Tag sessions by topic
session_tags = {
    'machine-learning': 5 pomodoros,
    'python': 3 pomodoros,
    'writing': 4 pomodoros
}
```

## Benefits

### 🎯 Productivity
- ✅ Improved focus
- ✅ Better time management
- ✅ Reduced burnout
- ✅ Clear progress tracking

### 🧠 Mental Health
- ✅ Regular breaks prevent fatigue
- ✅ Sense of accomplishment
- ✅ Sustainable work pace
- ✅ Stress reduction

### 📚 For Knowledge Work
- ✅ Deep work sessions
- ✅ Prevent context switching
- ✅ Track learning time
- ✅ Build consistent habits

## FAQ

**Q: Can I customize the durations?**
A: Yes! Choose "Custom" preset and set your own timings.

**Q: What if I need to stop mid-session?**
A: Click "Stop" button. Session won't count as completed.

**Q: Do breaks start automatically?**
A: No, you start breaks manually when ready.

**Q: Can I skip breaks?**
A: Yes, but not recommended! Breaks are important.

**Q: Does it work offline?**
A: Yes! Timer runs locally in your browser.

**Q: Can I sync across devices?**
A: Currently no, but history can be exported/imported.

## Resources

- [Pomodoro Technique Official](https://francescocirillo.com/pages/pomodoro-technique)
- [Research on Productivity](https://en.wikipedia.org/wiki/Pomodoro_Technique)
- [Deep Work by Cal Newport](https://www.calnewport.com/books/deep-work/)

## Version History

- **v1.0** - Initial release
  - Classic pomodoro timer
  - Statistics tracking
  - Session history
  - Multiple presets

---

**Happy Focusing! 🍅**

Remember: The Pomodoro Technique is flexible. Adjust to fit your needs!
