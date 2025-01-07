import pandas as pd

nature_meanings = {
    "Water": "This is a deeply emotional and intuitive time.",
    "Earth": "This period brings practical and grounded energy.",
    "Air": "This phase emphasizes intellect and communication.",
    "Fire": "This time ignites passion and bold action."
}

modality_meanings = {
    "Fixed": "This is a time for determination and staying the course.",
    "Cardinal": "This period promotes new beginnings and action.",
    "Mutable": "This phase supports adaptability and change."
}

zodiac_meanings = {
    "Aries": "Aries energizes, bringing boldness, action, and assertiveness.",
    "Taurus": "Taurus stabilizes fostering patience, endurance, and material focus.",
    "Gemini": "Gemini energizes, enhancing communication and intellectual curiosity.",
    "Cancer": "Cancer nurtures, encouraging emotional security and care.",
    "Leo": "Leo inspires confidence, radiating leadership and creative vitality.",
    "Virgo": "Virgo refines, promoting precision, analysis, and practical focus.",
    "Libra": "Libra balances, emphasizing fairness, beauty, and connection.",
    "Scorpio": "Scorpio transforms, revealing deep emotional and energetic renewal.",
    "Sagittarius": "Sagittarius expands, fostering optimism, exploration, and wisdom.",
    "Capricorn": "Capricorn disciplines, promoting ambition, responsibility, and endurance.",
    "Aquarius": "Aquarius innovates, encouraging uniqueness, rebellion, and new ideas.",
    "Pisces": "Pisces softens the body, enhancing compassion, dreams, and spiritual connections."
}

entity_meanings = {
    "Sun": "The Sun represents the core self, vitality, and life purpose.",
    "Moon": "The Moon symbolizes emotions, intuition, and subconscious needs.",
    "Mercury": "Mercury governs communication, intellect, and reasoning.",
    "Venus": "Venus relates to love, beauty, harmony, and values.",
    "Mars": "Mars signifies action, energy, passion, and assertiveness.",
    "Jupiter": "Jupiter expands horizons, bringing luck, wisdom, and optimism.",
    "Saturn": "Saturn represents discipline, structure, responsibility, and karma.",
    "Uranus": "Uranus symbolizes innovation, rebellion, and sudden changes.",
    "Neptune": "Neptune governs dreams, spirituality, and illusions.",
    "Pluto": "Pluto signifies transformation, power, and rebirth.",
    "Node": "The North Node represents destiny and life purpose.",
    "SouthNode": "The South Node represents past habits and lessons.",
    "Chiron": "Chiron embodies healing, vulnerability, and inner wounds.",
    "Ceres": "Ceres symbolizes nurturing, care, and abundance.",
    "Pallas": "Pallas represents wisdom, strategy, and creativity.",
    "Juno": "Juno relates to commitment, partnerships, and fairness.",
    "Vesta": "Vesta governs dedication, focus, and spiritual devotion.",
    "Eris": "Eris represents discord, transformation, and hidden power.",
    "Lilith": "Lilith symbolizes the shadow self, independence, and primal energy.",
    "Chiron": "Chiron embodies healing, vulnerability, and inner wounds."
}

aspect_meanings = {
    # Major Aspects
    "Conjunction": "A Conjunction (☌) fuses energies, creating intense focus and blending influences.",
    "Opposition": "An Opposition (☍) highlights tension, contrast, and opportunities for balance.",
    "Square": "A Square (□) challenges and creates dynamic friction, encouraging growth.",
    "Trine": "A Trine (△) offers harmony, ease, and natural support between energies.",
    "Sextile": "A Sextile (⚹) facilitates opportunities and collaboration with some effort.",
    "Quincunx": "A Quincunx (⚻) brings awkward adjustments and unrecognized opportunities.",
    "Semisextile": "A Semisextile (⚺) offers subtle opportunities requiring conscious effort.",
    "Semisquare": "A Semisquare (∠) introduces mild tension and the need for small adjustments.",
    "Tri-Octile": "A Tri-Octile (⚼) signifies hidden challenges and potential breakthroughs.",
    "Quintile": "A Quintile (⍫) fosters creative expression and unique talents.",
    "Biquintile": "A Biquintile (⍩) emphasizes artistic mastery and refined creativity."
}

modality_combination_meanings = {
    ("Cardinal", "Cardinal"): "Two initiators collide, sparking new beginnings but potential clashes.",
    ("Cardinal", "Fixed"): "Action meets determination, driving focused progress toward a goal.",
    ("Cardinal", "Mutable"): "Initiation meets adaptability, creating dynamic momentum.",
    ("Fixed", "Fixed"): "Stubborn energies combine, leading to unyielding determination or stalemates.",
    ("Fixed", "Mutable"): "Persistence meets adaptability, encouraging steady progress with flexibility.",
    ("Mutable", "Mutable"): "Two flexible forces combine, fostering change and adaptability.",
    ("Cardinal", "Fixed"): "Action meets determination, driving focused progress toward a goal.",
    ("Mutable", "Fixed"): "Persistence meets adaptability, encouraging steady progress with flexibility.",
    ("Cardinal", "Mutable"): "Initiation meets adaptability, creating dynamic momentum."
}

nature_combination_meanings = {
    ("Water", "Water"): "This union deepens emotional bonds and enhances intuition.",
    ("Water", "Fire"): "The emotional meets the passionate, creating dynamic energy.",
    ("Water", "Earth"): "Emotions find grounding and stability in practical matters.",
    ("Water", "Air"): "Emotions mix with intellect, encouraging understanding.",
    ("Fire", "Fire"): "This pairing ignites passion and energy, fueling bold action.",
    ("Fire", "Earth"): "Energy meets practicality, driving ambition toward goals.",
    ("Fire", "Air"): "Passion and intellect combine, fostering creative ideas.",
    ("Earth", "Earth"): "A grounded, stable connection fosters security and consistency.",
    ("Earth", "Air"): "Practicality meets intellect, enabling effective plans.",
    ("Air", "Air"): "A highly intellectual pairing fosters communication and innovation.",
    ("Water", "Fire"): "The emotional meets the passionate, creating dynamic energy.",
    ("Water", "Air"): "Emotions mix with intellect, encouraging understanding.",
    ("Earth", "Air"): "Practicality meets intellect, enabling effective plans."
}

entity_combination_meanings = {
    ("Sun", "Mercury"): "The relationship between vitality and intellect highlights clarity and communication dynamics.",
    ("Sun", "Venus"): "The connection between vitality and harmony explores creativity and relational themes.",
    ("Sun", "Mars"): "The interaction between vitality and action underscores drive and initiative.",
    ("Sun", "Chiron"): "The link between vitality and healing examines themes of self-awareness and growth.",
    ("Sun", "Jupiter"): "The relationship between vitality and expansion focuses on vision and potential.",
    ("Sun", "Saturn"): "The bond between vitality and discipline addresses structure and limitations.",
    ("Sun", "Uranus"): "The connection between vitality and innovation considers individuality and disruption.",
    ("Sun", "Neptune"): "The interaction between vitality and spirituality navigates intuition and imagination.",
    ("Sun", "Pluto"): "The relationship between vitality and transformation explores depth and renewal.",
    ("Sun", "Node"): "The alignment between vitality and destiny reflects themes of purpose and karmic direction.",
    ("Sun", "Lilith"): "The interaction between vitality and the shadow self reveals themes of authenticity and independence.",
    
    ("Mercury", "Venus"): "The relationship between intellect and harmony explores communication and aesthetic values.",
    ("Mercury", "Mars"): "The interaction between intellect and action examines assertiveness in expression.",
    ("Mercury", "Chiron"): "The connection between intellect and healing delves into themes of self-awareness through thought.",
    ("Mercury", "Jupiter"): "The relationship between intellect and expansion reflects on perspective and understanding.",
    ("Mercury", "Saturn"): "The bond between intellect and discipline addresses focus and constraints in thinking.",
    ("Mercury", "Uranus"): "The interaction between intellect and innovation considers breakthroughs and disruptions in ideas.",
    ("Mercury", "Neptune"): "The link between intellect and spirituality explores imagination and abstraction.",
    ("Mercury", "Pluto"): "The relationship between intellect and transformation uncovers themes of depth and insight.",
    ("Mercury", "Node"): "The connection between intellect and destiny reflects themes of purposeful communication.",
    ("Mercury", "Lilith"): "The interaction between intellect and the shadow self examines honesty and hidden truths.",
    
    ("Venus", "Mars"): "The relationship between love and passion navigates dynamics in attraction and action.",
    ("Venus", "Jupiter"): "The interaction between love and expansion explores themes of growth in connection.",
    ("Venus", "Saturn"): "The connection between love and discipline examines responsibility and boundaries in relationships.",
    ("Venus", "Uranus"): "The link between love and innovation considers unconventional expressions of affection.",
    ("Venus", "Neptune"): "The relationship between love and spirituality reflects idealism and imagination in connection.",
    ("Venus", "Pluto"): "The bond between love and transformation explores depth and intensity in relationships.",
    ("Venus", "Node"): "The alignment between love and destiny examines themes of relational purpose.",
    ("Venus", "Lilith"): "The interaction between love and the shadow self reflects on self-expression and autonomy.",
    
    ("Mars", "Jupiter"): "The relationship between passion and expansion navigates themes of action and ambition.",
    ("Mars", "Saturn"): "The connection between passion and discipline examines strategic effort and constraint.",
    ("Mars", "Uranus"): "The bond between passion and innovation explores unconventional approaches to action.",
    ("Mars", "Neptune"): "The relationship between passion and spirituality reflects on inspired effort and vision.",
    ("Mars", "Pluto"): "The interaction between passion and transformation delves into themes of power and depth.",
    ("Mars", "Node"): "The connection between passion and destiny explores themes of purposeful action.",
    ("Mars", "Lilith"): "The interaction between passion and the shadow self reflects themes of independence and assertiveness.",
    
    ("Jupiter", "Saturn"): "The relationship between expansion and discipline explores themes of growth within structure.",
    ("Jupiter", "Uranus"): "The bond between expansion and innovation examines shifts and visionary change.",
    ("Jupiter", "Neptune"): "The relationship between expansion and spirituality navigates themes of inspiration and dreams.",
    ("Jupiter", "Pluto"): "The interaction between expansion and transformation reflects depth and significant change.",
    ("Jupiter", "Node"): "The alignment between expansion and destiny considers themes of exploration and purpose.",
    ("Jupiter", "Lilith"): "The connection between expansion and the shadow self delves into themes of bold expression.",
    
    ("Saturn", "Uranus"): "The interaction between discipline and innovation explores tension between tradition and disruption.",
    ("Saturn", "Neptune"): "The link between discipline and spirituality examines practicality and abstraction.",
    ("Saturn", "Pluto"): "The bond between discipline and transformation considers enduring and profound change.",
    ("Saturn", "Node"): "The alignment between discipline and destiny reflects themes of karmic responsibility.",
    ("Saturn", "Lilith"): "The connection between discipline and the shadow self examines themes of self-control and mastery.",
    
    ("Uranus", "Neptune"): "The relationship between innovation and spirituality explores themes of creativity and imagination.",
    ("Uranus", "Pluto"): "The bond between innovation and transformation navigates themes of revolution and change.",
    ("Uranus", "Node"): "The connection between innovation and destiny reflects themes of unique breakthroughs.",
    ("Uranus", "Lilith"): "The relationship between innovation and the shadow self examines themes of fearless expression.",
    
    ("Neptune", "Pluto"): "The interaction between spirituality and transformation reflects themes of depth and renewal.",
    ("Neptune", "Node"): "The alignment between spirituality and destiny considers themes of intuitive direction.",
    ("Neptune", "Lilith"): "The connection between spirituality and the shadow self reflects themes of authenticity.",
    
    ("Pluto", "Node"): "The relationship between transformation and destiny examines themes of profound change and karma.",
    ("Pluto", "Lilith"): "The bond between transformation and the shadow self delves into themes of self-awareness.",
    
    ("Node", "Lilith"): "The alignment between destiny and the shadow self reflects themes of karmic authenticity.",

    ("Mars", "Chiron"): "The relationship between passion and healing explores themes of action through vulnerability.",
    ("Venus", "Chiron"): "The interaction between love and healing reflects the depth of emotional connections.",
    ("Lilith", "Chiron"): "The combination of the shadow self and healing highlights profound personal transformation.",
    ("Chiron", "Node"): "The alignment between healing and destiny suggests karmic growth and purpose.",
    ("Mars", "Lilith"): "The relationship between passion and the shadow self navigates assertive independence.",
    ("Venus", "Lilith"): "The bond between love and the shadow self reflects themes of autonomy in relationships.",
    ("Jupiter", "Chiron"): "The relationship between expansion and healing reflects opportunities for growth through understanding vulnerabilities.",
    ("Saturn", "Chiron"): "The connection between discipline and healing explores lessons learned through structure and perseverance.",
    ("Pluto", "Chiron"): "The bond between transformation and healing highlights profound renewal and addressing deep wounds.",
    ("Neptune", "Chiron"): "The interaction between spirituality and healing emphasizes dreams, compassion, and emotional growth.",
    ("Uranus", "Chiron"): "The relationship between innovation and healing navigates breakthroughs and unconventional approaches to personal growth."
}


# File paths
csv_file_path = '/mnt/data/AstrologicalAspects-2024to2056-majorsAndMinors-WithTitles.csv'
output_file_path = '/mnt/data/AstrologicalAspects_with_Interpretations.csv'
log_file_path = '/mnt/data/interpretation_log.txt'

# Initialize log
def initialize_log(file_path):
    with open(file_path, 'w') as log_file:
        log_file.write("Interpretation Process Log\n")
        log_file.write("==========================\n\n")

# Log a message
def log_message(file_path, message):
    with open(file_path, 'a') as log_file:
        log_file.write(f"{message}\n")

# Validate CSV columns
def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        log_message(log_file_path, f"Critical error: Missing required columns: {', '.join(missing_columns)}")
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

# Helper function for combination meanings
def get_combination_meaning(value1, value2, dictionary, row_index):
    if (value1, value2) in dictionary:
        return dictionary[(value1, value2)]
    elif (value2, value1) in dictionary:  # Handle tuple flipping
        return dictionary[(value2, value1)]
    else:
        log_message(log_file_path, f"Row {row_index}: No combination meaning found for ({value1}, {value2})")
        return ""

# Function to generate interpretations
def generate_interpretation(row, row_index):
    interpretations = []

    # Single-value lookups
    for col, dictionary in [
        ('First Nature', nature_meanings),
        ('Second Nature', nature_meanings),
        ('First Modality', modality_meanings),
        ('Second Modality', modality_meanings),
        ('First Zodiac', zodiac_meanings),
        ('Second Zodiac', zodiac_meanings),
        ('First Entity', entity_meanings),
        ('Second Entity', entity_meanings),
        ('Aspect', aspect_meanings),
    ]:
        value = row[col]
        meaning = dictionary.get(value, "")
        if not meaning:
            log_message(log_file_path, f"Row {row_index}: No meaning found for {col}='{value}'")
        if meaning:
            interpretations.append(meaning)

    # Combination lookups
    for (col1, col2, dictionary) in [
        ('First Nature', 'Second Nature', nature_combination_meanings),
        ('First Modality', 'Second Modality', modality_combination_meanings),
        ('First Entity', 'Second Entity', entity_combination_meanings),
    ]:
        value1, value2 = row[col1], row[col2]
        meaning = get_combination_meaning(value1, value2, dictionary, row_index)
        if meaning:
            interpretations.append(meaning)

    # Combine interpretations into a paragraph
    combined_interpretation = " ".join(filter(None, interpretations))
    if not combined_interpretation:
        log_message(log_file_path, f"Row {row_index}: No interpretations generated.")
        return "No interpretation available for this row."
    return combined_interpretation

# Main script execution
if __name__ == "__main__":
    # Initialize log
    initialize_log(log_file_path)

    # Load CSV into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Validate required columns
    required_columns = [
        'First Nature', 'Second Nature',
        'First Modality', 'Second Modality',
        'First Zodiac', 'Second Zodiac',
        'First Entity', 'Second Entity',
        'Aspect'
    ]
    try:
        validate_columns(df, required_columns)
    except ValueError as e:
        print(e)
        exit(1)

    # Apply the function row by row
    df['Interpretations'] = df.apply(lambda row: generate_interpretation(row, row.name), axis=1)

    # Save the updated CSV
    df.to_csv(output_file_path, index=False)

    # Final log summary
    log_message(log_file_path, f"Rows processed: {len(df)}")
    log_message(log_file_path, "Interpretation process completed successfully.")
    print(f"Updated CSV saved to: {output_file_path}")
    print(f"Log file saved to: {log_file_path}")