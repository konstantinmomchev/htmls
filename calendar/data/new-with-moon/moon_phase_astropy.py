import pandas as pd
from astropy.coordinates import get_body, GeocentricTrueEcliptic
from astropy.time import Time
import astropy.units as u
import numpy as np

def get_moon_phase(time: Time) -> float:
    """Return lunar phase as fraction 0..1 (0=new, 0.25=first quarter, 0.5=full, 0.75=last quarter)."""
    moon_ecl = get_body('moon', time).transform_to(GeocentricTrueEcliptic(obstime=time))
    sun_ecl = get_body('sun', time).transform_to(GeocentricTrueEcliptic(obstime=time))
    lon_diff = (moon_ecl.lon - sun_ecl.lon).wrap_at(360 * u.deg).to(u.deg).value
    return (lon_diff % 360) / 360.0

# Function to determine the moon phase number based on major phases
def get_phase_number(phase):
    # Threshold for phase matching (0.1 radians ~ 5.7 degrees, reasonable for daily check)
    threshold = 0.1
    if abs(phase - 0) < threshold or abs(phase - 1) < threshold:
        return 1  # New Moon
    elif abs(phase - 0.25) < threshold:
        return 2  # First Quarter
    elif abs(phase - 0.5) < threshold:
        return 3  # Full Moon
    elif abs(phase - 3*0.25) < threshold:  # 0.75
        return 4  # Last Quarter
    else:
        return 0  # No major phase change

# Read the CSV file (tab-separated) with quoting preserved
df = pd.read_csv('orthodox_feasts.csv', sep='\t', quoting=1, keep_default_na=False)

# Sort by date to ensure chronological order
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Calculate moon phase for each date (first pass - get all phases)
all_phases = []
for date in df['date']:
    current_phase = get_phase_number(get_moon_phase(Time(date)))
    all_phases.append(current_phase)

# Second pass: only mark the last day of each phase (when it's about to change)
phases = []
for i in range(len(all_phases)):
    # Check if next day has a different phase (and current day has a phase)
    if all_phases[i] != 0:
        # If this is the last row or next day has different phase, mark it
        if i == len(all_phases) - 1 or all_phases[i + 1] != all_phases[i]:
            phases.append(all_phases[i])
        else:
            phases.append(0)
    else:
        phases.append(0)

df['moon_phase'] = phases

# Convert date back to string format for writing
df['date'] = df['date'].dt.strftime('%Y-%m-%d')

# Write back to the CSV file with quotes for all columns except date
# We'll write manually to control quoting per column
with open('orthodox_feasts.csv', 'w', encoding='utf-8') as f:
    # Write header
    headers = df.columns.tolist()
    f.write('\t'.join(headers) + '\n')

    # Write data rows
    for _, row in df.iterrows():
        values = []
        for col in headers:
            val = row[col]
            # Handle NaN/None values - convert to empty string
            if pd.isna(val) or val is None:
                val = ''
            else:
                val = str(val)

            # Add quotes for all columns except 'date'
            if col == 'date':
                values.append(val)
            else:
                # Escape any existing quotes in the value
                val = val.replace('"', '""')
                values.append(f'"{val}"')
        f.write('\t'.join(values) + '\n')

print("Moon phases updated in orthodox_feasts.csv")
print(f"Total phase changes recorded: {sum(1 for p in phases if p != 0)}")
