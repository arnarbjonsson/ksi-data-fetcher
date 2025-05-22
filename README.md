# KSÍ Data Fetcher

A Python project for fetching, processing, and visualizing data from the Icelandic Football Association (KSÍ) API.

## Requirements
- Python 3.9 or newer

## Features
- Fetches data from KSÍ's SOAP API (https://www2.ksi.is/vefthjonustur/mot.asmx)
- Processes and cleans the data for analysis
- Creates interactive visualizations using Plotly

## Setup
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the main script:
```bash
python main.py
```

## Project Structure
- `src/`
  - `api/` - API interaction code
  - `data/` - Data processing modules
  - `visualization/` - Visualization functions
- `main.py` - Main entry point
- `requirements.txt` - Project dependencies 