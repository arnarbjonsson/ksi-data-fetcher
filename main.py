# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from src.data.match_fetcher import MatchFetcher
from src.const import AgeGroup, Team, TournamentType
from collections import defaultdict
from datetime import datetime

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

def calculate_result_stats(matches, team_id):
    """Calculate win/draw/loss statistics for a team's matches"""
    # Win/Draw/Loss stats
    result_stats = {'win': 0, 'draw': 0, 'loss': 0, 'not_played': 0}
    
    for match in matches:
        # Calculate result stats
        result = get_match_result(match, team_id)
        if result:
            result_stats[result] += 1
        else:
            result_stats['not_played'] += 1
    
    played_matches = len(matches) - result_stats['not_played']
    if played_matches > 0:
        # Calculate result percentages
        win_pct = (result_stats['win'] / played_matches) * 100
        draw_pct = (result_stats['draw'] / played_matches) * 100
        loss_pct = (result_stats['loss'] / played_matches) * 100
        
        return f"Results: W: {win_pct:.0f}% / D: {draw_pct:.0f}% / L: {loss_pct:.0f}%"
    else:
        return "No matches played yet"


def calculate_fairness_stats(matches):
    """Calculate fairness statistics based on goal differences"""
    # Fairness stats
    fairness_stats = {'fair': 0, 'uneven': 0, 'devastating': 0, 'not_played': 0}

    for match in matches:
        # Calculate fairness stats
        fairness = get_match_fairness(match)
        if fairness:
            fairness_stats[fairness] += 1
        else:
            fairness_stats['not_played'] += 1

    played_matches = len(matches) - fairness_stats['not_played']
    if played_matches > 0:
        # Calculate fairness percentages
        fair_pct = (fairness_stats['fair'] / played_matches) * 100
        uneven_pct = (fairness_stats['uneven'] / played_matches) * 100
        devastating_pct = (fairness_stats['devastating'] / played_matches) * 100

        return f"Fairness: {fair_pct:.0f}% / {uneven_pct:.0f}% / {devastating_pct:.0f}% (Fair / Uneven / Devastating)"
    else:
        return "No matches played yet"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch and analyze football match data from KSÍ.')
    parser.add_argument('--start-year', type=int, default=2024,
                      help='The year to start fetching matches from (inclusive)')
    parser.add_argument('--end-year', type=int, default=2024,
                      help='The year to end fetching matches at (inclusive)')
    parser.add_argument('--team', type=int, default=None,
                      help='The ID of the team to analyze')
    parser.add_argument('--age-group', type=int, default=AgeGroup.FIFTH_FLOKKUR.value,
                      help='The age group ID to fetch matches for')
    parser.add_argument('--tournament-type', type=int, default=TournamentType.ISLANDSMOT.value,
                      help='The tournament type ID to filter by')
    
    return parser.parse_args()

def format_date(date_str):
    """Format ISO date string for display."""
    if not date_str:
        return 'No date'
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return date_str

def main(start_year=2024, end_year=2024, team_id=None, age_group_id=AgeGroup.FIFTH_FLOKKUR.value, tournament_type=TournamentType.ISLANDSMOT.value):
    """
    Fetch and display match statistics for a youth team.
    
    Args:
        start_year (int): The year to start fetching matches from (inclusive)
        end_year (int): The year to end fetching matches at (inclusive)
        team_id (int): The ID of the team to analyze
        age_group_id (int): The age group ID to fetch matches for
        tournament_type (int): The tournament type ID to filter by
    """
    # Initialize components
    soap_client = KSIClient()
    web_scraper = KSIWebScraper()
    match_fetcher = MatchFetcher(soap_client, web_scraper)
    
    # Get team name for display
    team_name = Team.get_name(team_id) if team_id else "Unknown Team"
    age_group_name = AgeGroup.get_name(age_group_id)
    
    print(f"\nFetching matches for {team_name} in {age_group_name}")
    
    result = match_fetcher.get_matches_for_years(
        age_group_id=age_group_id,
        start_year=start_year,
        end_year=end_year,
        tournament_type=tournament_type,
    )
    
    print(f"\nTotal matches found: {result['total_matches']}")
    
    # Print matches by year
    for year, matches in result['matches_by_year'].items():
        print(f"\nYear {year}:")
        print(f"- Total matches: {len(matches)}")

        if not matches:
            continue

        if team_id:
            matches = [
                match for match in matches
                if str(team_id) in [str(match['home_team_id']), str(match['away_team_id'])]
            ]

        # Group matches by tournament
        matches_by_tournament = defaultdict(list)
        for match in matches:
            matches_by_tournament[match['tournament_name']].append(match)

        print(f"\n{team_name}'s matches by tournament:")
        for tournament_name, tournament_matches in matches_by_tournament.items():
            print(f"\n{tournament_name}:")

            # Print matches sorted by date
            for match in sorted(tournament_matches, key=lambda x: x['date'] or '9999-12-31'):
                home_team = match['home_team_name']
                away_team = match['away_team_name']
                score = f"{match['home_score']}-{match['away_score']}" if match['is_played'] else 'Not played'
                if team_id:
                    date = format_date(match['date'])
                    print(f"  {date}: {home_team} {score} {away_team}")

            # Print tournament statistics
            if team_id:
                result_stats = calculate_result_stats(tournament_matches, team_id)
                print(f"\n  {result_stats}")

            fairness_stats = calculate_fairness_stats(tournament_matches)
            print(f"  {fairness_stats}")

    all_matches = result['all_matches']
    if team_id:
        print(f"\nOverall Results:")
        result_stats = calculate_result_stats(all_matches, team_id)
        print(f"  {result_stats}")

    print(f"\nOverall Fairness:")
    fairness_stats = calculate_fairness_stats(all_matches)
    print(f"  {fairness_stats}")

if __name__ == '__main__':
    args = parse_args()
    main(
        start_year=args.start_year,
        end_year=args.end_year,
        team_id=args.team,
        age_group_id=args.age_group,
        tournament_type=args.tournament_type
    )

# pipenv run python main.py --start-year 2020 --end-year 2025 --team 170