from app.services.date_parser import parse_deadline


test_dates = [
    "September 3, 2026",
    "August 28, 2026",
    "2026-09-03",
    "Sep 3, 2026",
    "August 30, 2026",
]


for value in test_dates:

    result = parse_deadline(value)

    print(
        f"{value} -> {result}"
    )