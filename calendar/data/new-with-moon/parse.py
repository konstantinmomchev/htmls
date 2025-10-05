import csv

input_file = './orthodox_feasts_quoted.csv'
output_file = './orthodox_feasts_quoted_moon.csv'

with open(input_file, 'r', encoding='utf-8-sig') as infile, \
        open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['date', 'feast_name', 'description', 'fast_type', 'moon_phase']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t', quotechar='"', quoting=csv.QUOTE_STRINGS)
    writer.writeheader()
    for row in reader:
        writer.writerow({
            'date': row['date'],
            'feast_name': row['feast_name'],
            'description': row['description'],
            'fast_type': row['fast_type'],
            'moon_phase': ''
        })