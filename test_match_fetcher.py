from src.api.ksi_client import KSIClient
from src.api.web_scraper import KSIWebScraper
from src.data.match_fetcher import MatchFetcher

def main():
    # Initialize components
    soap_client = KSIClient()
    web_scraper = KSIWebScraper()
    match_fetcher = MatchFetcher(soap_client, web_scraper)
    
    # Test direct SOAP call first
    print("\nTesting direct SOAP call for matches...")
    tournament_id = 47844  # ID from previous test
    matches = soap_client.get_tournament_matches(tournament_id)
    
    if matches:
        print(f"\nDirect SOAP call found {len(matches)} matches")
        print("\nFirst match data:")
        for key, value in matches[0].items():
            print(f"  {key}: {value}")
    else:
        print("No matches found from direct SOAP call")
    
    # Now test through MatchFetcher
    print("\nTesting through MatchFetcher...")
    
    # Test with a single year
    age_group_id = 420  # 5. flokkur
    result = match_fetcher.get_matches_for_years(
        age_group_id=age_group_id,
        start_year=2024,
        end_year=2024
    )
    
    # Print detailed results
    print("\nMatchFetcher Results Summary:")
    print(f"Total matches found: {result['total_matches']}")
    
    for year, matches in result['matches_by_year'].items():
        print(f"\nYear {year}:")
        print(f"- Total matches: {len(matches)}")
        if matches:
            print("\nFirst match data:")
            for key, value in matches[0].items():
                print(f"  {key}: {value}")

if __name__ == '__main__':
    main() 