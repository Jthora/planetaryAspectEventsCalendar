import sys
from icalendar import Calendar, Event
from icalendar.parser import ContentLine
from datetime import datetime

def validate_ics(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for common issues
        if "BEGIN:VCALENDAR" not in content or "END:VCALENDAR" not in content:
            print("Error: Missing VCALENDAR block.")
            return False
        
        if "BEGIN:VEVENT" not in content or "END:VEVENT" not in content:
            print("Error: Missing VEVENT block.")
            return False

        # Parse the calendar
        cal = Calendar.from_ical(content)
        
        # Validate each event
        uids = set()
        for component in cal.walk():
            if component.name == "VEVENT":
                if not component.get('DTSTART'):
                    print("Error: Missing DTSTART in an event.")
                    return False
                if not component.get('SUMMARY'):
                    print("Error: Missing SUMMARY in an event.")
                    return False
                if not component.get('UID'):
                    print("Error: Missing UID in an event.")
                    return False
                if not component.get('DTSTAMP'):
                    print("Error: Missing DTSTAMP in an event.")
                    return False
                if not component.get('DESCRIPTION'):
                    print("Error: Missing DESCRIPTION in an event.")
                    return False
                if not component.get('STATUS'):
                    print("Error: Missing STATUS in an event.")
                    return False

                # Check for unique UID
                uid = component.get('UID')
                if uid in uids:
                    print(f"Error: Duplicate UID found: {uid}")
                    return False
                uids.add(uid)

                # Validate date-time fields
                try:
                    dtstart = component.decoded('DTSTART')
                    if not isinstance(dtstart, datetime):
                        print(f"Error: Invalid DTSTART format: {dtstart}")
                        return False
                except Exception as e:
                    print(f"Error: Invalid DTSTART format: {e}")
                    return False

                try:
                    dtstamp = component.decoded('DTSTAMP')
                    if not isinstance(dtstamp, datetime):
                        print(f"Error: Invalid DTSTAMP format: {dtstamp}")
                        return False
                except Exception as e:
                    print(f"Error: Invalid DTSTAMP format: {e}")
                    return False

        print("ICS file is valid.")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_ics.py <path_to_ics_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validate_ics(file_path)