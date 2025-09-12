#!/usr/bin/env python3
"""
Bulgarian Orthodox Calendar Parser
Converts Bulgarian Orthodox calendar text file to CSV format.

Usage: python parse_calendar.py input.txt output.csv
"""

import csv
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional


class BulgarianCalendarParser:
    """Parser for Bulgarian Orthodox calendar text files."""
    
    def __init__(self):
        # Month name mapping from Bulgarian to numbers
        self.month_map = {
            'Януари': '01',
            'Февруари': '02', 
            'Март': '03',
            'Април': '04',
            'Май': '05',
            'Юни': '06',
            'Юли': '07',
            'Август': '08',
            'Септември': '09',
            'Октомври': '10',
            'Ноември': '11',
            'Декември': '12'
        }
        
        # Patterns for cleaning up feast content
        self.cleanup_patterns = [
            r'†\s*',  # Remove † symbol
            r'\*\s*',  # Remove * symbol
            r'\([^)]*\)',  # Remove parentheses content
            r'\[[^\]]*\]',  # Remove square bracket content
            r'Гл\.\s*\d+.*$',  # Remove chapter references
            r'утр\.\s*ев\..*$',  # Remove liturgical references
            r'лит\.\s*ев\..*$',  # Remove liturgical references
            r'ап\..*$',  # Remove apostolic references
            r'с\.\s*\d+.*$',  # Remove page references
            r'стр\.\s*\d+.*$',  # Remove page references
            r'т\.\s*\d+.*$',  # Remove tome references
            r'вечерта.*$',  # Remove evening service references
            r'сутринта.*$',  # Remove morning service references
            r'\s+',  # Multiple spaces to single space
        ]
    
    def clean_feast_content(self, content: str) -> str:
        """Clean feast content by removing liturgical annotations."""
        cleaned = content.strip()
        
        # Apply cleanup patterns
        for pattern in self.cleanup_patterns[:-1]:  # All except the last one
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Handle multiple spaces separately
        cleaned = re.sub(self.cleanup_patterns[-1], ' ', cleaned)
        
        return cleaned.strip()
    
    def is_wednesday_or_friday(self, date_str: str) -> bool:
        """Check if date falls on Wednesday or Friday."""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
            return date_obj.weekday() in [2, 4]  # Wednesday or Friday
        except ValueError:
            return False
    
    def is_strict_fast_day(self, date_str: str) -> bool:
        """Check if date is a strict fast day."""
        return date_str in ['2025-04-25', '2025-08-29']
    
    def parse_file(self, filename: str) -> List[Dict[str, str]]:
        """Parse the Bulgarian calendar text file."""
        feasts = []
        current_month = ''
        current_month_number = ''
        current_day = ''
        current_year = 2025
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except UnicodeDecodeError:
            print(f"Error: Could not decode '{filename}'. Please ensure it's UTF-8 encoded.")
            return []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a month name
            month_match = re.match(r'^(Януари|Февруари|Март|Април|Май|Юни|Юли|Август|Септември|Октомври|Ноември|Декември)', line)
            if month_match:
                current_month = month_match.group(1)
                current_month_number = self.month_map[current_month]
                print(f"Processing month: {current_month} ({current_month_number})")
                continue
            
            # Check if line starts with two digits (day number)
            day_match = re.match(r'^(\d{2})\s+(.+)', line)
            if day_match and current_month_number:
                current_day = day_match.group(1)
                # Skip this line as it just contains day number and day of week
                continue
            
            # If we have a current day and this line contains feast content
            if (current_day and current_month_number and line and 
                not re.match(r'^\d{2}', line) and 
                not re.match(r'^(Януари|Февруари|Март|Април|Май|Юни|Юли|Август|Септември|Октомври|Ноември|Декември)', line)):
                
                # feast_content = self.clean_feast_content(line)
                feast_content = line.strip()  # Keep original content as per requirements
                if feast_content and len(feast_content) > 3:
                    date_str = f"{current_year}-{current_month_number}-{current_day}"
                    
                    # Apply fasting rules according to specifications
                    show_fish = self.is_wednesday_or_friday(date_str)
                    show_oil = self.is_wednesday_or_friday(date_str)
                    show_strict_fast = self.is_strict_fast_day(date_str)
                    
                    feast = {
                        'date': date_str,
                        'feast_name': feast_content,
                        'description': '',  # Empty as per requirements
                        'show_fish': str(show_fish).lower(),
                        'show_oil': str(show_oil).lower(),
                        'show_strict_fast': str(show_strict_fast).lower()
                    }
                    
                    feasts.append(feast)
                    
                    if len(feasts) % 50 == 0:  # Progress indicator
                        print(f"Processed {len(feasts)} feasts...")
        
        print(f"Total feasts processed: {len(feasts)}")
        return feasts
    
    def write_csv(self, feasts: List[Dict[str, str]], output_filename: str) -> bool:
        """Write feasts data to CSV file."""
        if not feasts:
            print("No feast data to write.")
            return False
        
        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'feast_name', 'description', 'show_fish', 'show_oil', 'show_strict_fast']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                
                writer.writeheader()
                writer.writerows(feasts)
                
            print(f"Successfully wrote {len(feasts)} feasts to '{output_filename}'")
            return True
            
        except Exception as e:
            print(f"Error writing CSV file: {e}")
            return False
    
    def validate_output(self, feasts: List[Dict[str, str]]) -> None:
        """Validate the parsed output."""
        if not feasts:
            print("Warning: No feasts were parsed.")
            return
        
        # Check date range
        dates = [feast['date'] for feast in feasts]
        min_date = min(dates)
        max_date = max(dates)
        print(f"Date range: {min_date} to {max_date}")
        
        # Check for specific strict fast days
        strict_fast_days = [feast for feast in feasts if feast['show_strict_fast'] == 'true']
        print(f"Strict fast days found: {len(strict_fast_days)}")
        for day in strict_fast_days:
            print(f"  {day['date']}: {day['feast_name'][:50]}...")
        
        # Check Wednesday/Friday fasting
        wed_fri_days = [feast for feast in feasts if feast['show_fish'] == 'true']
        print(f"Wednesday/Friday fasting days: {len(wed_fri_days)}")


def main():
    """Main function to run the parser."""
    if len(sys.argv) != 3:
        print("Usage: python parse_calendar.py input.txt output.csv")
        print("Example: python parse_calendar.py 2025.txt orthodox_feasts.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Bulgarian Orthodox Calendar Parser")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    parser = BulgarianCalendarParser()
    
    # Parse the input file
    feasts = parser.parse_file(input_file)
    
    if not feasts:
        print("No feast data was parsed. Please check the input file format.")
        sys.exit(1)
    
    # Validate the output
    parser.validate_output(feasts)
    
    # Write to CSV
    if parser.write_csv(feasts, output_file):
        print(f"\nConversion completed successfully!")
        print(f"CSV file '{output_file}' is ready for use with your PHP script.")
    else:
        print("Failed to write CSV file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
