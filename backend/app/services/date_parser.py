from datetime import date, timedelta
import re


def parse_deadline(deadline):
    """
    Convert Gemini's deadline into a Python date.

    Examples:
        "2026-08-25" -> date(2026, 8, 25)
        "Friday"     -> next Friday
        "Tomorrow"   -> tomorrow
        "Monday"     -> next Monday
        "Before the deadline" -> None
    """

    if not deadline:
        return None

    deadline = str(deadline).strip()

    today = date.today()

    # -----------------------------------------
    # Already a YYYY-MM-DD date
    # -----------------------------------------

    try:
        return date.fromisoformat(deadline)

    except ValueError:
        pass

    # -----------------------------------------
    # Relative: tomorrow
    # -----------------------------------------

    if deadline.lower() == "tomorrow":
        return today + timedelta(days=1)

    # -----------------------------------------
    # Relative: today
    # -----------------------------------------

    if deadline.lower() == "today":
        return today

    # -----------------------------------------
    # Ignore vague deadlines
    # -----------------------------------------

    vague_deadlines = [
        "before the deadline",
        "soon",
        "later",
        "as soon as possible",
        "when possible",
        "next time",
    ]

    if deadline.lower() in vague_deadlines:
        return None

    # -----------------------------------------
    # Weekdays
    # -----------------------------------------

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    day_name = deadline.lower()

    if day_name in weekdays:

        target_day = weekdays[day_name]
        current_day = today.weekday()

        days_ahead = (target_day - current_day) % 7

        # If today is that day, choose next week
        if days_ahead == 0:
            days_ahead = 7

        return today + timedelta(days=days_ahead)

    # -----------------------------------------
    # Unknown format
    # -----------------------------------------

    return None