import sys
import traceback
from ics import Calendar, Event
from datetime import datetime

def filter_lunar_aspect_events_by_year(input_file, output_file, year):
    try:
        with open(input_file, 'r') as file:
            calendar = Calendar(file.read())
    except Exception as e:
        print(f"Error reading input file: {input_file}")
        print(f"Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

    filtered_events = []
    for event in calendar.events:
        try:
            if event.begin.year == year:
                filtered_events.append(event)
        except AttributeError as e:
            print(f"Skipping malformed event: {event}")
            print(f"Exception: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"Error processing event: {event}")
            print(f"Exception: {e}")
            traceback.print_exc()

    filtered_calendar = Calendar(events=filtered_events)

    try:
        with open(output_file, 'w') as file:
            file.writelines(filtered_calendar.serialize_iter())
    except Exception as e:
        print(f"Error writing output file: {output_file}")
        print(f"Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter_lunar_aspect_events.py <input_file> <year>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        year = int(sys.argv[2])
    except ValueError:
        print("Year must be an integer.")
        sys.exit(1)

    output_file = f'Filtered_Lunar_Aspect_Events_{year}.ics'

    filter_lunar_aspect_events_by_year(input_file, output_file, year)