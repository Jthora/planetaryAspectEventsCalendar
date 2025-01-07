import os
import argparse
import logging
from datetime import datetime
from ics import Calendar
from tqdm import tqdm

def setup_logging(output_folder):
    """
    Sets up error logging to a file in the output folder.

    Args:
        output_folder (str): Path to the output folder.

    Returns:
        str: Path to the log file.
    """
    log_file = os.path.join(output_folder, "error_log.txt")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_file

def parse_ics_file(file_path):
    """
    Parses an .ics file and returns a Calendar object.

    Args:
        file_path (str): Path to the .ics file.

    Returns:
        Calendar: Parsed calendar object, or None if parsing fails.
    """
    try:
        with open(file_path, 'r') as file:
            return Calendar(file.read())
    except Exception as e:
        logging.error(f"Failed to parse .ics file: {e}")
        print(f"Error: Failed to parse the input file. Check the log for details.")
        return None

def filter_events(calendar, year):
    """
    Filters events in the calendar by the specified year.

    Args:
        calendar (Calendar): The calendar object to filter.
        year (int): The target year for filtering.

    Returns:
        list: A list of events occurring in the specified year.
    """
    filtered_events = []
    errors = []
    for event in tqdm(calendar.events, desc="Filtering events"):
        try:
            if event.begin.year == year:
                filtered_events.append(event)
        except Exception as e:
            error_message = f"Skipping event '{event.name if event else 'Unknown'}': {e}"
            logging.warning(error_message)
            errors.append(error_message)
    return filtered_events, errors

def write_ics_file(events, output_file):
    """
    Writes the filtered events to a new .ics file.

    Args:
        events (list): List of filtered events.
        output_file (str): Path to the output .ics file.
    """
    try:
        new_calendar = Calendar(events=events)
        with open(output_file, 'w') as file:
            file.writelines(new_calendar)
        print(f"Filtered events successfully saved to: {output_file}")
    except Exception as e:
        logging.error(f"Failed to write .ics file: {e}")
        print("Error: Failed to save the filtered events.")

def create_output_folder(base_folder):
    """
    Creates an output folder if it doesn't already exist.

    Args:
        base_folder (str): Path to the desired output folder.

    Returns:
        str: Path to the created output folder.
    """
    os.makedirs(base_folder, exist_ok=True)
    return base_folder

def summarize_results(filtered_count, total_count, errors, log_file):
    """
    Summarizes the results of the filtering operation.

    Args:
        filtered_count (int): Number of events successfully filtered.
        total_count (int): Total number of events processed.
        errors (list): List of errors encountered during processing.
        log_file (str): Path to the error log file.
    """
    print("\n--- Summary ---")
    print(f"Total events processed: {total_count}")
    print(f"Filtered events: {filtered_count}")
    if errors:
        print(f"Errors encountered: {len(errors)} (See {log_file} for details)")
    else:
        print("No errors encountered.")

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Filter .ics events by a specific year.")
    parser.add_argument("input_file", help="Path to the input .ics file.")
    parser.add_argument("target_year", type=int, help="Year to filter events by.")
    parser.add_argument("output_folder", nargs="?", default="./output", help="Optional folder to save results.")
    args = parser.parse_args()

    # Input validation
    if not os.path.exists(args.input_file):
        print("Error: The input file does not exist.")
        return

    # Prepare output folder and logging
    output_folder = create_output_folder(args.output_folder)
    log_file = setup_logging(output_folder)

    # Parse the calendar
    print("Parsing the .ics file...")
    calendar = parse_ics_file(args.input_file)
    if not calendar:
        print("Error: Failed to parse the input file.")
        return

    # Filter events
    print(f"Filtering events for the year {args.target_year}...")
    filtered_events, errors = filter_events(calendar, args.target_year)

    # Write filtered events to a new .ics file
    output_file = os.path.join(output_folder, f"filtered_events_{args.target_year}.ics")
    write_ics_file(filtered_events, output_file)

    # Summarize results
    summarize_results(len(filtered_events), len(calendar.events), errors, log_file)

if __name__ == "__main__":
    main()