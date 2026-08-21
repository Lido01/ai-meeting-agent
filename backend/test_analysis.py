from app.services.meeting_analysis import analyze_meeting


# Test transcript
transcript = """
John said he will finish the payment API by September 5.

Sarah will prepare the QA test plan by September 3.

The team discussed the product launch.
"""


# Send transcript to Gemini
result = analyze_meeting(transcript)


# Display result
print("\nMEETING ANALYSIS:")
print(result)


from app.services.meeting_analysis import analyze_meeting


transcript = """
John: I will finish the payment API by September 5.

Sarah: I will prepare the QA test plan.

Mike: I will update the documentation.

Manager: John, please also test the payment API before the deadline.
"""


result = analyze_meeting(transcript)

print("\n===== FINAL RESULT =====")
print(result)