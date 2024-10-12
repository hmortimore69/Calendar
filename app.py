from flask import Flask, jsonify, render_template
from icalendar import Calendar
from dateutil.rrule import rrulestr
from datetime import datetime, timedelta

app = Flask(__name__)


def preprocess_ics(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    processed_lines = []
    categories_buffer = []

    for line in lines:
        if line.startswith("CATEGORIES:"):
            categories_buffer.append(line.strip())
        else:
            if categories_buffer:
                combined_categories = ",".join(
                    [cat.split(":", 1)[1] for cat in categories_buffer]
                )
                processed_lines.append(f"CATEGORIES:{combined_categories}\n")
                categories_buffer = []
            processed_lines.append(line)

    return "".join(processed_lines)


# Preprocess the .ics file
ics_content = preprocess_ics("calendar.ics")

# Parse the .ics file using icalendar
calendar = Calendar.from_ical(ics_content)

# Extract events and handle recurrence rules
events = []
for component in calendar.walk():
    if component.name == "VEVENT":
        event_data = {
            "title": str(component.get("SUMMARY")),
            "start": component.get("DTSTART").dt.isoformat(),
            "end": (
                component.get("DTEND").dt.isoformat()
                if component.get("DTEND")
                else None
            ),
            "description": str(component.get("DESCRIPTION")),
        }
        rrule = component.get("RRULE")
        if rrule:
            rrule_str = rrule.to_ical().decode("utf-8")
            rule = rrulestr(rrule_str, dtstart=component.get("DTSTART").dt)
            for dt in rule:
                event_data = {
                    "title": str(component.get("SUMMARY")),
                    "start": dt.isoformat(),
                    "end": (
                        (
                            dt
                            + (component.get("DTEND").dt - component.get("DTSTART").dt)
                        ).isoformat()
                        if component.get("DTEND")
                        else None
                    ),
                    "description": str(component.get("DESCRIPTION")),
                }
                events.append(event_data)
        else:
            events.append(event_data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/events")
def get_events():
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True)
