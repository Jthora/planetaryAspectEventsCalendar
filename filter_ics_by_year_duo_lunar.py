import os
import argparse
import logging
from datetime import datetime
from ics import Calendar
from tqdm import tqdm

def setup_logging(output_folder):
    log_file = os.path.join(output_folder, "error_log.txt")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_file

def parse_ics_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return Calendar(file.read())
    except Exception as e:
        logging.error(f"Failed to parse .ics file: {e}")
        print(f"Error: Failed to parse the input file. Check the log for details.")
        return None

def filter_events(calendar, year):
    filtered_events = []
    errors = []
    for event in tqdm(calendar.events, desc="Filtering events"):
        try:
            if event.begin.year == year:
                filtered_events.append(event)
        except Exception as e:
            errors.append(e)
            logging.error(f"Error processing event: {e}")
    return filtered_events, errors

def write_ics_file(events, output_file):
    try:
        calendar = Calendar(events=events)
        with open(output_file, 'w') as file:
            file.writelines(calendar)
    except Exception as e:
        logging.error(f"Failed to write .ics file: {e}")
        print(f"Error: Failed to write the output file. Check the log for details.")

def create_output_folder(base_folder):
    os.makedirs(base_folder, exist_ok=True)
    return base_folder

def summarize_results(filtered_count, total_count, errors, log_file):
    print("\n--- Summary ---")
    print(f"Total events processed: {total_count}")
    print(f"Filtered events: {filtered_count}")
    if errors:
        print(f"Errors encountered: {len(errors)}. Check the log file at {log_file} for details.")
    else:
        print("No errors encountered.")

def main():
    parser = argparse.ArgumentParser(description="Filter .ics events by a specific year.")
    parser.add_argument("input_files", nargs='+', help="Paths to the input .ics files.")
    parser.add_argument("target_year", type=int, help="Year to filter events by.")
    parser.add_argument("output_folder", nargs="?", default="./output", help="Optional folder to save results.")
    args = parser.parse_args()

    if not all(os.path.exists(file) for file in args.input_files):
        print("Error: One or more input files do not exist.")
        return

    output_folder = create_output_folder(args.output_folder)
    log_file = setup_logging(output_folder)

    all_events = []
    for input_file in args.input_files:
        calendar = parse_ics_file(input_file)
        if calendar:
            all_events.extend(calendar.events)

    print(f"Filtering events for the year {args.target_year}...")
    filtered_events, errors = filter_events(Calendar(events=all_events), args.target_year)

    output_file = os.path.join(output_folder, f"filtered_events_{args.target_year}.ics")
    write_ics_file(filtered_events, output_file)

    summarize_results(len(filtered_events), len(all_events), errors, log_file)

if __name__ == "__main__":
    main()