import csv
from datetime import datetime, timedelta

def update_orthodox_feasts():
    input_file = 'orthodox_feasts_original.csv'
    output_file = 'orthodox_feasts.csv'

    # Read the CSV file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    # Update each row according to the rules
    for row in rows:
        date_str = row['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Rule 1: If Wednesday or Friday, set show_fish to true
        if date_obj.weekday() in [2, 4]:  # Wednesday=2, Friday=4
            row['show_fish'] = 'true'

        # Rule 2: From March 03 and next 49 days set show_oil to true
        march_03 = datetime(date_obj.year, 3, 3)
        if march_03 <= date_obj <= march_03 + timedelta(days=49):
            row['show_oil'] = 'true'

        # Rule 3: From August 01 and next 15 days set show_oil to true
        august_01 = datetime(date_obj.year, 8, 1)
        if august_01 <= date_obj <= august_01 + timedelta(days=15):
            row['show_oil'] = 'true'

        # Rule 4: For Jan 05 and August 29 set show_strict_fast to true
        if (date_obj.month == 1 and date_obj.day == 5) or \
                (date_obj.month == 8 and date_obj.day == 29):
            row['show_strict_fast'] = 'true'

        # Rule 5: For November 15, 17, 18, 19 set show_oil to true
        if date_obj.month == 11 and date_obj.day in [15, 17, 18, 19]:
            row['show_oil'] = 'true'

        # Rule 6: From November 15 to December 24 set show_oil to true
        nov_15 = datetime(date_obj.year, 11, 15)
        dec_24 = datetime(date_obj.year, 12, 24)
        if nov_15 <= date_obj <= dec_24:
            row['show_oil'] = 'true'

        # Rule 7: For December 20, 21, 22, 23, 24 set show_oil to true
        if date_obj.month == 12 and date_obj.day in [20, 21, 22, 23, 24]:
            row['show_oil'] = 'true'

        # Rule 8: For March 03 to March 07, set show_strict_fast to true
        march_07 = datetime(date_obj.year, 3, 7)
        if march_03 <= date_obj <= march_07:
            row['show_strict_fast'] = 'true'

        # Rule 9: For April 14 to April 16, set show_strict_fast to true
        april_14 = datetime(date_obj.year, 4, 14)
        april_16 = datetime(date_obj.year, 4, 16)
        if april_14 <= date_obj <= april_16:
            row['show_strict_fast'] = 'true'

        # Rule 10: From June 15 to June 29 set show_fish to true
        june_15 = datetime(date_obj.year, 6, 15)
        june_29 = datetime(date_obj.year, 6, 29)
        if june_15 <= date_obj <= june_29:
            row['show_fish'] = 'true'

        if 'Разрешава се риба' in row['feast_name']:
           row['show_fish'] = 'true'
           row['show_strict_fast'] = 'false'
           row['show_oil'] = 'false'

        if 'Блажи се' in row['feast_name']:
           row['show_fish'] = 'false'
           row['show_strict_fast'] = 'false'
           row['show_oil'] = 'false'

        # Rule 11: If feast_name contains '†', downgrade the fast level
        if '†' in row['feast_name']:
            if row['show_strict_fast'] == 'true':
              row['show_strict_fast'] = 'false'
              row['show_oil'] = 'true'
            elif row['show_oil'] == 'true':
              row['show_oil'] = 'false'
              row['show_fish'] = 'true'
            elif row['show_fish'] == 'true':
              row['show_fish'] = 'false'


    # Write the updated data back to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['date', 'feast_name', 'description', 'show_fish', 'show_oil', 'show_strict_fast']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {len(rows)} records in {output_file}")

if __name__ == "__main__":
    update_orthodox_feasts()