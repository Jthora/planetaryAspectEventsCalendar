import os
import subprocess

def main():
    input_file_part1 = "Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Part1.ics"
    input_file_part2 = "Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Part2.ics"
    output_folder = "./output"

    os.makedirs(output_folder, exist_ok=True)

    for year in range(2024, 2045):
        print(f"Processing year {year}...")
        try:
            subprocess.run([
                "python", "filter_ics_by_year_duo_lunar.py",
                input_file_part1, input_file_part2, str(year), output_folder
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing year {year}: {e}")

if __name__ == "__main__":
    main()