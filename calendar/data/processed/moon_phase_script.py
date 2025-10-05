import csv
from datetime import datetime, timedelta

# Simple moon phase calculation (0=new, 1=first quarter, 2=full, 3=last quarter)
def moon_phase(date):
    # This algorithm is approximate and returns 0-7 (8 phases)
    # Source: https://stackoverflow.com/a/60192338
    year = date.year
    month = date.month
    day = date.day
    if month < 3:
        year -= 1
        month += 12
    K1 = int(365.25 * (year + 4712))
    K2 = int(30.6 * (month + 1))
    K3 = int(((year / 100) + 49) * 0.75) - 38
    JD = K1 + K2 + day + 59  # Julian Day
    JD -= K3  # Correction for Gregorian Calendar
    IP = (JD - 2451550.1) / 29.530588853
    IP -= int(IP)
    if IP < 0:
        IP += 1
    age = IP * 29.53
    # 0: new, 1: first quarter, 2: full, 3: last quarter
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

input_file = 'orthodox_feasts.csv'
output_file = 'orthodox_feasts_with_moon.csv'

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['moon_phase_change']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    prev_phase = None
    for row in reader:
        date_str = row['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        phase = moon_phase(date_obj)
        if prev_phase is None or phase != prev_phase:
            row['moon_phase_change'] = phase
        else:
            row['moon_phase_change'] = -1
        prev_phase = phase
        writer.writerow(row)

print(f"Done. Output written to {output_file}")

