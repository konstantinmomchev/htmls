import pandas as pd
from astropy.coordinates import get_moon_phase
from astropy.time import Time

# Function to determine the moon phase number
def get_phase_number(phase):
    # Threshold for phase matching (0.1 radians ~ 5.7 degrees, reasonable for daily check)
    threshold = 0.1
    if abs(phase - 0) < threshold or abs(phase - 1) < threshold:
        return 1  # New Moon
    elif abs(phase - 0.25) < threshold:
        return 2  # First Quarter
    elif abs(phase - 0.5) < threshold:
        return 3  # Full Moon
    elif abs(phase - 0.75) < threshold:
        return 4  # Last Quarter
    else:
        return 0  # No major phase change

# Read the CSV file (tab-separated)
df = pd.read_csv('orthodox_feasts.csv', sep='\t')

# Calculate moon phase for each date and assign the number
df['moon_phase'] = df['date'].apply(lambda d: get_phase_number(get_moon_phase(Time(d))))

# Write back to the CSV file
df.to_csv('orthodox_feasts.csv', sep='\t', index=False)

print("Moon phases updated in orthodox_feasts.csv")
8