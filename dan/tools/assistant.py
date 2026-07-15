from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dan.tools.base import Tool, ToolResult
from dan.tools.decorators import tool
from dan.core.config import DEFAULT_DATA_DIR

DATA_DIR = DEFAULT_DATA_DIR
CALENDAR_FILE = DATA_DIR / "calendar.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"
ROUTINE_FILE = DATA_DIR / "routine.json"


def _load_json(path: Path) -> list[dict]:
    if path.exists():
        return json.loads(path.read_text())
    return []


def _save_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))


_DATE_PATTERN = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{2,4})")


def _parse_date(date_str: str) -> datetime | None:
    m = _DATE_PATTERN.search(date_str)
    if not m:
        return None
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if year < 100:
        year += 2000
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _resolve_date(date_str: str) -> str:
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    s = date_str.strip().lower()

    if s in ("today", "hoje", "hoy"):
        return now.strftime("%d/%m/%Y")
    if s in ("tomorrow", "manana", "mañana", "amanha", "amanhã"):
        return (today + timedelta(days=1)).strftime("%d/%m/%Y")
    if s in ("day after tomorrow", "passedat", "pasado manana", "pasado mañana"):
        return (today + timedelta(days=2)).strftime("%d/%m/%Y")
    if s in ("next week", "proxima semana", "proxima semana", "semana que vem"):
        return (today + timedelta(weeks=1)).strftime("%d/%m/%Y")

    day_names = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
        "lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3,
        "viernes": 4, "sabado": 5, "domingo": 6,
        "segunda": 0, "terca": 1, "quarta": 2, "quinta": 3,
        "sexta": 4, "sabado": 5, "domingo": 6,
    }
    for name, idx in day_names.items():
        if s == name or s.startswith("next " + name) or s.startswith("proximo " + name) or s.startswith("proxima " + name):
            days_ahead = idx - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%d/%m/%Y")

    return date_str


def _cleanup_outdated_calendar() -> int:
    events = _load_json(CALENDAR_FILE)
    if not events:
        return 0
    now = datetime.now()
    kept = []
    removed = 0
    for e in events:
        date_str = e.get("date", "")
        if date_str:
            dt = _parse_date(date_str)
            if dt and dt < now:
                removed += 1
                continue
        kept.append(e)
    if removed:
        _save_json(CALENDAR_FILE, kept)
    return removed


def _cleanup_outdated_reminders() -> int:
    reminders = _load_json(REMINDERS_FILE)
    if not reminders:
        return 0
    now = datetime.now()
    kept = []
    removed = 0
    for r in reminders:
        if r.get("done"):
            removed += 1
            continue
        remind_at = r.get("remind_at", "")
        if remind_at:
            dt = _parse_date(remind_at)
            if dt and dt < now:
                removed += 1
                continue
        kept.append(r)
    if removed:
        _save_json(REMINDERS_FILE, kept)
    return removed


# ─── Calendar ──────────────────────────────────────────────


@tool
class CalendarAddTool(Tool):
    name = "calendar_add"
    description = "Adds an event to the calendar"
    aliases = ("add event", "schedule", "create event")
    intents = {
        "add event": 5,
        "set an event": 5,
        "schedule": 5,
        "create event": 5,
        "new event": 5,
        "set meeting": 5,
        "add to calendar": 4,
        "block time": 4,
        "put on calendar": 3,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        title = kwargs.get("title", kwargs.get("message", ""))
        date = _resolve_date(kwargs.get("date", ""))
        time = kwargs.get("time", "")
        duration = kwargs.get("duration", "60")
        recurrence = kwargs.get("recurrence", "")
        priority = kwargs.get("priority", "normal")
        notes = kwargs.get("notes", "")

        if not title:
            return ToolResult(success=False, message="No event title provided.")

        if date:
            dt = _parse_date(date)
            if dt and dt < datetime.now():
                return ToolResult(
                    success=False,
                    message=f"Cannot add event in the past. '{date}' ({dt.strftime('%d/%m/%Y')}) is before today ({datetime.now().strftime('%d/%m/%Y')}).",
                )

        event = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "date": date,
            "time": time,
            "duration": duration,
            "recurrence": recurrence,
            "priority": priority,
            "notes": notes,
            "created": datetime.now().isoformat(),
        }

        events = _load_json(CALENDAR_FILE)
        events.append(event)
        _save_json(CALENDAR_FILE, events)

        when = ""
        if date:
            when = date
        if time:
            when += f" at {time}"

        return ToolResult(
            success=True,
            message=f"Event added: {title}" + (f" ({when})" if when else ""),
        )


@tool
class CalendarListTool(Tool):
    name = "calendar_list"
    description = "Lists upcoming calendar events"
    aliases = ("list events", "show calendar", "what's on")
    intents = {
        "list events": 5,
        "show calendar": 5,
        "what's on": 5,
        "what do i have": 5,
        "upcoming events": 5,
        "my schedule": 5,
        "my day": 5,
        "today schedule": 5,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        removed = _cleanup_outdated_calendar()
        events = _load_json(CALENDAR_FILE)
        if not events:
            msg = "No events scheduled."
            if removed:
                msg += f" Cleaned up {removed} outdated event(s)."
            return ToolResult(success=True, message=msg)

        today = datetime.now().strftime("%d/%m/%Y")
        filter_date = kwargs.get("date", today)

        filtered = [e for e in events if e.get("date") == filter_date]
        if not filtered:
            filtered = events[:10]

        lines = []
        for e in filtered:
            when = e.get("date", "no date")
            if e.get("time"):
                when += f" {e['time']}"
            lines.append(f"  [{e['id']}] {e['title']} - {when} (priority: {e.get('priority', 'normal')})")

        cleanup_msg = f" Cleaned up {removed} outdated event(s)." if removed else ""
        return ToolResult(
            success=True,
            message=f"Calendar ({len(filtered)} events):{cleanup_msg}\n" + "\n".join(lines),
        )


@tool
class CalendarDeleteTool(Tool):
    name = "calendar_delete"
    description = "Deletes a calendar event"
    aliases = ("remove event", "cancel event", "delete event")
    intents = {
        "delete event": 5,
        "remove event": 5,
        "cancel event": 5,
        "cancel meeting": 5,
        "remove from calendar": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        event_id = kwargs.get("id", "")
        title = kwargs.get("title", kwargs.get("message", ""))

        events = _load_json(CALENDAR_FILE)
        if not events:
            return ToolResult(success=True, message="No events to delete.")

        if event_id:
            events = [e for e in events if e["id"] != event_id]
        elif title:
            events = [e for e in events if title.lower() not in e.get("title", "").lower()]
        else:
            return ToolResult(success=False, message="Provide event ID or title to delete.")

        _save_json(CALENDAR_FILE, events)
        return ToolResult(success=True, message="Event deleted.")


# ─── Reminders ─────────────────────────────────────────────


@tool
class ReminderSetTool(Tool):
    name = "reminder_set"
    description = "Sets a reminder"
    aliases = ("remind me", "set reminder", "create reminder")
    intents = {
        "remind me": 5,
        "set reminder": 5,
        "create reminder": 5,
        "don't forget": 5,
        "remember to": 4,
        "alert me": 4,
        "notification": 3,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        message = kwargs.get("message", kwargs.get("title", ""))
        remind_at = _resolve_date(kwargs.get("time", kwargs.get("datetime", "")))

        if not message:
            return ToolResult(success=False, message="No reminder message provided.")

        if remind_at:
            dt = _parse_date(remind_at)
            if dt and dt < datetime.now():
                return ToolResult(
                    success=False,
                    message=f"Cannot set reminder in the past. '{remind_at}' is before today ({datetime.now().strftime('%d/%m/%Y')}).",
                )

        reminder = {
            "id": str(uuid.uuid4())[:8],
            "message": message,
            "remind_at": remind_at,
            "created": datetime.now().isoformat(),
            "done": False,
        }

        reminders = _load_json(REMINDERS_FILE)
        reminders.append(reminder)
        _save_json(REMINDERS_FILE, reminders)

        when = remind_at if remind_at else "later"
        return ToolResult(
            success=True,
            message=f"Reminder set: {message} (at {when})",
        )


@tool
class ReminderListTool(Tool):
    name = "reminder_list"
    description = "Lists active reminders"
    aliases = ("list reminders", "show reminders", "my reminders")
    intents = {
        "list reminders": 5,
        "show reminders": 5,
        "my reminders": 5,
        "what reminders": 5,
        "pending reminders": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        removed = _cleanup_outdated_reminders()
        reminders = _load_json(REMINDERS_FILE)
        active = [r for r in reminders if not r.get("done")]

        cleanup_msg = f" Cleaned up {removed} outdated reminder(s)." if removed else ""

        if not active:
            msg = "No active reminders." + cleanup_msg
            return ToolResult(success=True, message=msg)

        lines = []
        for r in active:
            when = r.get("remind_at", "no time set")
            lines.append(f"  [{r['id']}] {r['message']} (at {when})")

        return ToolResult(
            success=True,
            message=f"Reminders ({len(active)} active):{cleanup_msg}\n" + "\n".join(lines),
        )


@tool
class ReminderDoneTool(Tool):
    name = "reminder_done"
    description = "Marks a reminder as done"
    aliases = ("done reminder", "complete reminder", "clear reminder")
    intents = {
        "done reminder": 5,
        "complete reminder": 5,
        "clear reminder": 5,
        "mark done": 4,
        "dismiss reminder": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        reminder_id = kwargs.get("id", "")
        message = kwargs.get("message", "")

        reminders = _load_json(REMINDERS_FILE)
        if not reminders:
            return ToolResult(success=True, message="No reminders to complete.")

        found = False
        for r in reminders:
            if reminder_id and r["id"] == reminder_id:
                r["done"] = True
                found = True
                break
            elif message and message.lower() in r.get("message", "").lower():
                r["done"] = True
                found = True

        if found:
            _save_json(REMINDERS_FILE, reminders)
            return ToolResult(success=True, message="Reminder marked as done.")
        return ToolResult(success=False, message="Reminder not found.")


# ─── Routine Memory ────────────────────────────────────────


@tool
class RoutineSetTool(Tool):
    name = "routine_set"
    description = "Stores a user routine or preference"
    aliases = ("set routine", "remember routine", "my routine")
    intents = {
        "set routine": 5,
        "remember routine": 5,
        "my routine": 5,
        "i usually": 5,
        "i always": 5,
        "normally i": 5,
        "typically i": 4,
        "i work": 4,
        "my schedule": 3,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        category = kwargs.get("category", "general")
        pattern = kwargs.get("pattern", kwargs.get("message", ""))
        time_range = kwargs.get("time", "")
        days = kwargs.get("days", "")
        notes = kwargs.get("notes", "")

        if not pattern:
            return ToolResult(success=False, message="No routine pattern provided.")

        routine = {
            "id": str(uuid.uuid4())[:8],
            "category": category,
            "pattern": pattern,
            "time": time_range,
            "days": days,
            "notes": notes,
            "created": datetime.now().isoformat(),
        }

        routines = _load_json(ROUTINE_FILE)
        routines.append(routine)
        _save_json(ROUTINE_FILE, routines)

        return ToolResult(
            success=True,
            message=f"Routine stored: {pattern}" + (f" ({time_range})" if time_range else ""),
        )


@tool
class RoutineGetTool(Tool):
    name = "routine_get"
    description = "Retrieves user routines and preferences"
    aliases = ("get routine", "show routine", "what's my routine")
    intents = {
        "get routine": 5,
        "show routine": 5,
        "what's my routine": 5,
        "what do i usually": 5,
        "what's my schedule": 5,
        "what am i doing": 4,
        "what should i do": 4,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        routines = _load_json(ROUTINE_FILE)
        if not routines:
            return ToolResult(success=True, message="No routines stored yet. Tell me about your daily patterns and I'll remember them.")

        category = kwargs.get("category", "")
        if category:
            routines = [r for r in routines if r.get("category") == category]

        lines = []
        for r in routines:
            when = r.get("time", "")
            days = r.get("days", "")
            extra = ""
            if when:
                extra += f" at {when}"
            if days:
                extra += f" on {days}"
            lines.append(f"  [{r['category']}] {r['pattern']}{extra}")

        return ToolResult(
            success=True,
            message=f"Your routines ({len(routines)} stored):\n" + "\n".join(lines),
        )


# ─── Daily Briefing ────────────────────────────────────────


@tool
class DailyBriefingTool(Tool):
    name = "daily_briefing"
    description = "Generates a daily briefing with calendar, reminders, and routine"
    aliases = ("briefing", "morning briefing", "start my day")
    intents = {
        "daily briefing": 5,
        "morning briefing": 5,
        "start my day": 5,
        "good morning": 5,
        "what's today": 4,
        "plan my day": 4,
        "what should i do today": 5,
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        now = datetime.now()
        today = now.strftime("%d/%m/%Y")
        day_name = now.strftime("%A")
        time_str = now.strftime("%H:%M")

        cal_removed = _cleanup_outdated_calendar()
        rem_removed = _cleanup_outdated_reminders()

        events = _load_json(CALENDAR_FILE)
        today_events = [e for e in events if e.get("date") == today]

        reminders = _load_json(REMINDERS_FILE)
        active_reminders = [r for r in reminders if not r.get("done")]

        routines = _load_json(ROUTINE_FILE)

        cleanup_parts = []
        if cal_removed:
            cleanup_parts.append(f"{cal_removed} outdated event(s)")
        if rem_removed:
            cleanup_parts.append(f"{rem_removed} outdated reminder(s)")

        greeting = f"Good morning! Today is {day_name}, {today}. It's {time_str}."
        if cleanup_parts:
            greeting += f" Cleaned up {' and '.join(cleanup_parts)}."
        lines = [greeting, ""]

        if today_events:
            lines.append("Today's events:")
            for e in sorted(today_events, key=lambda x: x.get("time", "")):
                when = e.get("time", "no time")
                lines.append(f"  - {e['title']} at {when} (priority: {e.get('priority', 'normal')})")
        else:
            lines.append("No events scheduled for today.")

        if active_reminders:
            lines.append(f"\nActive reminders ({len(active_reminders)}):")
            for r in active_reminders[:5]:
                when = r.get("remind_at", "no time set")
                lines.append(f"  - {r['message']} (at {when})")

        if routines:
            lines.append("\nYour routines:")
            for r in routines[:5]:
                extra = ""
                if r.get("time"):
                    extra += f" at {r['time']}"
                if r.get("days"):
                    extra += f" on {r['days']}"
                lines.append(f"  - {r['pattern']}{extra}")

        return ToolResult(
            success=True,
            message="\n".join(lines),
        )
