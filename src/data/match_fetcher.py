from typing import List, Dict, Any
from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from src.data.cache_manager import CacheManager
from time import sleep
from datetime import datetime

class MatchFetcher:
    """Class for fetching and processing football matches."""
    
    def __init__(self, soap_client: KSIClient, web_scraper: KSIWebScraper, cache_ttl_days: int = 1):
        self.soap_client = soap_client
        self.web_scraper = web_scraper
        self.cache = CacheManager(ttl_days=cache_ttl_days)

    def _convert_match_data(self, raw_match: Dict[str, Any], tournament) -> Dict[str, Any]:
        """Convert raw match data from SOAP API to standardized format."""
        return {
            'match_id': raw_match.get('LeikurNumer', None),
            'date': raw_match.get('LeikDagur', None),
            'home_team_id': raw_match.get('FelagHeimaNumer', None),
            'away_team_id': raw_match.get('FelagUtiNumer', None),
            'home_team_name': raw_match.get('FelagHeimaNafn', None),
            'away_team_name': raw_match.get('FelagUtiNafn', None),
            'home_score': int(raw_match.get('UrslitHeima', 0)) if raw_match.get('UrslitHeima') else None,
            'away_score': int(raw_match.get('UrslitUti', 0)) if raw_match.get('UrslitUti') else None,
            'venue': raw_match.get('VollurNafn', None),
            'is_played': bool(raw_match.get('UrslitHeima') and raw_match.get('UrslitUti')),
            'tournament_id': int(tournament['tournament_id']),
            'tournament_name': tournament['name'],
        }
    
    def get_matches_for_years(self, age_group_id: int, start_year: int, end_year: int, tournament_type: int = None) -> Dict[str, Any]:
        """
        Fetch all matches for a given age group between specified years.
        
        Args:
            age_group_id: The ID of the age group to fetch matches for
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            tournament_type: Optional tournament type ID to filter by
            
        Returns:
            Dictionary containing:
            - total_matches: Total number of matches found
            - matches_by_year: Dictionary of matches grouped by year
            - tournaments_by_year: Dictionary of tournaments grouped by year
        """
        total_matches = 0
        matches_by_year = {}
        tournaments_by_year = {}
        all_matches = []
        
        # Process each year in the range
        for year in range(end_year, start_year - 1, -1):
            print(f"\nProcessing {year} tournaments...")
            
            # Try to get tournaments from cache
            cache_key = self.cache.build_key("tournaments", age_group=age_group_id, year=year, tournament_type=tournament_type)
            tournaments = self.cache.get(cache_key)
            
            if tournaments is None:
                # Not in cache, fetch from API
                tournaments = self.web_scraper.get_tournaments_in_age_group(age_group_id, year=year, tournament_type=tournament_type)
                if tournaments:
                    # Store in cache
                    self.cache.set(cache_key, tournaments)
            
            if tournaments:
                print(f"Found {len(tournaments)} tournaments in {year}")
                tournaments_by_year[year] = tournaments
                
                # All tournaments are already filtered by type in the web scraper
                regular_tournaments = tournaments
                
                print(f"Processing {len(regular_tournaments)} tournaments...")
                year_matches = []
                
                # Check each tournament for matches
                for i, tournament in enumerate(regular_tournaments, 1):
                    tournament_id = int(tournament['tournament_id'])
                    print(f"\rChecking tournament {i}/{len(regular_tournaments)}: {tournament['name']}", end='')
                    
                    # Try to get matches from cache
                    cache_key = self.cache.build_key("matches", tournament_id=tournament_id)
                    matches = self.cache.get(cache_key)
                    
                    if matches is None:
                        # Not in cache, fetch from API
                        raw_matches = self.soap_client.get_tournament_matches(tournament_id)
                        if raw_matches:
                            matches = [self._convert_match_data(raw_match, tournament) for raw_match in raw_matches]
                            self.cache.set(cache_key, matches)
                            
                            # Add a small delay between API calls
                            sleep(0.5)
                    
                    if matches:
                        year_matches.extend(matches)
                        total_matches += len(matches)
                
                matches_by_year[year] = year_matches
                all_matches += year_matches

                print(f"\nFound {len(year_matches)} matches in {year}")
            else:
                print(f"No tournaments found for {year}")
                matches_by_year[year] = []
        
        return {
            'total_matches': total_matches,
            'matches_by_year': matches_by_year,
            'tournaments_by_year': tournaments_by_year,
            'all_matches': all_matches,
        }
    
    def filter_team_matches(self, matches: List[Dict[str, Any]], team_id: str) -> List[Dict[str, Any]]:
        """
        Filter matches to only include those involving a specific team.
        
        Args:
            matches: List of matches to filter
            team_id: ID of the team to filter for
            
        Returns:
            List of matches involving the specified team
        """
        return [
            match for match in matches
            if team_id in [str(match.get('home_team_id')), str(match.get('away_team_id'))]
        ] 