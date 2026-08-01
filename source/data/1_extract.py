from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import time
from nba_api.stats.static import players
import re

salary_url = 'https://www.spotrac.com'
stats_url = 'https://www.basketball-reference.com'
headshot_url = 'https://cdn.nba.com/headshots/nba/latest/1040x760'
logos_url = 'https://www.nba.com/teams'
file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/raw'
salary_headers = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/137.0.0.0 Safari/537.36'
    )
}
stats_headers = {'User-Agent': 'Mozilla/5.0'}
stats_table_id_mapping = {
    'per_game': 'per_game_stats',
    'advanced': 'advanced',
    'per_poss': 'per_poss'
}

def salary_scrape(leagues, seasons, salary_type):
    """Scrape Spotrac for salary data."""
    
    for league in leagues:
        for season in seasons:
            print(f'Scraping {league} salaries for the {season} season..')

            url = f'{salary_url}/{league}/rankings/player/_/year/{season}/sort/{salary_type}'

            page = requests.get(url, headers=salary_headers)
            soup = BeautifulSoup(page.text, 'html.parser')

            # Find row data
            rows = soup.select('li.list-group-item')

            data = []

            for row in rows:
                try:
                    # Rank
                    rank = row.select_one('div.fw-bold').text.strip()

                    # Player name
                    player = row.select_one('a.link').text.strip()

                    # Team + position
                    meta = row.select_one('small')
                    meta_text = meta.text.strip() if meta else ''

                    if ',' in meta_text:
                        team, position = [x.strip() for x in meta_text.split(',', 1)]
                    else:
                        team, position = meta_text, None

                    # Salary
                    salary = row.select('span.medium')[-1].text.strip()

                    data.append({
                        'league': league,
                        'season': season,
                        'rank': rank,
                        'player': player,
                        'team': team,
                        'position': position,
                        'salary': salary
                    })

                except Exception as e:
                    continue
            
            # Create DataFrame
            salary_df = pd.DataFrame(data)

            # Save csv
            if salary_type == 'cap_total_league_pct':
                salary_df.to_csv(file_path + f'/{league}/{league}_{season}_cap_percentages.csv')
            else:
                salary_df.to_csv(file_path + f'/{league}/{league}_{season}_salaries.csv')

            print(f'Saved to {league}_{season}_salaries.csv')

            time.sleep(random.uniform(4, 7))

        print(f'Finished extracting {league} salaries.')



def stats_scrape(seasons, stat_type, playoffs=False):
    """Scrape Basketball Reference for player stats."""

    for season in seasons:
        season_type = 'playoff' if playoffs else 'regular season'

        print(f'Scraping {season} {season_type} {stat_type} stats..')

        if playoffs:
            url = f'{stats_url}/playoffs/NBA_{season}_{stat_type}.html'
        else:
            url = f'{stats_url}/leagues/NBA_{season}_{stat_type}.html'

        page = requests.get(url, headers=stats_headers)
        page.encoding = 'utf-8'

        print(page.status_code)

        soup = BeautifulSoup(page.text, 'html.parser')

        # Find stats table

        if playoffs:
            mapping = {
                'per_game': 'per_game_stats',
                'advanced': 'advanced_stats',
                'per_poss': 'per_poss_stats'
            }
            table_id = mapping[stat_type]
            table = soup.find('table', id=table_id)
        else:
            table_id = stats_table_id_mapping[stat_type]
            table = soup.find('table', id=table_id)

        if table is None:
            print(f'Could not find {stat_type} stats table for {season} season')
            time.sleep(random.uniform(4, 7))
            continue
        
        # Extract column headers
        header_row = table.find('thead').find('tr').find_all('th')
        columns = [column['aria-label'] for column in header_row]

        # Extract rows
        rows = []

        body_rows = table.find('tbody').find_all('tr')

        for row in body_rows:

            player_data = row.find_all(['th','td'])

            row_values = [player.get_text(strip=True) for player in player_data]
            
            rows.append(row_values)
        
        # Create DataFrame
        season_df = pd.DataFrame(rows, columns=columns)

        # Save csv
        file_prefix = 'playoffs' if playoffs else 'regular'
        
        season_df.to_csv(f'{file_path}/nba_stats/{stat_type}/{file_prefix}_{season}_{stat_type}_stats.csv')

        print(f'Saved {season} {season_type} {stat_type} stats')

        time.sleep(random.uniform(4, 7))


def get_headshot(player):
    """Use NBA-API to obtain player headshots"""

    player_list = players.find_players_by_full_name(str(player))

    if not player_list:
        return None
    
    # Get player id
    player_id = player_list[0]['id']

    # Create image url
    image_url = f'{headshot_url}/{player_id}.png'

    return image_url


def headshot_map():
    """Map headshots to players"""

    df = pd.read_csv(file_path + f'/nba_stats/per_game/2026_season_per_game_stats.csv')

    players = df['Player']

    headshot_map = {}

    # Map headshots to players
    for player in players:
        headshot_map[player] = get_headshot(player)

    # Add player headshots to df
    df['Images'] = df['Player'].map(headshot_map)

    # Save to csv
    df.to_csv(file_path + f'/nba_stats/player_images.csv')


def get_logos():
    """Scrape NBA.com for team logos."""

    url = logos_url

    page = requests.get(url, headers=stats_headers)
    page.encoding = 'utf-8'

    soup = BeautifulSoup(page.text, 'html.parser')

    # Find images table
    images = soup.find_all("img")

    teams_logos = []

    # Get team name and logos for each team
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt")

        if src and "cdn.nba.com/logos/nba" in src:

            team_name = alt.replace(" Logo", "") if alt else "Unknown"

            teams_logos.append({
                "team": team_name,
                "logo": src
            })

    # Create dataframe of teams and logos
    logos_df = pd.DataFrame(teams_logos)

    logos_df = logos_df.drop_duplicates()

    # Save csv
    logos_df.to_csv(file_path + f'/nba/team_logos.csv')


def main():
    salary_seasons = list(range(2011, 2026))
    stats_seasons = list(range(2012, 2027))

    salary_scrape(['nba', 'nfl', 'nhl'], salary_seasons, 'cap_total')
    salary_scrape(['mlb', 'epl'], salary_seasons, 'cash_total')

    salary_scrape(['nba'], salary_seasons, 'cap_total_league_pct')

    stats_scrape(stats_seasons, 'per_game')
    stats_scrape(stats_seasons, 'advanced')
    stats_scrape(stats_seasons, 'per_poss')

    stats_scrape(stats_seasons, 'per_game', playoffs=True)
    stats_scrape(stats_seasons, 'advanced', playoffs=True)
    stats_scrape(stats_seasons, 'per_poss', playoffs=True)

    headshot_map()
    get_logos()


if __name__ == '__main__':
    main()