import pandas as pd
from datetime import datetime

# Constants
REFERENCE_POSITION = 26.854  # Galactic Center position in degrees (year 2000)
PRECESSION_RATE = 0.01397    # Degrees per year due to precession
REFERENCE_YEAR = 2000        # Base year for Galactic Center alignment

# Zodiac Signs and Degree Ranges
ZODIAC_SIGNS = [
    ('Aries', 0, 30), ('Taurus', 30, 60), ('Gemini', 60, 90),
    ('Cancer', 90, 120), ('Leo', 120, 150), ('Virgo', 150, 180),
    ('Libra', 180, 210), ('Scorpio', 210, 240), ('Sagittarius', 240, 270),
    ('Capricorn', 270, 300), ('Aquarius', 300, 330), ('Pisces', 330, 360)
]

# Aspect to degree offset mapping
ASPECT_OFFSETS = {
    'Conjunction': 0,
    'Sextile': 60,
    'Square': 90,
    'Trine': 120,
    'Opposition': 180
}

# Map abbreviated zodiac names to full names
ZODIAC_ABBREVIATIONS = {
    'Ari': 'Aries', 'Tau': 'Taurus', 'Gem': 'Gemini', 'Can': 'Cancer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Scorpio',
    'Sag': 'Sagittarius', 'Cap': 'Capricorn', 'Aqu': 'Aquarius', 'Pis': 'Pisces'
}

# Functions
def fractional_year(date_str, time_str):
    date_time = datetime.strptime(f"{date_str} {time_str}", "%b %d, %Y %H:%M")
    year = date_time.year
    start_of_year = datetime(year, 1, 1)
    day_of_year = (date_time - start_of_year).total_seconds() / 86400
    return year + (day_of_year / 365.25)

def calculate_ayanamsa(fractional_year):
    return REFERENCE_POSITION - (fractional_year - REFERENCE_YEAR) * PRECESSION_RATE

def adjust_position(position, ayanamsa):
    corrected_position = position - ayanamsa
    return corrected_position % 360  # Wrap around 0-360

def get_zodiac(position):
    for sign, start, end in ZODIAC_SIGNS:
        if start <= position < end:
            return sign
    return 'Pisces'

def calculate_body_position(moon_position, aspect, original_body_zodiac, moon_zodiac):
    """
    Calculate the Body Position based on:
    - Corrected Moon Position
    - Aspect Offset (positive or negative based on relative zodiac positions)
    - Original Body Zodiac to determine direction
    """
    # Map abbreviated zodiac to full name
    original_body_zodiac_full = ZODIAC_ABBREVIATIONS.get(original_body_zodiac, original_body_zodiac)
    
    offset = ASPECT_OFFSETS.get(aspect, 0)
    
    # Determine if offset should be positive or negative
    moon_index = [z[0] for z in ZODIAC_SIGNS].index(moon_zodiac)
    body_index = [z[0] for z in ZODIAC_SIGNS].index(original_body_zodiac_full)
    
    if body_index >= moon_index:
        corrected_body_position = (moon_position + offset) % 360
    else:
        corrected_body_position = (moon_position - offset) % 360
    
    return corrected_body_position

# Process the Data
def process_data(input_file, output_file):
    df = pd.read_csv(input_file)
    
    for index, row in df.iterrows():
        # Calculate Ayanamsa
        frac_year = fractional_year(row['Date'], row['Time'])
        ayanamsa = calculate_ayanamsa(frac_year)
        
        # Correct Moon Position and Zodiac
        corrected_moon_position = adjust_position(row['Moon Position'], ayanamsa)
        corrected_moon_zodiac = get_zodiac(corrected_moon_position)
        
        # Correct Body Position and Zodiac
        corrected_body_position = calculate_body_position(
            corrected_moon_position, row['Astrological Aspect'],
            row['Body Zodiac Word'], corrected_moon_zodiac
        )
        corrected_body_zodiac = get_zodiac(corrected_body_position)
        
        # Update DataFrame
        df.at[index, 'Moon Position'] = corrected_moon_position
        df.at[index, 'Moon Zodiac Word'] = corrected_moon_zodiac
        df.at[index, 'Body Zodiac Word'] = corrected_body_zodiac
    
    df.to_csv(output_file, index=False)
    print(f"Updated file saved to: {output_file}")

# Main Execution
if __name__ == "__main__":
    input_file = 'Lunar_Aspects.csv'       # Input file
    output_file = 'Updated_Lunar_Aspects.csv'  # Output file
    process_data(input_file, output_file)