import unittest
from datetime import date

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.context_change import ContextChange
from app.models.meeting import Meeting
from app.models.task import Task
from app.models.user import User
from app.services.auth_service import create_access_token
from app.services.context_continuity import (
    detect_context_changes,
    extract_assignment_facts,
    get_comparable_previous_meeting,
    parse_ai_context_result,
    run_context_continuity,
)


MEET_1 = (
    "Rahma is assigned to implement JWT authentication "
    "with a deadline of September 10."
)

MEET_2 = (
    "Ali is now responsible for implementing JWT authentication. "
    "The deadline has been changed to September 15."
)

MEET_SAME = (
    "Rahma is assigned to implement JWT authentication "
    "with a deadline of September 10."
)


class ContextDetectionTests(unittest.TestCase):

    def test_no_previous_meeting_facts_means_no_change(self):
        changes = detect_context_changes(
            previous_text="",
            current_text=MEET_2,
            previous_meeting_id=None,
        )
        self.assertEqual(changes, [])

    def test_same_owner_and_deadline_means_no_change(self):
        changes = detect_context_changes(
            previous_text=MEET_1,
            current_text=MEET_SAME,
            previous_meeting_id=1,
        )
        self.assertEqual(changes, [])

    def test_owner_changed_rahma_to_ali(self):
        previous = (
            "Rahma is assigned to implement JWT authentication "
            "with a deadline of September 10."
        )
        current = (
            "Ali is now responsible for implementing JWT authentication "
            "with a deadline of September 10."
        )
        changes = detect_context_changes(previous, current, 1)
        types = [item["change_type"] for item in changes]
        self.assertIn("assignee", types)
        owner = next(item for item in changes if item["change_type"] == "assignee")
        self.assertEqual(owner["previous_value"], "Rahma")
        self.assertEqual(owner["new_value"], "Ali")

    def test_deadline_changed(self):
        previous = (
            "Rahma is assigned to implement JWT authentication "
            "with a deadline of September 10."
        )
        current = (
            "Rahma is assigned to implement JWT authentication. "
            "The deadline has been changed to September 15."
        )
        changes = detect_context_changes(previous, current, 1)
        types = [item["change_type"] for item in changes]
        self.assertIn("deadline", types)
        deadline = next(item for item in changes if item["change_type"] == "deadline")
        self.assertIn("September 10", deadline["previous_value"])
        self.assertIn("September 15", deadline["new_value"])

    def test_owner_and_deadline_changed(self):
        changes = detect_context_changes(MEET_1, MEET_2, 10)
        types = sorted(item["change_type"] for item in changes)
        self.assertEqual(types, ["assignee", "deadline"])

    def test_malformed_ai_output_does_not_crash(self):
        self.assertEqual(parse_ai_context_result("not json"), [])
        self.assertEqual(parse_ai_context_result(None), [])
        self.assertEqual(parse_ai_context_result(123), [])
        self.assertEqual(
            parse_ai_context_result('{"change_type":"none"}'),
            [],
        )
        parsed = parse_ai_context_result(
            '[{"change_type":"assignee","previous_value":"Rahma","new_value":"Ali","task":"JWT"}]'
        )
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["change_type"], "assignee")

    def test_extract_facts(self):
        first = extract_assignment_facts(MEET_1)
        second = extract_assignment_facts(MEET_2)
        self.assertEqual(first["owner"], "Rahma")
        self.assertEqual(second["owner"], "Ali")
        self.assertIsNotNone(parse_deadline_safe(first["deadline"]))
        self.assertIsNotNone(parse_deadline_safe(second["deadline"]))


def parse_deadline_safe(value):
    from app.services.date_parser import parse_deadline
    return parse_deadline(value)


class ContextPersistenceTests(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()
        self.user_ids = []
        self.meeting_ids = []
        self.task_ids = []
        self.change_ids = []

    def tearDown(self):
        try:
            self.db.rollback()

            if self.meeting_ids:
                existing = (
                    self.db.query(ContextChange.id)
                    .filter(
                        ContextChange.meeting_id.in_(self.meeting_ids)
                    )
                    .all()
                )
                self.change_ids.extend(row[0] for row in existing)

            if self.change_ids:
                self.db.query(ContextChange).filter(
                    ContextChange.id.in_(self.change_ids)
                ).delete(synchronize_session=False)

            if self.task_ids:
                self.db.query(Task).filter(
                    Task.id.in_(self.task_ids)
                ).delete(synchronize_session=False)

            if self.meeting_ids:
                self.db.query(Task).filter(
                    Task.meeting_id.in_(self.meeting_ids)
                ).delete(synchronize_session=False)
                self.db.query(Meeting).filter(
                    Meeting.id.in_(self.meeting_ids)
                ).delete(synchronize_session=False)

            if self.user_ids:
                self.db.query(User).filter(
                    User.id.in_(self.user_ids)
                ).delete(synchronize_session=False)

            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            self.db.close()

    def _user(self, email):
        user = User(
            name="Context Test",
            email=email,
            role="user",
            password_hash="unused",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.user_ids.append(user.id)
        return user

    def _meeting(self, user, title, transcript):
        meeting = Meeting(
            title=title,
            user_id=user.id,
            transcript_text=transcript,
            summary_text=transcript,
            status="analyzed",
        )
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        self.meeting_ids.append(meeting.id)
        return meeting

    def test_no_previous_meeting_persists_nothing(self):
        user = self._user("ctx-none@example.com")
        current = self._meeting(user, "Only Meeting", MEET_2)
        previous = get_comparable_previous_meeting(
            self.db,
            user.id,
            exclude_meeting_id=current.id,
        )
        saved = run_context_continuity(
            db=self.db,
            user_id=user.id,
            current_meeting=current,
            previous_meeting=previous,
            current_transcript=MEET_2,
            use_gemini=False,
        )
        self.assertEqual(saved, [])

    def test_owner_and_deadline_are_persisted_pending(self):
        user = self._user("ctx-both@example.com")
        previous = self._meeting(user, "MEET_1 Auth", MEET_1)
        current = self._meeting(user, "MEET_2 Auth", MEET_2)
        saved = run_context_continuity(
            db=self.db,
            user_id=user.id,
            current_meeting=current,
            previous_meeting=previous,
            current_transcript=MEET_2,
            use_gemini=False,
        )
        self.change_ids.extend(item["id"] for item in saved)
        types = sorted(item["change_type"] for item in saved)
        self.assertEqual(types, ["assignee", "deadline"])
        self.assertTrue(all(item["status"] == "pending" for item in saved))

        owner = next(item for item in saved if item["change_type"] == "assignee")
        deadline = next(item for item in saved if item["change_type"] == "deadline")
        self.assertEqual(owner["previous_value"], "Rahma")
        self.assertEqual(owner["new_value"], "Ali")
        self.assertIn("September 10", deadline["previous_value"])
        self.assertIn("September 15", deadline["new_value"])

    def test_user_isolation(self):
        user_a = self._user("ctx-a@example.com")
        user_b = self._user("ctx-b@example.com")
        self._meeting(user_a, "A previous", MEET_1)
        current_b = self._meeting(user_b, "B current", MEET_2)

        previous_for_b = get_comparable_previous_meeting(
            self.db,
            user_b.id,
            exclude_meeting_id=current_b.id,
        )
        self.assertIsNone(previous_for_b)

        saved = run_context_continuity(
            db=self.db,
            user_id=user_b.id,
            current_meeting=current_b,
            previous_meeting=previous_for_b,
            current_transcript=MEET_2,
            use_gemini=False,
        )
        self.assertEqual(saved, [])

    def test_confirm_and_reject(self):
        user = self._user("ctx-confirm@example.com")
        previous = self._meeting(user, "MEET_1 Auth", MEET_1)
        current = self._meeting(user, "MEET_2 Auth", MEET_2)
        task = Task(
            description="Implement JWT authentication",
            assigned_to="Rahma",
            deadline=date(2026, 9, 10),
            status="open",
            meeting_id=previous.id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self.task_ids.append(task.id)

        saved = run_context_continuity(
            db=self.db,
            user_id=user.id,
            current_meeting=current,
            previous_meeting=previous,
            current_transcript=MEET_2,
            use_gemini=False,
        )
        self.assertGreaterEqual(len(saved), 2)
        self.change_ids.extend(item["id"] for item in saved)

        token = create_access_token(user.id)
        client = TestClient(app)

        pending = client.get(
            "/context-changes/pending",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(pending.status_code, 200)
        pending_rows = pending.json()
        self.assertGreaterEqual(len(pending_rows), 2)

        all_rows = client.get(
            "/context-changes/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(all_rows.status_code, 200)
        self.assertGreaterEqual(len(all_rows.json()), 2)

        owner = next(item for item in saved if item["change_type"] == "assignee")
        deadline = next(item for item in saved if item["change_type"] == "deadline")

        confirmed = client.post(
            f"/context-changes/{owner['id']}/confirm",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json()["status"], "confirmed")

        rejected = client.post(
            f"/context-changes/{deadline['id']}/reject",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(rejected.json()["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
