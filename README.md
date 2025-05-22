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

The script can be run in two ways:

1. Default mode (fetches data for current year):
```bash
pipenv run python main.py
```

2. Specify a year range:
```bash
pipenv run python main.py [start_year] [end_year]
```

Example:
```bash
# Fetch data for 2023-2024
pipenv run python main.py 2023 2024
```

## Output Format

The script outputs:
- Total matches found
- Matches grouped by tournament
- For each tournament:
  - Match details (date, teams, scores)
  - Statistics showing win/draw/loss percentages

## Example Output

```
Year 2024:
- Total matches: 1039
- Grótta matches: 27

Grótta's matches by tournament:
Íslandsmót KSÍ - 5. flokkur karla A-lið:
  2024-05-12: Grótta vs Leiknir R. (8-1)
  2024-05-29: Grótta vs Álftanes (10-3)
  Statistics: (W: 75.0% / D: 12.5% / L: 12.5%)
```

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 