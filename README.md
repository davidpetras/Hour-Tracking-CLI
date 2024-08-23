# Hour Tracker CLI Tool

## Overview

This command-line tool allows users to track and report working hours, including PTO, across multiple time codes. It supports generating daily, weekly, monthly, and yearly reports, as well as tracking PTO accumulation and usage. The tool is designed to help users keep track of their work hours efficiently and simplify reporting for timesheets.

## Features

- **Track Hours**: Record hours worked for different time codes.
- **Time Code Management**: Add new time codes as needed.
- **Reports**: Generate reports on daily, weekly, monthly, and yearly bases.
- **PTO Tracking**: Track PTO accumulation based on a 89% utilization rate.
- **12-hour Limit**: Enforce a maximum of 12 tracked hours per day.

## Prerequisites

- Python 3.9.6 or higher

## Usage

### Add a Timecode

To add a specific timecode:

```sh
ht add_code <time_code>
```

### Track Hours

To track hours for a specific time code:

```sh
ht track <duration> <time_code>
```
### Generate Report

To generate a daily, weekly, monthly, yearly report of hours tracked:

```sh
ht report -d <YYYY-MM-DD> -t <type>
```
### PTO Report

To generate a report of PTO used/earned:

```sh
ht pto
```

## Error Handling

If incorrect inputs are used, the script will return detailed error messages with guidance on how to correct the input. Use:

```sh
ht --help
```

## Data Storage

Tracked hours are stored in a JSON file (tracked_hours.json) in the current directory. This file is automatically created and updated as you use the tool.
