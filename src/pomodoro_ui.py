"""
Pomodoro UI Components for Streamlit
"""
import streamlit as st
from datetime import datetime
import time
from src.pomodoro import PomodoroTimer, PomodoroState, PomodoroPresets


def init_pomodoro_session_state():
    """Initialize Pomodoro timer in session state"""
    if 'pomodoro_timer' not in st.session_state:
        st.session_state.pomodoro_timer = PomodoroTimer()

    if 'pomodoro_auto_refresh' not in st.session_state:
        st.session_state.pomodoro_auto_refresh = False

    if 'pomodoro_sound_enabled' not in st.session_state:
        st.session_state.pomodoro_sound_enabled = True


def render_pomodoro_widget():
    """Render compact Pomodoro widget for sidebar"""
    init_pomodoro_session_state()

    timer = st.session_state.pomodoro_timer

    st.markdown("### 🍅 Pomodoro Timer")

    # Current state indicator
    state_emoji = {
        PomodoroState.IDLE: "⏸️",
        PomodoroState.WORKING: "🔥",
        PomodoroState.SHORT_BREAK: "☕",
        PomodoroState.LONG_BREAK: "🌴",
        PomodoroState.PAUSED: "⏸️"
    }

    state_name = {
        PomodoroState.IDLE: "Ready",
        PomodoroState.WORKING: "Working",
        PomodoroState.SHORT_BREAK: "Short Break",
        PomodoroState.LONG_BREAK: "Long Break",
        PomodoroState.PAUSED: "Paused"
    }

    current_emoji = state_emoji.get(timer.state, "⏸️")
    current_name = state_name.get(timer.state, "Ready")

    st.caption(f"{current_emoji} Status: **{current_name}**")

    # Display timer
    if timer.state != PomodoroState.IDLE:
        remaining = timer.get_remaining_time()
        formatted_time = timer.format_time(remaining)

        # Check if finished
        if timer.is_finished():
            st.success("⏰ Time's up!")
            suggestion = timer.auto_complete_and_suggest_next()
            st.info(suggestion)

            # Play sound (placeholder)
            if st.session_state.pomodoro_sound_enabled:
                st.balloons()

        else:
            # Big timer display
            st.markdown(f"## <center>{formatted_time}</center>", unsafe_allow_html=True)

            # Progress bar
            progress = timer.get_progress_percentage()
            st.progress(progress / 100)

            # Control buttons
            col1, col2 = st.columns(2)

            with col1:
                if timer.state == PomodoroState.PAUSED:
                    if st.button("▶️ Resume", use_container_width=True):
                        timer.resume()
                        st.rerun()
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        timer.pause()
                        st.rerun()

            with col2:
                if st.button("⏹️ Stop", use_container_width=True):
                    timer.stop(completed=False)
                    st.rerun()

    else:
        # Start buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔥 Start Work", use_container_width=True):
                timer.start_work_session()
                st.rerun()

        with col2:
            if st.button("☕ Break", use_container_width=True):
                timer.start_break()
                st.rerun()

    # Stats
    st.markdown("---")
    st.caption(f"**Today**: {timer.sessions_completed} 🍅 completed")

    # Auto-refresh toggle (for live timer)
    if timer.state not in [PomodoroState.IDLE, PomodoroState.PAUSED]:
        st.markdown("""
        <script>
            setTimeout(function(){
                window.parent.location.reload();
            }, 1000);
        </script>
        """, unsafe_allow_html=True)


def render_pomodoro_page():
    """Render full Pomodoro page with settings and statistics"""
    init_pomodoro_session_state()

    st.title("🍅 Pomodoro Timer")

    timer = st.session_state.pomodoro_timer

    # Main timer display
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Current Session")

        # Large timer display
        if timer.state != PomodoroState.IDLE:
            remaining = timer.get_remaining_time()
            formatted_time = timer.format_time(remaining)

            st.markdown(f"# <center>{formatted_time}</center>", unsafe_allow_html=True)

            # Progress
            progress = timer.get_progress_percentage()
            st.progress(progress / 100)

            # State
            state_name = {
                PomodoroState.WORKING: "🔥 Focus Time",
                PomodoroState.SHORT_BREAK: "☕ Short Break",
                PomodoroState.LONG_BREAK: "🌴 Long Break",
                PomodoroState.PAUSED: "⏸️ Paused"
            }

            st.markdown(f"### <center>{state_name.get(timer.state, 'Ready')}</center>",
                       unsafe_allow_html=True)

            # Check if finished
            if timer.is_finished():
                st.success("⏰ Session Complete!")
                suggestion = timer.auto_complete_and_suggest_next()
                st.info(suggestion)

                if st.session_state.pomodoro_sound_enabled:
                    st.balloons()

            # Controls
            st.markdown("---")
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if timer.state == PomodoroState.PAUSED:
                    if st.button("▶️ Resume", use_container_width=True, type="primary"):
                        timer.resume()
                        st.rerun()
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        timer.pause()
                        st.rerun()

            with col_b:
                if st.button("⏹️ Stop", use_container_width=True):
                    timer.stop(completed=False)
                    st.rerun()

            with col_c:
                if st.button("✅ Complete", use_container_width=True, type="primary"):
                    timer.stop(completed=True)
                    st.success("Session marked as complete!")
                    st.rerun()

        else:
            # Start new session
            st.markdown("## <center>Ready to Start</center>", unsafe_allow_html=True)

            task_desc = st.text_input("What are you working on? (optional)",
                                     placeholder="e.g., Write blog post, Study Python...")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("🔥 Start Work Session", use_container_width=True, type="primary"):
                    timer.start_work_session(task_description=task_desc if task_desc else None)
                    st.rerun()

            with col_b:
                if st.button("☕ Start Break", use_container_width=True):
                    timer.start_break()
                    st.rerun()

    with col2:
        # Today's stats
        st.markdown("### 📊 Today's Stats")

        stats = timer.get_today_stats()

        st.metric("Pomodoros Completed", f"{stats['sessions_completed']} 🍅")
        st.metric("Total Work Time", f"{stats['total_work_hours']}h")
        st.metric("Focus Minutes", stats['total_work_minutes'])

        st.markdown("---")

        # Settings
        st.markdown("### ⚙️ Settings")

        preset = st.selectbox(
            "Preset",
            ["classic", "extended", "short", "custom"],
            format_func=lambda x: PomodoroPresets.get_all_presets()[x]['name']
        )

        if preset == "custom":
            work_min = st.number_input("Work (min)", 1, 90, timer.work_duration)
            short_break_min = st.number_input("Short break (min)", 1, 30, timer.short_break)
            long_break_min = st.number_input("Long break (min)", 1, 60, timer.long_break)
            sessions = st.number_input("Sessions until long break", 1, 10, timer.sessions_until_long_break)

            if st.button("Apply Settings"):
                st.session_state.pomodoro_timer = PomodoroTimer(
                    work_duration=work_min,
                    short_break=short_break_min,
                    long_break=long_break_min,
                    sessions_until_long_break=sessions
                )
                st.success("Settings updated!")
                st.rerun()
        else:
            if st.button("Apply Preset"):
                st.session_state.pomodoro_timer = PomodoroPresets.create_timer_from_preset(preset)
                st.success(f"{PomodoroPresets.get_all_presets()[preset]['name']} applied!")
                st.rerun()

        # Sound toggle
        st.session_state.pomodoro_sound_enabled = st.checkbox(
            "Enable notifications",
            value=st.session_state.pomodoro_sound_enabled
        )

    # Weekly stats
    st.markdown("---")
    st.markdown("### 📅 This Week")

    week_stats = timer.get_week_stats()

    # Create columns for each day
    cols = st.columns(7)

    for idx, day_stat in enumerate(week_stats):
        with cols[idx]:
            st.metric(
                day_stat['day_name'][:3],
                f"{day_stat['sessions']}🍅",
                f"{day_stat['minutes']}m"
            )

    # Session history
    if timer.session_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Sessions")

        with st.expander("View Session History"):
            for session in reversed(timer.session_history[-10:]):  # Last 10 sessions
                status = "✅" if session.completed else "❌"
                session_type = session.session_type.value.replace('_', ' ').title()

                col_a, col_b, col_c = st.columns([1, 2, 1])

                with col_a:
                    st.caption(status)

                with col_b:
                    st.caption(f"**{session_type}** - {session.start_time.strftime('%H:%M')}")
                    if session.task_description:
                        st.caption(f"📝 {session.task_description}")

                with col_c:
                    st.caption(f"{session.duration_minutes}m")

                st.markdown("---")

        # Export history
        if st.button("📥 Export History"):
            history_md = timer.export_session_history()
            st.download_button(
                "Download History",
                history_md,
                file_name=f"pomodoro_history_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

    # Auto-refresh for live timer
    if timer.state not in [PomodoroState.IDLE, PomodoroState.PAUSED]:
        time.sleep(1)
        st.rerun()


def render_pomodoro_mini_widget():
    """Render minimal Pomodoro widget (for embedding in other pages)"""
    init_pomodoro_session_state()

    timer = st.session_state.pomodoro_timer

    if timer.state == PomodoroState.IDLE:
        if st.button("🍅 Start Pomodoro", use_container_width=True):
            timer.start_work_session()
            st.rerun()
    else:
        remaining = timer.get_remaining_time()
        formatted_time = timer.format_time(remaining)

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.metric("🍅", formatted_time)

        with col2:
            progress = timer.get_progress_percentage()
            st.progress(progress / 100)

        with col3:
            if st.button("⏹️", use_container_width=True):
                timer.stop(completed=False)
                st.rerun()

        # Auto-refresh
        if timer.state not in [PomodoroState.IDLE, PomodoroState.PAUSED]:
            time.sleep(1)
            st.rerun()
