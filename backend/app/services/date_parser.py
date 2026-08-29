from datetime import date, datetime
import re


def parse_deadline(value):
    """
    Convert Gemini deadline text into a Python date.

    Examples:

        "September 3, 2026"
        -> 2026-09-03

        "August 28, 2026"
        -> 2026-08-28

        "2026-09-03"
        -> 2026-09-03

    If the value cannot be converted,
    return None.
    """

    # No deadline
    if not value:
        return None

    # Already a Python date
    if isinstance(value, date):
        return value

    value = str(value).strip()

    # ---------------------------------------------------------
    # FORMAT 1: YYYY-MM-DD
    # ---------------------------------------------------------

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        pass

    # ---------------------------------------------------------
    # FORMAT 2: September 3, 2026
    # ---------------------------------------------------------

    try:
        return datetime.strptime(
            value,
            "%B %d, %Y"
        ).date()

    except ValueError:
        pass

    # ---------------------------------------------------------
    # FORMAT 3: Sep 3, 2026
    # ---------------------------------------------------------

    try:
        return datetime.strptime(
            value,
            "%b %d, %Y"
        ).date()

    except ValueError:
        pass

    # ---------------------------------------------------------
    # FORMAT 4: September 3 2026
    # ---------------------------------------------------------

    try:
        return datetime.strptime(
            value,
            "%B %d %Y"
        ).date()

    except ValueError:
        pass

    # ---------------------------------------------------------
    # FORMAT 5: Sep 3 2026
    # ---------------------------------------------------------

    try:
        return datetime.strptime(
            value,
            "%b %d %Y"
        ).date()

    except ValueError:
        pass

    # ---------------------------------------------------------
    # Could not understand the date
    # ---------------------------------------------------------

    print(
        f"WARNING: Could not parse deadline: {value}"
    )

    return None