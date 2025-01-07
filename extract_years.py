import os
import subprocess

def main():
    input_file = "AstrologicalAspects-2024to2056-majorsAndMinors-GalacticCenter-Interpretations.ics"
    output_folder = "./output"

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for year in range(2024, 2057):
        print(f"Extracting events for the year {year}...")
        subprocess.run([
            "python3", "filter_ics_by_year.py", input_file, str(year), output_folder
        ])

if __name__ == "__main__":
    main()