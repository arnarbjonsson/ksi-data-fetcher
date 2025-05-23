from typing import List, Dict, Any
from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from time import sleep

class MatchFetcher:
    """Class for fetching and processing football matches."""
    
    def __init__(self, soap_client: KSIClient, web_scraper: KSIWebScraper):
        self.soap_client = soap_client
        self.web_scraper = web_scraper
    
    def get_matches_for_years(self, age_group_id: int, start_year: int, end_year: int, tournament_type: int) -> Dict[str, Any]:
        """
        Fetch all matches for a given age group between specified years.
        
        Args:
            age_group_id: The ID of the age group to fetch matches for
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            
        Returns:
            Dictionary containing:
            - total_matches: Total number of matches found
            - matches_by_year: Dictionary of matches grouped by year
            - tournaments_by_year: Dictionary of tournaments grouped by year
        """
        total_matches = 0
        matches_by_year = {}
        tournaments_by_year = {}
        
        # Process each year in the range
        for year in range(end_year, start_year - 1, -1):
            print(f"\nProcessing {year} tournaments...")
            
            # Get tournaments for this year
            tournaments = self.web_scraper.get_tournaments_in_age_group(age_group_id, year=year, tournament_type=tournament_type)
            
            if tournaments:
                print(f"Found {len(tournaments)} tournaments in {year}")
                tournaments_by_year[year] = tournaments
                
                # Filter tournaments that are likely to have standings
                regular_tournaments = [t for t in tournaments 
                                    if not any(x in t['name'].lower() for x in ['úrslit', 'umspil'])]
                
                print(f"Processing {len(regular_tournaments)} regular season tournaments...")
                year_matches = []
                
                # Check each tournament for matches
                for i, tournament in enumerate(regular_tournaments, 1):
                    tournament_id = int(tournament['tournament_id'])
                    print(f"\rChecking tournament {i}/{len(regular_tournaments)}: {tournament['name']}", end='')
                    
                    # Get matches from SOAP API
                    raw_matches = self.soap_client.get_tournament_matches(tournament_id)
                    if raw_matches:
                        # Convert SOAP API response format to our standard format
                        matches = [{
                            'match_id': match.get('LeikurNumer', None),
                            'date': match.get('LeikDagur', None),
                            'home_team_id': match.get('FelagHeimaNumer', None),
                            'away_team_id': match.get('FelagUtiNumer', None),
                            'home_team_name': match.get('FelagHeimaNafn', None),
                            'away_team_name': match.get('FelagUtiNafn', None),
                            'home_score': int(match.get('UrslitHeima', 0)) if match.get('UrslitHeima') else None,
                            'away_score': int(match.get('UrslitUti', 0)) if match.get('UrslitUti') else None,
                            'venue': match.get('VollurNafn', None),
                            'is_played': bool(match.get('UrslitHeima') and match.get('UrslitUti')),
                            'tournament_id': str(tournament_id),
                            'tournament_name': tournament['name']
                        } for match in raw_matches]
                        
                        year_matches.extend(matches)
                        total_matches += len(matches)
                    
                    # Add a small delay between API calls
                    sleep(0.5)
                
                matches_by_year[year] = year_matches
                print(f"\nFound {len(year_matches)} matches in {year}")
            else:
                print(f"No tournaments found for {year}")
                matches_by_year[year] = []
        
        return {
            'total_matches': total_matches,
            'matches_by_year': matches_by_year,
            'tournaments_by_year': tournaments_by_year
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