import csv
import datetime
import ephem

def get_phase_code(year: int, month: int, day: int):
    """
    Returns an integer 0-7 for the moon phase, matching the logic of moon_phase_script.py:
    0: New Moon, 1: Waxing Crescent, 2: First Quarter, 3: Waxing Gibbous,
    4: Full Moon, 5: Waning Gibbous, 6: Last Quarter, 7: Waning Crescent
    """
    date = ephem.Date(datetime.date(year, month, day))
    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)
    lunation = (date - pnm) / (nnm - pnm)  # 0-1
    if lunation < 0:
        lunation += 1
    age = lunation * 29.53
    if age < 1.84566:
        return 0  # New Moon
    elif age < 5.53699:
        return 1  # Waxing Crescent
    elif age < 9.22831:
        return 2  # First Quarter
    elif age < 12.91963:
        return 3  # Waxing Gibbous
    elif age < 16.61096:
        return 4  # Full Moon
    elif age < 20.30228:
        return 5  # Waning Gibbous
    elif age < 23.99361:
        return 6  # Last Quarter
    elif age < 27.68493:
        return 7  # Waning Crescent
    else:
        return 0  # New Moon

# input_file = 'orthodox_feasts.csv'
input_file = 'orthodox_feasts_quoted_moon.csv'
output_file = 'orthodox_feasts_with_ephem_moon.csv'

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile, delimiter='\t', quotechar='"')
    # Remove any existing 'ephem_moon_phase_change' column to avoid duplicates
    fieldnames = [fn for fn in reader.fieldnames if fn != 'moon_phase'] + ['moon_phase']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t', quotechar='"', quoting=csv.QUOTE_STRINGS)
    writer.writeheader()

    prev_phase = None
    for row in reader:
        date_str = row['date']
        try:
            year, month, day = map(int, date_str.split('-'))
            phase_code = get_phase_code(year, month, day)
        except Exception as e:
            phase_code = None
            print(f"Error processing date {date_str}: {e}")
        if prev_phase is None or phase_code != prev_phase:
            row['moon_phase'] = phase_code
        else:
            row['moon_phase'] = -1
        prev_phase = phase_code
        writer.writerow(row)

print(f"Done. Output written to {output_file}")
