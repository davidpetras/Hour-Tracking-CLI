#!/usr/bin/env python3

import argparse
import json
from datetime import timedelta, date, datetime
import os

# File to store tracked hours
TRACKED_HOURS_FILE = 'tracked_hours.json'
MAX_HOURS_PER_DAY = 12  # 12-hour boundary
TOTAL_WORKING_HOURS_YEAR = 2080  # Total working hours in a year
UTILIZATION_RATE = 0.89  # Utilization rate
TOTAL_UTILIZED_HOURS_YEAR = TOTAL_WORKING_HOURS_YEAR * UTILIZATION_RATE

def load_tracked_hours():
    if not os.path.exists(TRACKED_HOURS_FILE):
        return {}, []

    try:
        with open(TRACKED_HOURS_FILE, 'r') as file:
            data = json.load(file)
            tracked_hours = {day: {code: timedelta(seconds=seconds) for code, seconds in times.items()} for day, times in data.get('tracked_hours', {}).items()}
            time_codes = data.get('time_codes', [])
            return tracked_hours, time_codes
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error loading tracked hours: {e}")
        return {}, []

def save_tracked_hours(tracked_hours, time_codes):
    with open(TRACKED_HOURS_FILE, 'w') as file:
        data = {
            'tracked_hours': {day: {code: duration.total_seconds() for code, duration in times.items()} for day, times in tracked_hours.items()},
            'time_codes': time_codes
        }
        json.dump(data, file)

def parse_duration(duration_str):
    try:
        hours = 0
        minutes = 0
        if 'h' in duration_str and 'm' in duration_str:
            hours, minutes = map(int, duration_str.replace('h', ' ').replace('m', '').split())
        elif 'h' in duration_str:
            hours = int(duration_str.replace('h', ''))
        elif 'm' in duration_str:
            minutes = int(duration_str.replace('m', ''))
        else:
            raise ValueError
        return timedelta(hours=hours, minutes=minutes)
    except ValueError:
        raise ValueError("Invalid duration format. Use 'XhYm', 'Xh', or 'Ym' format.")

def add_hours(tracked_hours, duration, time_code, current_date, time_codes):
    if current_date not in tracked_hours:
        tracked_hours[current_date] = {code: timedelta() for code in time_codes}
    
    total_hours_today = sum(duration.total_seconds() for duration in tracked_hours[current_date].values()) / 3600
    new_total_hours = total_hours_today + duration.total_seconds() / 3600

    if new_total_hours > MAX_HOURS_PER_DAY:
        raise ValueError(f"Cannot track hours. Total hours for {current_date} would exceed the {MAX_HOURS_PER_DAY}-hour limit.")
    
    tracked_hours[current_date][time_code] += duration

def track_hours(duration, time_code):
    current_date = str(date.today())
    tracked_hours, time_codes = load_tracked_hours()

    if time_code not in time_codes:
        print(f"Invalid time code '{time_code}'. Please add the time code first.")
        return
    
    duration_td = parse_duration(duration)
    add_hours(tracked_hours, duration_td, time_code, current_date, time_codes)
    save_tracked_hours(tracked_hours, time_codes)
    print(f"Tracked {duration_td} hours for time code '{time_code}' on {current_date}")

def generate_report(report_date=None, report_type=None):
    tracked_hours, time_codes = load_tracked_hours()
    
    if report_type == 'daily':
        if report_date not in tracked_hours:
            print(f"No hours tracked for {report_date}")
            return
        report_data = {report_date: tracked_hours[report_date]}
    elif report_type in ['weekly', 'monthly', 'yearly']:
        report_data = {}
        target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        if report_type == 'weekly':
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif report_type == 'monthly':
            start_date = target_date.replace(day=1)
            if target_date.month == 12:
                end_date = target_date.replace(month=1, day=1, year=target_date.year + 1) - timedelta(days=1)
            else:
                end_date = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        elif report_type == 'yearly':
            start_date = target_date.replace(month=1, day=1)
            end_date = target_date.replace(month=12, day=31)

        for day in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
            day_str = str(day)
            if day_str in tracked_hours:
                report_data[day_str] = tracked_hours[day_str]

        if not report_data:
            print(f"No hours tracked for the {report_type} starting from {start_date} to {end_date}")
            return
    else:
        print("Invalid report type. Available options are 'daily', 'weekly', 'monthly', 'yearly'")
        return

    print(f"{report_type.capitalize()} report for {report_date}:")
    for day, times in report_data.items():
        print(f"Date: {day}")
        for time_code, duration in times.items():
            total_minutes = duration.total_seconds() // 60
            rounded_duration = timedelta(minutes=(total_minutes // 15) * 15)
            print(f"  - {time_code}: {rounded_duration}")

def generate_pto_report():
    tracked_hours, _ = load_tracked_hours()
    total_working_seconds = sum(
        duration.total_seconds()
        for times in tracked_hours.values()
        for code, duration in times.items()
        if code != 'PTO'
    )
    total_working_hours = total_working_seconds / 3600
    total_pto_seconds = sum(
        duration.total_seconds()
        for times in tracked_hours.values()
        for code, duration in times.items()
        if code == 'PTO'
    )
    total_pto_hours = total_pto_seconds / 3600
    earned_pto_hours = total_working_hours * (1 - UTILIZATION_RATE)
    remaining_pto_hours = earned_pto_hours - total_pto_hours

    print(f"PTO Report:")
    print(f"  - Total Working Hours: {total_working_hours:.2f} hours")
    print(f"  - Total PTO Earned: {earned_pto_hours:.2f} hours")
    print(f"  - Total PTO Used: {total_pto_hours:.2f} hours")
    print(f"  - PTO Remaining: {remaining_pto_hours:.2f} hours")

def add_time_code(new_code):
    tracked_hours, time_codes = load_tracked_hours()
    if new_code in time_codes:
        print(f"Time code '{new_code}' already exists.")
        return
    time_codes.append(new_code)
    for day in tracked_hours:
        tracked_hours[day][new_code] = timedelta()
    save_tracked_hours(tracked_hours, time_codes)
    print(f"Added new time code '{new_code}'.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Command-line tool for hour tracking")
    subparsers = parser.add_subparsers(dest='command', help="Commands")

    track_parser = subparsers.add_parser('track', help="Track hours for a specific time code")
    track_parser.add_argument('duration', help="Duration of hours to track (e.g., '2h30m'). Format: XhYm where X is hours and Y is minutes.")
    track_parser.add_argument('time_code', help="Time code for tracking hours.")

    report_parser = subparsers.add_parser('report', help="Generate a report of tracked hours for a specific date or period")
    report_parser.add_argument('-d', '--date', required=True, help="Date for the report (format: YYYY-MM-DD)")
    report_parser.add_argument('-t', '--type', choices=['daily', 'weekly', 'monthly', 'yearly'], default='daily', help="Type of report: daily, weekly, monthly, or yearly")

    pto_parser = subparsers.add_parser('pto', help="Generate a PTO report")

    add_code_parser = subparsers.add_parser('add_code', help="Add a new time code")
    add_code_parser.add_argument('new_code', help="New time code to add")

    return parser.parse_args()

def main():
    args = parse_arguments()
    try:
        if args.command == 'track':
            track_hours(args.duration, args.time_code)
        elif args.command == 'report':
            generate_report(report_date=args.date, report_type=args.type)
        elif args.command == 'pto':
            generate_pto_report()
        elif args.command == 'add_code':
            add_time_code(args.new_code)
        else:
            print("Invalid command. Use --help for usage information.")
    except ValueError as ve:
        print(f"Error: {ve}")
        print("Use the following format for tracking hours:")
        print("  ht track <duration> <time_code>")
        print("  Examples: 'ht track 2h VA_GSA_PLATFORM_OY2', 'ht track 45m PTO'")
        print("Use the following format for generating a report:")
        print("  ht report -d <date> -t <type>")
        print("  Example: 'ht report -d 2023-06-01 -t daily'")
        print("           'ht report -d 2023-06-01 -t weekly'")
        print("           'ht report -d 2023-06-01 -t monthly'")
        print("           'ht report -d 2023-06-01 -t yearly'")
        print("Use the following format for generating a PTO report:")
        print("  ht pto")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
