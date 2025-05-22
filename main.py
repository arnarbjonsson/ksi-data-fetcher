# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from src.data.match_fetcher import MatchFetcher
from collections import defaultdict

def get_match_result(match, team_id):
    """Get if the team won, drew or lost the match"""
    if not match['is_played']:
        return None
        
    team_id = str(team_id)
    home_score = match['home_score']
    away_score = match['away_score']
    is_home = str(match['home_team_id']) == team_id
    
    if home_score == away_score:
        return 'draw'
    elif (is_home and home_score > away_score) or (not is_home and away_score > home_score):
        return 'win'
    else:
        return 'loss'

def calculate_tournament_stats(matches, team_id):
    """Calculate tournament statistics for a team"""
    stats = {'win': 0, 'draw': 0, 'loss': 0, 'not_played': 0}
    
    for match in matches:
        result = get_match_result(match, team_id)
        if result:
            stats[result] += 1
        else:
            stats['not_played'] += 1
    
    played_matches = len(matches) - stats['not_played']
    if played_matches > 0:
        win_pct = (stats['win'] / played_matches) * 100
        draw_pct = (stats['draw'] / played_matches) * 100
        loss_pct = (stats['loss'] / played_matches) * 100
        return f"(W: {win_pct:.1f}% / D: {draw_pct:.1f}% / L: {loss_pct:.1f}%)"
    else:
        return "No matches played yet"

def main(start_year=2024, end_year=2024):
    """
    Fetch and display match statistics for Grótta's youth team.
    
    Args:
        start_year (int): The year to start fetching matches from (inclusive)
        end_year (int): The year to end fetching matches at (inclusive)
    """
    # Initialize components
    soap_client = KSIClient()
    web_scraper = KSIWebScraper()
    match_fetcher = MatchFetcher(soap_client, web_scraper)
    
    # Example: Fetch matches for Grótta in 5. flokkur karla
    team_id = 170  # Grótta
    age_group_id = 420  # 5. flokkur karla
    
    result = match_fetcher.get_matches_for_years(
        age_group_id=age_group_id,
        start_year=start_year,
        end_year=end_year
    )
    
    print(f"\nTotal matches found: {result['total_matches']}")
    
    # Print matches by year
    for year, matches in result['matches_by_year'].items():
        print(f"\nYear {year}:")
        print(f"- Total matches: {len(matches)}")
        
        # Filter Grótta's matches
        grotta_matches = [
            match for match in matches
            if str(team_id) in [str(match['home_team_id']), str(match['away_team_id'])]
        ]
        
        print(f"- Grótta matches: {len(grotta_matches)}")
        
        if grotta_matches:
            # Group matches by tournament
            matches_by_tournament = defaultdict(list)
            for match in grotta_matches:
                matches_by_tournament[match['tournament_name']].append(match)
            
            print("\nGrótta's matches by tournament:")
            for tournament_name, tournament_matches in matches_by_tournament.items():
                print(f"\n{tournament_name}:")
                
                # Print matches sorted by date
                for match in sorted(tournament_matches, key=lambda x: x['date']):
                    home_team = match['home_team_name']
                    away_team = match['away_team_name']
                    score = f"{match['home_score']}-{match['away_score']}" if match['is_played'] else 'Not played'
                    date = match['date'].split('T')[0]  # Just show the date part
                    print(f"  {date}: {home_team} vs {away_team} ({score})")
                
                # Print tournament statistics
                stats = calculate_tournament_stats(tournament_matches, team_id)
                print(f"  Statistics: {stats}")

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments if provided, otherwise use defaults
    try:
        if len(sys.argv) > 2:
            start_year = int(sys.argv[1])
            end_year = int(sys.argv[2])
            main(start_year, end_year)
        else:
            main()  # Use default values
    except ValueError:
        print("Error: Years must be valid integers")
        print("Usage: python main.py [start_year] [end_year]")
        sys.exit(1)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
