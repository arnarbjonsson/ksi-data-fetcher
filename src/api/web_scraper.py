import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
from datetime import datetime

from src.const import TournamentType


class KSIWebScraper:
    """Scraper for fetching tournament data from the KSÍ website."""
    
    def __init__(self):
        self.base_url = "https://www.ksi.is/mot/leikir-og-mot/oll-mot/"
        self.matches_base_url = "https://www.ksi.is/mot/leikir-og-mot/leiksedill/"
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string from KSÍ format to ISO format."""
        try:
            # Example: "15.3.2024 17:00"
            date = datetime.strptime(date_str.strip(), "%d.%m.%Y %H:%M")
            return date.isoformat()
        except ValueError:
            try:
                # Try without time
                date = datetime.strptime(date_str.strip(), "%d.%m.%Y")
                return date.isoformat()
            except ValueError:
                return None
    
    def _extract_team_id(self, team_link: Optional[Any]) -> Optional[str]:
        """Extract team ID from team link."""
        if not team_link:
            return None
        href = team_link.get('href', '')
        if 'felag=' in href:
            return href.split('felag=')[1].split('&')[0]
        return None
    
    def _parse_score(self, score_text: str) -> tuple[Optional[int], Optional[int]]:
        """Parse score text into home and away goals."""
        try:
            if not score_text or '-' not in score_text:
                return None, None
            home_score, away_score = score_text.split('-')
            return int(home_score.strip()), int(away_score.strip())
        except (ValueError, AttributeError):
            return None, None
    
    def get_tournament_matches(self, tournament_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all matches for a specific tournament.
        
        Args:
            tournament_id: The ID of the tournament
            
        Returns:
            List of matches with their details including:
            - match_id: Unique identifier for the match
            - date: Match date and time in ISO format
            - home_team_id: ID of the home team
            - away_team_id: ID of the away team
            - home_team_name: Name of the home team
            - away_team_name: Name of the away team
            - home_score: Goals scored by home team (if played)
            - away_score: Goals scored by away team (if played)
            - venue: Name of the venue
            - is_played: Whether the match has been played
        """
        params = {
            'motnumer': tournament_id
        }
        
        url = f"{self.matches_base_url}?{urlencode(params)}"
        print(f"Fetching matches from: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = []
            
            # Find the matches table
            matches_table = None
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables on the page")
            
            for table in tables:
                headers = table.find_all('th')
                if headers:
                    header_texts = [h.text.strip() for h in headers]
                    print(f"Found table with headers: {header_texts}")
                    if any('leikur' in h.text.strip().lower() for h in headers):
                        matches_table = table
                        break
            
            if not matches_table:
                print("Could not find matches table")
                # Save the HTML for debugging
                debug_file = f'debug_matches_{tournament_id}.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print(f"Saved HTML to {debug_file} for inspection")
                return matches
            
            print("Found matches table, processing rows...")
            
            # Process each match row
            for row in matches_table.find_all('tr')[1:]:  # Skip header row
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 5:  # Basic validation
                        print(f"Skipping row with insufficient cells: {len(cells)}")
                        continue
                    
                    # Extract match ID from the first cell's link
                    match_link = cells[0].find('a')
                    match_id = None
                    if match_link and 'leikur=' in match_link.get('href', ''):
                        match_id = match_link.get('href', '').split('leikur=')[1].split('&')[0]
                    
                    # Get team links
                    home_team_link = cells[2].find('a')
                    away_team_link = cells[4].find('a')
                    
                    # Get team IDs
                    home_team_id = self._extract_team_id(home_team_link)
                    away_team_id = self._extract_team_id(away_team_link)
                    
                    # Get team names
                    home_team_name = home_team_link.text.strip() if home_team_link else cells[2].text.strip()
                    away_team_name = away_team_link.text.strip() if away_team_link else cells[4].text.strip()
                    
                    # Parse score
                    score_cell = cells[3].text.strip()
                    home_score, away_score = self._parse_score(score_cell)
                    is_played = home_score is not None and away_score is not None
                    
                    # Parse date and venue
                    date_str = cells[1].text.strip() if len(cells) > 1 else None
                    venue = cells[5].text.strip() if len(cells) > 5 else None
                    
                    match = {
                        'match_id': match_id,
                        'date': self._parse_date(date_str) if date_str else None,
                        'home_team_id': home_team_id,
                        'away_team_id': away_team_id,
                        'home_team_name': home_team_name,
                        'away_team_name': away_team_name,
                        'home_score': home_score,
                        'away_score': away_score,
                        'venue': venue,
                        'is_played': is_played,
                        'tournament_id': str(tournament_id)
                    }
                    
                    matches.append(match)
                    print(f"Processed match: {home_team_name} vs {away_team_name}")
                    
                except Exception as e:
                    print(f"Error processing match row: {str(e)}")
                    continue
            
            print(f"Found {len(matches)} matches in tournament {tournament_id}")
            return matches
            
        except requests.RequestException as e:
            print(f"Error fetching matches for tournament {tournament_id}: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error processing tournament {tournament_id}: {str(e)}")
            return []
        
    def get_tournaments_in_age_group(self, age_group_id: int, year: int = 2025, gender: int = 1, tournament_type: int=TournamentType.ISLANDSMOT.value) -> List[Dict[str, Any]]:
        """
        Fetch tournaments for a specific age group from the KSÍ website.
        
        Args:
            age_group_id: The ID of the age group (flokkur)
            year: The year to fetch tournaments for (default: 2025)
            gender: 1 for men's tournaments, 2 for women's tournaments (default: 1)
            
        Returns:
            List of tournaments with their details
        """
        params = {
            'filter': '',
            'flokkur': age_group_id,
            'tegund': tournament_type,
            'ar': year,
            'kyn': gender
        }
        
        url = f"{self.base_url}?{urlencode(params)}"
        print(f"Fetching tournaments from: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tournaments = []
        
        # Debug: Print all tables found
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page")
        
        # Try to find the tournament table
        tournament_table = None
        for table in tables:
            # Look for table headers that might indicate this is the tournament table
            headers = table.find_all('th')
            if headers:
                header_texts = [h.text.strip() for h in headers]
                print(f"Found table with headers: {header_texts}")
                if any('mót' in h.lower() for h in header_texts):
                    tournament_table = table
                    break
        
        if tournament_table:
            print("Found tournament table, processing rows...")
            # Process each row (skipping header row)
            for row in tournament_table.find_all('tr')[1:]:
                cells = row.find_all(['td', 'th'])  # Look for both td and th cells
                if cells:
                    # Find the tournament link and extract the ID
                    link = cells[0].find('a')
                    if link:
                        tournament_url = link.get('href', '')
                        tournament_id = None
                        if 'motnumer=' in tournament_url:
                            tournament_id = tournament_url.split('motnumer=')[1]
                        
                        tournament = {
                            'name': link.text.strip(),
                            'tournament_id': tournament_id,
                            'url': tournament_url,
                            'year': cells[1].text.strip() if len(cells) > 1 else None,
                            'status': cells[2].text.strip() if len(cells) > 2 else None,
                            'category': cells[3].text.strip() if len(cells) > 3 else None,
                            'age_group': cells[4].text.strip() if len(cells) > 4 else None,
                            'gender': cells[5].text.strip() if len(cells) > 5 else None
                        }
                        tournaments.append(tournament)
                        print(f"Found tournament: {tournament['name']}")
        else:
            print("Could not find tournament table in the page")
            # Debug: Save the HTML for inspection
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("Saved HTML to debug_page.html for inspection")
        
        return tournaments 