# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from src.data.match_fetcher import MatchFetcher
from src.const import AgeGroup, Team
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

def get_match_fairness(match):
    """
    Calculate match fairness based on goal difference.
    Returns: 'fair' (0-2), 'uneven' (3-5), or 'devastating' (6+)
    """
    if not match['is_played']:
        return None
        
    goal_diff = abs(match['home_score'] - match['away_score'])
    
    if goal_diff <= 2:
        return 'fair'
    elif goal_diff <= 5:
        return 'uneven'
    else:
        return 'devastating'

def calculate_tournament_stats(matches, team_id):
    """Calculate tournament statistics for a team"""
    # Win/Draw/Loss stats
    result_stats = {'win': 0, 'draw': 0, 'loss': 0, 'not_played': 0}
    # Fairness stats
    fairness_stats = {'fair': 0, 'uneven': 0, 'devastating': 0, 'not_played': 0}
    
    for match in matches:
        # Calculate result stats
        result = get_match_result(match, team_id)
        if result:
            result_stats[result] += 1
        else:
            result_stats['not_played'] += 1
            
        # Calculate fairness stats
        fairness = get_match_fairness(match)
        if fairness:
            fairness_stats[fairness] += 1
        else:
            fairness_stats['not_played'] += 1
    
    played_matches = len(matches) - result_stats['not_played']
    if played_matches > 0:
        # Calculate result percentages
        win_pct = (result_stats['win'] / played_matches) * 100
        draw_pct = (result_stats['draw'] / played_matches) * 100
        loss_pct = (result_stats['loss'] / played_matches) * 100
        
        # Calculate fairness percentages
        fair_pct = (fairness_stats['fair'] / played_matches) * 100
        uneven_pct = (fairness_stats['uneven'] / played_matches) * 100
        devastating_pct = (fairness_stats['devastating'] / played_matches) * 100
        
        return (
            f"Results: (W: {win_pct:.1f}% / D: {draw_pct:.1f}% / L: {loss_pct:.1f}%)\n"
            f"  Fairness: (Fair: {fair_pct:.1f}% / Uneven: {uneven_pct:.1f}% / Devastating: {devastating_pct:.1f}%)"
        )
    else:
        return "No matches played yet"

def main(start_year=2024, end_year=2024, team_id=Team.GROTTA.value):
    """
    Fetch and display match statistics for a youth team.
    
    Args:
        start_year (int): The year to start fetching matches from (inclusive)
        end_year (int): The year to end fetching matches at (inclusive)
        team_id (int): The ID of the team to analyze (defaults to Grótta)
    """
    # Initialize components
    soap_client = KSIClient()
    web_scraper = KSIWebScraper()
    match_fetcher = MatchFetcher(soap_client, web_scraper)
    
    # Get team name for display
    team_name = Team.get_name(team_id)
    age_group = AgeGroup.FIFTH_FLOKKUR
    age_group_name = AgeGroup.get_name(age_group.value)
    
    print(f"\nFetching matches for {team_name} in {age_group_name}")
    
    result = match_fetcher.get_matches_for_years(
        age_group_id=age_group.value,
        start_year=start_year,
        end_year=end_year
    )
    
    print(f"\nTotal matches found: {result['total_matches']}")
    
    # Print matches by year
    for year, matches in result['matches_by_year'].items():
        print(f"\nYear {year}:")
        print(f"- Total matches: {len(matches)}")
        
        # Filter team's matches
        team_matches = [
            match for match in matches
            if str(team_id) in [str(match['home_team_id']), str(match['away_team_id'])]
        ]
        
        print(f"- {team_name} matches: {len(team_matches)}")
        
        if team_matches:
            # Group matches by tournament
            matches_by_tournament = defaultdict(list)
            for match in team_matches:
                matches_by_tournament[match['tournament_name']].append(match)
            
            print(f"\n{team_name}'s matches by tournament:")
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
                print(f"\n  {stats}")

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
