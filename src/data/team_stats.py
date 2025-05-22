from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TeamSeasonStats:
    """Statistics for a team in a single season."""
    year: int
    matches_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    
    @property
    def win_ratio(self) -> float:
        """Calculate win ratio."""
        return self.wins / self.matches_played if self.matches_played > 0 else 0.0
    
    @property
    def draw_ratio(self) -> float:
        """Calculate draw ratio."""
        return self.draws / self.matches_played if self.matches_played > 0 else 0.0
    
    @property
    def loss_ratio(self) -> float:
        """Calculate loss ratio."""
        return self.losses / self.matches_played if self.matches_played > 0 else 0.0

class TeamStatsAnalyzer:
    """Analyzes team statistics across seasons."""
    
    def __init__(self, team_id: str, team_name: str):
        self.team_id = team_id
        self.team_name = team_name
        self.season_stats: Dict[int, TeamSeasonStats] = {}
    
    def add_tournament_stats(self, year: int, stats: Dict[str, str]) -> None:
        """
        Add tournament statistics for a team.
        
        Args:
            year: The year of the tournament
            stats: Dictionary containing the team's stats from the tournament
        """
        if year not in self.season_stats:
            self.season_stats[year] = TeamSeasonStats(year=year)
        
        season = self.season_stats[year]
        
        # Update season totals
        season.matches_played += int(stats.get('LeikirAlls', 0))
        season.wins += int(stats.get('LeikirUnnir', 0))
        season.draws += int(stats.get('LeikirJafnt', 0))
        season.losses += int(stats.get('LeikirTap', 0))
        season.goals_for += int(stats.get('MorkSkorud', 0))
        season.goals_against += int(stats.get('MorkFenginASig', 0))
    
    def get_summary(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """
        Get a summary of the team's performance over a range of years.
        
        Args:
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            
        Returns:
            Dictionary containing summary statistics
        """
        total_matches = 0
        total_wins = 0
        total_draws = 0
        total_losses = 0
        total_goals_for = 0
        total_goals_against = 0
        
        yearly_stats = []
        
        for year in range(start_year, end_year + 1):
            if year in self.season_stats:
                stats = self.season_stats[year]
                total_matches += stats.matches_played
                total_wins += stats.wins
                total_draws += stats.draws
                total_losses += stats.losses
                total_goals_for += stats.goals_for
                total_goals_against += stats.goals_against
                
                yearly_stats.append({
                    'year': year,
                    'matches': stats.matches_played,
                    'wins': stats.wins,
                    'draws': stats.draws,
                    'losses': stats.losses,
                    'win_ratio': stats.win_ratio,
                    'draw_ratio': stats.draw_ratio,
                    'loss_ratio': stats.loss_ratio,
                    'goals_for': stats.goals_for,
                    'goals_against': stats.goals_against
                })
        
        return {
            'team_id': self.team_id,
            'team_name': self.team_name,
            'total_matches': total_matches,
            'total_wins': total_wins,
            'total_draws': total_draws,
            'total_losses': total_losses,
            'total_goals_for': total_goals_for,
            'total_goals_against': total_goals_against,
            'overall_win_ratio': total_wins / total_matches if total_matches > 0 else 0.0,
            'overall_draw_ratio': total_draws / total_matches if total_matches > 0 else 0.0,
            'overall_loss_ratio': total_losses / total_matches if total_matches > 0 else 0.0,
            'yearly_stats': yearly_stats
        } 