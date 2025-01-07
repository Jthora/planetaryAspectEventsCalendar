import os

def rename_files(output_folder):
    for filename in os.listdir(output_folder):
        if filename.endswith(".ics") and "filtered_events" in filename:
            new_filename = filename.replace("filtered_events", "planetary_aspect_events")
            old_file_path = os.path.join(output_folder, filename)
            new_file_path = os.path.join(output_folder, new_filename)
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")

def main():
    output_folder = "./output"
    rename_files(output_folder)

if __name__ == "__main__":
    main()