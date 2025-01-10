import pandas as pd

# Define mappings for Zodiac signs, Entities, and Aspects
zodiac_emoji = {
    "Aries": "♈️", "Taurus": "♉️", "Gemini": "♊️", "Cancer": "♋️", 
    "Leo": "♌️", "Virgo": "♍️", "Libra": "♎️", "Scorpio": "♏️", 
    "Sagittarius": "♐️", "Capricorn": "♑️", "Aquarius": "♒️", "Pisces": "♓️"
}

entity_glyphs = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", 
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", 
    "Neptune": "♆", "Pluto": "♇", "Node": "☊", "SouthNode": "☋", 
    "Chiron": "⚷", "Ceres": "⚸", "Pallas": "⚹", "Juno": "⚳", 
    "Vesta": "⚴", "Hygiea": "⚵", "Eris": "⚶", "Lilith": "⚸"
}

aspect_glyphs = {
    "Conjunction": "☌", "Opposition": "☍", "Square": "□", 
    "Trine": "△", "Sextile": "⚹", "Quincunx": "⚻", 
    "Semisextile": "⚺", "Semisquare": "∠", "Tri-Octile": "⚼", 
    "Quintile": "⍫", "Biquintile": "⍩"
}

# Function to generate Symbol Title and Word Title
def generate_titles(row):
    # Extract data from the row
    first_zodiac = row['First Zodiac']
    first_entity = row['First Entity']
    aspect = row['Aspect']
    second_entity = row['Second Entity']
    second_zodiac = row['Second Zodiac']

    # Create Symbol Title
    symbol_title = f"{zodiac_emoji.get(first_zodiac, first_zodiac)} " \
                   f"{entity_glyphs.get(first_entity, first_entity)} " \
                   f"{aspect_glyphs.get(aspect, aspect)} " \
                   f"{entity_glyphs.get(second_entity, second_entity)} " \
                   f"{zodiac_emoji.get(second_zodiac, second_zodiac)}"

    # Create Word Title
    word_title = f"{first_zodiac} {first_entity} {aspect} {second_entity} {second_zodiac}"

    return pd.Series([symbol_title, word_title])

# Load the CSV file
file_path = '/mnt/data/Astrological_Aspects_with_Natures_and_Modalities.csv'
data = pd.read_csv(file_path)

# Apply the function to create new columns
data[['Symbol Title', 'Word Title']] = data.apply(generate_titles, axis=1)

# Save the transformed data to a new CSV
output_file_path = '/mnt/data/Transformed_Astrological_Aspects.csv'
data.to_csv(output_file_path, index=False)

print(f"Transformed CSV saved to: {output_file_path}")