import json
import os
import re
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from sqlalchemy.orm import Session

from app.models.context_change import ContextChange
from app.models.meeting import Meeting
from app.models.task import Task
from app.services.date_parser import parse_deadline


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MONTHS = (
    "January|February|March|April|May|June|July|"
    "August|September|October|November|December|"
    "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

NO_CHANGE_TYPES = {
    "none",
    "no_change",
    "no change",
    "no-change",
}

OWNER_CHANGE_TYPES = {
    "assignee",
    "owner",
    "owner_changed",
    "assignee_changed",
}

DEADLINE_CHANGE_TYPES = {
    "deadline",
    "deadline_changed",
    "due_date",
    "due date",
}


def _has_meeting_content(meeting: Meeting) -> bool:
    transcript = (meeting.transcript_text or "").strip()
    summary = (meeting.summary_text or "").strip()
    return bool(transcript or summary)


def get_comparable_previous_meeting(
    db: Session,
    user_id: int,
    exclude_meeting_id: Optional[int] = None,
):
    """
    Return the most recent previous meeting for this user that
    actually has transcript or summary text.

    Skips empty title-only meetings and other users' meetings.
    """

    query = (
        db.query(Meeting)
        .filter(Meeting.user_id == user_id)
        .order_by(Meeting.id.desc())
    )

    if exclude_meeting_id is not None:
        query = query.filter(Meeting.id != exclude_meeting_id)

    fallback = None

    for meeting in query.all():
        if not _has_meeting_content(meeting):
            continue

        if fallback is None:
            fallback = meeting

        facts = extract_assignment_facts(meeting_context_text(meeting))
        if facts.get("owner") or facts.get("deadline"):
            print(
                "===== CONTEXT CONTINUITY: previous meeting found ====="
            )
            print(
                f"previous_meeting_id={meeting.id} "
                f"title={meeting.title!r} user_id={user_id}"
            )
            return meeting

    if fallback is not None:
        print(
            "===== CONTEXT CONTINUITY: previous meeting found ====="
        )
        print(
            f"previous_meeting_id={fallback.id} "
            f"title={fallback.title!r} user_id={user_id}"
        )
        return fallback

    print(
        "===== CONTEXT CONTINUITY: no previous meeting found ====="
    )
    print(f"user_id={user_id}")
    return None


def meeting_context_text(meeting: Meeting) -> str:
    parts = []

    if meeting.title:
        parts.append(f"Title: {meeting.title}")

    if meeting.summary_text:
        parts.append(f"Summary: {meeting.summary_text}")

    if meeting.transcript_text:
        parts.append(f"Transcript: {meeting.transcript_text}")

    return "\n".join(parts)


def normalize_owner(value) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(
        r"^(assigned to|owner|assignee|responsible[: ]+)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = text.strip(" .,:;")

    if not text:
        return None

    return text.title()


def format_deadline_display(value) -> Optional[str]:
    parsed = parse_deadline(value)

    if parsed is None:
        if value:
            return str(value).strip()
        return None

    return parsed.strftime("%B %d, %Y").replace(" 0", " ")


def extract_assignment_facts(text: str) -> dict:
    """
    Extract task, owner, and deadline from meeting text.

    This is deterministic so owner/deadline changes can be
    detected even when Gemini output is missing or malformed.
    """

    source = text or ""
    facts = {
        "task": None,
        "owner": None,
        "deadline": None,
    }

    owner_patterns = [
        r"([A-Z][a-zA-Z]+)\s+is\s+assigned\s+to",
        r"assigned\s+to\s+([A-Z][a-zA-Z]+)",
        r"([A-Z][a-zA-Z]+)\s+is\s+now\s+responsible",
        r"([A-Z][a-zA-Z]+)\s+is\s+responsible\s+for",
        r"responsible(?:\s+for)?(?:\s+it)?(?:\s+now)?[:\s]+([A-Z][a-zA-Z]+)",
        r"owner[:\s]+([A-Z][a-zA-Z]+)",
        r"assignee[:\s]+([A-Z][a-zA-Z]+)",
        r"responsibility\s+changed\s+from\s+[A-Z][a-zA-Z]+\s+to\s+([A-Z][a-zA-Z]+)",
    ]

    for pattern in owner_patterns:
        match = re.search(pattern, source)
        if match:
            facts["owner"] = normalize_owner(match.group(1))
            break

    deadline_pattern = (
        rf"(?:deadline|due date|due)\s+"
        rf"(?:of|is|to|has been changed to|changed to|:)?\s*"
        rf"((?:{MONTHS})\s+\d{{1,2}}(?:,?\s+\d{{4}})?)"
    )

    match = re.search(deadline_pattern, source, flags=re.IGNORECASE)
    if match:
        facts["deadline"] = format_deadline_display(match.group(1))

    task_patterns = [
        r"implement(?:ing)?\s+([^.]+?)(?:\s+with\s+a\s+deadline|\.)",
        r"task[:\s]+([^.]+)",
        r"(JWT authentication)",
    ]

    for pattern in task_patterns:
        match = re.search(pattern, source, flags=re.IGNORECASE)
        if match:
            facts["task"] = re.sub(r"\s+", " ", match.group(1)).strip(" .")
            break

    print("===== CONTEXT CONTINUITY: context extracted =====")
    print(facts)

    return facts


def detect_context_changes(
    previous_text: str,
    current_text: str,
    previous_meeting_id: Optional[int] = None,
) -> list[dict]:
    """
    Compare previous and current meeting facts.

    Returns zero or more change dictionaries.
    """

    previous_facts = extract_assignment_facts(previous_text)
    current_facts = extract_assignment_facts(current_text)

    changes = []

    previous_owner = normalize_owner(previous_facts.get("owner"))
    current_owner = normalize_owner(current_facts.get("owner"))

    if (
        previous_owner
        and current_owner
        and previous_owner != current_owner
    ):
        changes.append({
            "change_type": "assignee",
            "task": current_facts.get("task") or previous_facts.get("task") or "",
            "previous_value": previous_owner,
            "new_value": current_owner,
            "evidence": current_text.strip(),
            "previous_meeting_id": previous_meeting_id,
        })

    previous_deadline = parse_deadline(previous_facts.get("deadline"))
    current_deadline = parse_deadline(current_facts.get("deadline"))

    if previous_deadline and current_deadline and previous_deadline != current_deadline:
        changes.append({
            "change_type": "deadline",
            "task": current_facts.get("task") or previous_facts.get("task") or "",
            "previous_value": format_deadline_display(previous_deadline),
            "new_value": format_deadline_display(current_deadline),
            "evidence": current_text.strip(),
            "previous_meeting_id": previous_meeting_id,
        })

    print("===== CONTEXT CONTINUITY: changes detected =====")
    print(changes)

    return changes


def _strip_code_fence(text: str) -> str:
    cleaned = (text or "").strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def parse_ai_context_result(
    raw,
    previous_meeting_id: Optional[int] = None,
) -> list[dict]:
    """
    Accept dict, list, JSON string, or malformed AI output
    and return a list of valid change dictionaries.
    """

    if raw is None:
        return []

    parsed = raw

    if isinstance(parsed, str):
        try:
            parsed = json.loads(_strip_code_fence(parsed))
        except (json.JSONDecodeError, TypeError, ValueError):
            print(
                "===== CONTEXT CONTINUITY: malformed AI output ignored ====="
            )
            return []

    if isinstance(parsed, dict):
        items = [parsed]
    elif isinstance(parsed, list):
        items = parsed
    else:
        return []

    results = []

    for item in items:
        if isinstance(item, str):
            try:
                item = json.loads(_strip_code_fence(item))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue

        if not isinstance(item, dict):
            continue

        change_type = str(item.get("change_type") or "none").strip().lower()
        change_type = change_type.replace(" ", "_")

        if change_type in NO_CHANGE_TYPES:
            continue

        if change_type in OWNER_CHANGE_TYPES:
            change_type = "assignee"
        elif change_type in DEADLINE_CHANGE_TYPES:
            change_type = "deadline"
        elif change_type == "decision":
            change_type = "decision"
        elif "|" in change_type:
            # Gemini sometimes copies "deadline | assignee | decision"
            continue
        else:
            continue

        previous_value = item.get("previous_value")
        new_value = item.get("new_value")

        if change_type == "assignee":
            previous_value = normalize_owner(previous_value)
            new_value = normalize_owner(new_value)
        elif change_type == "deadline":
            previous_value = format_deadline_display(previous_value)
            new_value = format_deadline_display(new_value)

        if not previous_value or not new_value or previous_value == new_value:
            continue

        results.append({
            "change_type": change_type,
            "task": item.get("task") or "",
            "previous_value": previous_value,
            "new_value": new_value,
            "evidence": item.get("evidence") or "",
            "previous_meeting_id": (
                item.get("previous_meeting_id")
                or previous_meeting_id
            ),
        })

    return results


def analyze_context_change(
    previous_context: str,
    current_transcript: str,
    previous_meeting_id: Optional[int] = None
):
    """
    Compare a previous meeting with the current meeting using Gemini.

    Returns a list of change dictionaries. Never raises on malformed
    model output; returns an empty list instead.
    """

    prompt = f"""
You are a meeting context continuity assistant.

Compare the previous meeting with the new meeting.

Look for important changes involving:

1. Deadline changes
2. Task owner / assignee changes
3. Important decision changes

Only report a change when there is clear evidence.
Do NOT invent information.

Previous meeting:
{previous_context}

Current meeting:
{current_transcript}

Return ONLY valid JSON.

If there is one change, return a JSON object.
If there are multiple changes, return a JSON array of objects.

Each object must use this structure:

{{
    "change_type": "deadline",
    "task": "task or decision affected",
    "previous_value": "old value",
    "new_value": "new value",
    "evidence": "sentence from the current meeting proving the change",
    "previous_meeting_id": {previous_meeting_id if previous_meeting_id else "null"}
}}

change_type must be exactly one of: deadline, assignee, decision, none

If there is NO important change, return:

{{
    "change_type": "none",
    "task": "",
    "previous_value": null,
    "new_value": null,
    "evidence": "",
    "previous_meeting_id": null
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        response_text = (response.text or "").strip()

        print("\n===== GEMINI CONTEXT RESPONSE =====")
        print(response_text)

        return parse_ai_context_result(
            response_text,
            previous_meeting_id=previous_meeting_id,
        )

    except errors.APIError as e:
        print("===== GEMINI API ERROR =====")
        print(e)
        return []

    except Exception as e:
        print("===== GEMINI CONTEXT PARSE ERROR =====")
        print(e)
        return []


def _merge_changes(primary: list[dict], extra: list[dict]) -> list[dict]:
    merged = []
    seen = set()

    for change in primary + extra:
        key = (
            change.get("change_type"),
            str(change.get("previous_value") or "").lower(),
            str(change.get("new_value") or "").lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(change)

    return merged


def _find_related_task(
    db: Session,
    user_id: int,
    task_name: str,
    previous_meeting_id: Optional[int] = None,
):
    query = (
        db.query(Task)
        .join(Meeting)
        .filter(Meeting.user_id == user_id)
    )

    if previous_meeting_id is not None:
        previous_task = (
            query.filter(Task.meeting_id == previous_meeting_id)
            .order_by(Task.id.desc())
            .first()
        )
        if previous_task:
            return previous_task

    if task_name:
        return (
            query.filter(Task.description.ilike(f"%{task_name}%"))
            .order_by(Task.id.desc())
            .first()
        )

    return None


def persist_context_changes(
    db: Session,
    user_id: int,
    current_meeting_id: int,
    previous_meeting_id: Optional[int],
    changes: list[dict],
) -> list[dict]:
    """
    Insert PENDING ContextChange rows. Does not update tasks.
    """

    saved = []

    for change in changes:
        if not isinstance(change, dict):
            continue

        change_type = change.get("change_type")
        if not change_type or str(change_type).lower() in NO_CHANGE_TYPES:
            continue

        related_task = _find_related_task(
            db=db,
            user_id=user_id,
            task_name=change.get("task") or "",
            previous_meeting_id=previous_meeting_id,
        )

        new_change = ContextChange(
            meeting_id=current_meeting_id,
            previous_meeting_id=(
                change.get("previous_meeting_id")
                or previous_meeting_id
            ),
            change_type=change_type,
            task_id=related_task.id if related_task else None,
            previous_value=(
                str(change.get("previous_value"))
                if change.get("previous_value") is not None
                else None
            ),
            new_value=(
                str(change.get("new_value"))
                if change.get("new_value") is not None
                else None
            ),
            evidence=change.get("evidence"),
            status="pending",
        )

        db.add(new_change)
        db.commit()
        db.refresh(new_change)

        print("===== CONTEXT CONTINUITY: ContextChange created =====")
        print(
            f"id={new_change.id} type={new_change.change_type} "
            f"{new_change.previous_value} -> {new_change.new_value}"
        )
        print("===== CONTEXT CONTINUITY: ContextChange committed =====")

        saved.append({
            "id": new_change.id,
            "change_type": new_change.change_type,
            "task": change.get("task") or "",
            "task_id": new_change.task_id,
            "previous_value": new_change.previous_value,
            "new_value": new_change.new_value,
            "evidence": new_change.evidence,
            "status": new_change.status,
            "previous_meeting_id": new_change.previous_meeting_id,
            "meeting_id": new_change.meeting_id,
        })

    return saved


def run_context_continuity(
    db: Session,
    user_id: int,
    current_meeting: Meeting,
    previous_meeting: Optional[Meeting],
    current_transcript: str,
    use_gemini: bool = True,
) -> list[dict]:
    """
    Full Context Continuity pipeline used by meeting upload.
    """

    if previous_meeting is None:
        print("===== CONTEXT CONTINUITY: skipped, no previous meeting =====")
        return []

    if previous_meeting.user_id != user_id:
        print("===== CONTEXT CONTINUITY: skipped, user isolation =====")
        return []

    previous_text = meeting_context_text(previous_meeting)
    current_text = current_transcript or meeting_context_text(current_meeting)

    print("===== CONTEXT CONTINUITY: context extracted =====")
    print(f"previous_meeting_id={previous_meeting.id}")
    print(f"current_meeting_id={current_meeting.id}")

    changes = detect_context_changes(
        previous_text=previous_text,
        current_text=current_text,
        previous_meeting_id=previous_meeting.id,
    )

    if use_gemini:
        try:
            ai_changes = analyze_context_change(
                previous_context=previous_text,
                current_transcript=current_text,
                previous_meeting_id=previous_meeting.id,
            )
            changes = _merge_changes(changes, ai_changes)
        except Exception as exc:
            print("===== CONTEXT CONTINUITY: Gemini merge failed =====")
            print(exc)

    print("===== CONTEXT CONTINUITY: changes detected =====")
    print(f"count={len(changes)}")

    return persist_context_changes(
        db=db,
        user_id=user_id,
        current_meeting_id=current_meeting.id,
        previous_meeting_id=previous_meeting.id,
        changes=changes,
    )
