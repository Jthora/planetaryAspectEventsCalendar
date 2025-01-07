import re
import sys

def analyze_ics_file(file_path):
    """
    Analyzes an ICS file to count the number of events and determine the year range.

    Args:
        file_path (str): Path to the .ics file.

    Returns:
        dict: A dictionary containing the total number of events and the year range.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Count the number of events based on the "BEGIN:VEVENT" marker
        events = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', content, re.DOTALL)
        total_events = len(events)

        # Extract all years from "DTSTART" fields
        years = re.findall(r'DTSTART:(\d{4})', content)
        if years:
            min_year = min(years)
            max_year = max(years)
            year_range = (min_year, max_year)
        else:
            year_range = None

        return {
            "total_events": total_events,
            "year_range": year_range
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 icsEventsCounter.py <path_to_ics_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = analyze_ics_file(file_path)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Total Events: {result['total_events']}")
        if result['year_range']:
            print(f"Year Range: {result['year_range'][0]} to {result['year_range'][1]}")
        else:
            print("No valid years found.")