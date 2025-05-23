# KSÍ Data Fetcher

A Python tool to fetch and analyze football match data from the Icelandic Football Association (KSÍ) API.

## Features

- Fetches match data from KSÍ's SOAP API
- Scrapes tournament information from KSÍ's website
- Groups matches by tournament
- Calculates win/draw/loss statistics
- Supports fetching data across multiple years

## Prerequisites

- Python 3.8 or higher
- pipenv (for dependency management)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arnarbjonsson/ksi-data-fetcher.git
cd ksi-data-fetcher
```

2. Install dependencies using pipenv:
```bash
pipenv install
```

## Usage

The script accepts several named parameters to customize the data fetching:

```bash
pipenv run python main.py [--start-year YEAR] [--end-year YEAR] [--team TEAM_ID] [--age-group AGE_GROUP_ID] [--tournament-type TYPE_ID]
```

Parameters:
- `--start-year`: Year to start fetching from (default: 2024)
- `--end-year`: Year to end fetching at (default: 2024)
- `--team`: Team ID to filter matches for (optional)
- `--age-group`: Age group ID (default: 420 for 5th flokkur)
- `--tournament-type`: Tournament type ID (default: 61 for Íslandsmót)

Examples:
```bash
# Fetch all 5th flokkur matches from 2024
pipenv run python main.py

# Fetch Grótta's matches (team ID 170) for 2023-2024
pipenv run python main.py --start-year 2023 --end-year 2024 --team 170

# Fetch matches for a specific age group (e.g., 4th flokkur, ID: 4)
pipenv run python main.py --age-group 4

# Fetch matches from a specific tournament type (e.g., Faxaflóamót, ID: 2340)
pipenv run python main.py --tournament-type 2340
```

## Output Format

The script outputs:
- Total matches found
- Matches grouped by tournament
- For each tournament:
  - Match details (date, teams, scores)
  - Win/Draw/Loss statistics (when filtering for a specific team)
  - Match fairness statistics based on goal differences:
    - Fair: 0-2 goal difference
    - Uneven: 3-5 goal difference
    - Devastating: 6+ goal difference

Example Output:
```
Year 2024:
- Total matches: 1039
- Grótta matches: 27

Grótta's matches by tournament:
Íslandsmót KSÍ - 5. flokkur karla A-lið:
  2024-05-12: Grótta vs Leiknir R. (8-1)
  2024-05-29: Grótta vs Álftanes (10-3)
  
  Results: W: 75% / D: 12% / L: 13%
  Fairness: 25% / 50% / 25% (Fair / Uneven / Devastating)
```

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 