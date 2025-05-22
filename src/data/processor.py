import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class DataProcessor:
    """Process and clean data from the KSÍ API."""
    
    @staticmethod
    def process_tournaments(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert tournaments data to a DataFrame and clean it."""
        df = pd.DataFrame(data)
        return df
    
    @staticmethod
    def process_standings(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert standings data to a DataFrame and clean it."""
        df = pd.DataFrame(data)
        # Rename columns to more readable format if needed
        column_mapping = {
            'FELAG': 'team',
            'LEIKIR': 'matches_played',
            'STIG': 'points',
            'MORK': 'goals',
            'MORKAMUNUR': 'goal_difference'
        }
        df = df.rename(columns=column_mapping)
        return df
    
    @staticmethod
    def process_matches(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert matches data to a DataFrame and clean it."""
        df = pd.DataFrame(data)
        # Convert date strings to datetime objects if needed
        if 'DAGS' in df.columns:
            df['DAGS'] = pd.to_datetime(df['DAGS'])
        return df
    
    @staticmethod
    def calculate_team_stats(matches_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional team statistics from matches data."""
        # Add implementation for calculating win rates, scoring trends, etc.
        pass 