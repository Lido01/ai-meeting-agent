import json

from app.services.context_continuity import analyze_context_change


# ============================================================
# TEST DATA
# ============================================================

# This represents information from an older meeting.
previous_meeting = """
Previous meeting:

John is responsible for finishing the payment API.
The deadline is August 28, 2026.
"""


# This represents the new/current meeting.
current_meeting = """
Current meeting:

John said that he needs more time to finish the payment API.
He will now finish it on September 3, 2026.
"""


# ============================================================
# RUN CONTEXT ANALYSIS
# ============================================================

print("========================================")
print("TESTING CONTEXT CONTINUITY")
print("========================================")

try:

    result = analyze_context_change(
        previous_context=previous_meeting,
        current_transcript=current_meeting,
        previous_meeting_id=10
    )

    print("\n===== CONTEXT ANALYSIS RESULT =====")

    # Pretty-print the result
    print(json.dumps(result, indent=4))

except Exception as e:

    print("\n===== ERROR =====")
    print(str(e))