from app.services.meeting_agent import create_meeting_agent


transcript = """
John: I will finish the payment API.

Sarah: I will prepare the QA test plan.
"""


context = """
Previous Meeting:
John was responsible for starting the payment API.

Previous Task:
John - Payment API - in_progress
"""


result = create_meeting_agent(
    transcript,
    context
)

print("\n===== AI AGENT RESULT =====")
print(result)