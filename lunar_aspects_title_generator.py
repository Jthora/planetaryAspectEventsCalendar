import pandas as pd

# Define mappings for Zodiac symbols, Aspect symbols, and Body symbols
zodiac_symbols = {
    'Aries': '♈️', 'Taurus': '♉️', 'Gemini': '♊️', 'Cancer': '♋️',
    'Leo': '♌️', 'Virgo': '♍️', 'Libra': '♎️', 'Scorpio': '♏️',
    'Sagittarius': '♐️', 'Capricorn': '♑️', 'Aquarius': '♒️', 'Pisces': '♓️'
}

aspect_symbols = {
    'Conjunction': '☌', 'Sextile': '⚹', 'Square': '□',
    'Trine': '△', 'Opposition': '☍'
}

body_symbols = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'Chiron': '⚷', 'Lilith': '⚸'
}

moon_symbol = '☽'

# Load the original dataset
file_path = 'Lunar_Aspects-GalacticCenter-NaturesAndModalities.csv'
data = pd.read_csv(file_path)

# Function to create Symbol Title
def create_symbol_title(row):
    moon_zodiac = zodiac_symbols.get(row['Moon Zodiac Word'], '?')
    aspect = aspect_symbols.get(row['Astrological Aspect'], '?')
    body_name = body_symbols.get(row['Body Name'], row['Body Name'])  # Use symbol if available
    body_zodiac = zodiac_symbols.get(row['Body Zodiac Word'], '?')
    
    return f"{moon_zodiac} {moon_symbol} {aspect} {body_name} {body_zodiac}"

# Function to create Word Title
def create_word_title(row):
    return f"{row['Moon Zodiac Word']} Moon {row['Astrological Aspect']} {row['Body Name']} {row['Body Zodiac Word']}"

# Apply the functions to generate new columns
data['Symbol Title'] = data.apply(create_symbol_title, axis=1)
data['Word Title'] = data.apply(create_word_title, axis=1)

# Save the modified DataFrame to a new CSV file
output_file = 'Lunar_Aspects_With_Titles.csv'
data.to_csv(output_file, index=False)

print(f"File saved as