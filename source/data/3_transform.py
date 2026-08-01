import pandas as pd
import unicodedata
from bs4 import BeautifulSoup
import requests
from string import ascii_lowercase
import random
import time


raw_file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/raw'
processed_file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/processed'
final_file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/final'

first_season_url = 'https://www.basketball-reference.com/players/'

per_game_df = pd.read_csv(f'{processed_file_path}/regular_per_game_stats.csv', index_col=0)
playoffs_per_game_df = pd.read_csv(f'{processed_file_path}/playoffs_per_game_stats.csv', index_col=0)
advanced_df = pd.read_csv(f'{processed_file_path}/regular_advanced_stats.csv', index_col=0)
playoffs_advanced_df = pd.read_csv(f'{processed_file_path}/playoffs_advanced_stats.csv', index_col=0)
per_poss_df = pd.read_csv(f'{processed_file_path}/regular_per_poss_stats.csv', index_col=0)
playoffs_per_poss_df = pd.read_csv(f'{processed_file_path}/playoffs_per_poss_stats.csv', index_col=0)
team_logos_df = pd.read_csv(f'{raw_file_path}/nba/team_logos.csv', index_col=0)
player_images_df = pd.read_csv(f'{processed_file_path}/player_images_cleaned.csv', index_col=0)
cap_percent_df = pd.read_csv(f'{processed_file_path}/nba_cap_percentages.csv', index_col=0)
nba_salaries_df = pd.read_csv(f'{processed_file_path}/nba_salaries.csv', index_col=0)


def transform_league_salaries():
    """Transform league salary tables and merge into one table"""

    print('Transforming salary data..')

    # Transform and merge league salary data
    leagues = ['nba', 'nfl', 'nhl', 'mlb']
    all_leagues = []

    for league in leagues:
        df = pd.read_csv(f'{processed_file_path}/{league}_salaries.csv', index_col=0)

        df['league'] = league

        df['salary'] = pd.to_numeric(
            df['salary']
            .str.replace(',', '', regex=False)
            .str.extract(r'(\d+)')[0],
            errors='coerce'
        )

        grouped_df = df.groupby(['season', 'league'])['salary'].mean().reset_index(name='avg_salary')

        all_leagues.append(grouped_df)

    # Create dataframe
    all_salary_df = pd.concat(all_leagues, ignore_index=True)

    # Add yoy % change column
    all_salary_df = all_salary_df.sort_values(['league', 'season'])

    all_salary_df['yoy_pct_change'] = all_salary_df.groupby('league')['avg_salary'].pct_change()* 100

    all_salary_df['yoy_pct_change'] = all_salary_df['yoy_pct_change'].round(2)

    # Save csv
    all_salary_df.to_csv(f'{final_file_path}/all_league_salaries.csv')

    print('Salary data transformations are complete.')


def build_first_season_lookup():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    records = []

    for letter in ascii_lowercase:
        url = f'https://www.basketball-reference.com/players/{letter}/'

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f'Failed to retrieve {url}')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', id='players')

        if table is None:
            continue

        for row in table.select('tbody tr'):
            player_cell = row.find('th', {'data-stat': 'player'})

            if player_cell is None:
                continue

            player = player_cell.get_text(strip=True)
            player = player.replace('*', '').strip()

            try:
                player = player.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass

            from_year = row.find('td', {'data-stat': 'year_min'})

            if from_year is None:
                continue

            first_year = int(from_year.get_text(strip=True))
         
            season_start = first_year - 1
            season_end = str(first_year)[-2:]

            first_season = f'{season_start}-{season_end}'

            records.append({
                'Player': player,
                'First_Season': first_season
            })

    time.sleep(random.uniform(4, 7))

    return pd.DataFrame(records)


def transform_nba_stats():
    """Tranform NBA stats tables and merge into one table"""

    print('Transforming stats data..')

    # Filter advanced and per 100 dfs
    filtered_advanced = advanced_df[['Player', 'Season', 'MP', 'PER', 'TS%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']]
    filtered_per_poss = per_poss_df[['Player', 'Season', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', '3PA']]

    # Filter playoff stats
    filtered_playoffs_per_game = playoffs_per_game_df[['Player', 'Games', 'Games Started', 'Minutes Played Per Game', 'Season']]
    filtered_playoffs_advanced = playoffs_advanced_df[
        ['Player', 'Minutes Played', 'Player Efficiency Rating', 'True Shooting Percentage', 'Usage Percentage', 'Offensive Win Shares',
         'Defensive Win Shares', 'Win Shares', 'Win Shares Per 48 Minutes', 'OBPM', 'DBPM', 'BPM', 'VORP', 'Season']
    ]
    filtered_playoffs_per_poss = playoffs_per_poss_df[
        ['Player', 'Field Goal Percentage', '3-Point Field Goal Percentage', '3-Point Field Goal Attempts Per 100 Team Possessions',
         'Total Rebounds Per 100 Team Possessions', 'Assists Per 100 Team Possessions', 'Steals Per 100 Team Possessions', 'Blocks Per 100 Team Possessions',
         'Turnovers Per 100 Team Possessions', 'Points Per 100 Team Possessions', 'Season']
    ]

    # Merge all regular season stat dfs
    per_game_advanced_df = per_game_df.merge(filtered_advanced, how='inner', on=['Player', 'Season'], suffixes=('', '_adv'))
    merged_stat_df = per_game_advanced_df.merge(filtered_per_poss, how='inner', on=['Player', 'Season'], suffixes=('', '_p100'))

    # Merge all playoff stat dfs
    playoffs_per_game_advanced_df = filtered_playoffs_per_game.merge(filtered_playoffs_advanced, how='inner', on=['Player', 'Season'], suffixes=('', '_adv'))
    playoffs_merged_stat_df = playoffs_per_game_advanced_df.merge(filtered_playoffs_per_poss, how='inner', on=['Player', 'Season'], suffixes=('', '_p100'))

    # Merge regular season and playoffs
    merged_stat_df = merged_stat_df.merge(playoffs_merged_stat_df, how='left', on=['Player', 'Season'], suffixes=('', '_playoffs'))

    # Add column for normalized player names
    def normalize_name(name):
        if pd.isna(name):
            return name

        # Remove accents
        name = ''.join(
            char for char in unicodedata.normalize('NFKD', str(name))
            if not unicodedata.combining(char)
        )

        # Remove punctuation
        name = (
            name.replace('.', '')
                .replace("'", '')
                .replace('-', ' ')
        )

        # Standardize spacing and case
        return ' '.join(name.lower().split())
    
    # Add column with normalized names
    merged_stat_df['names_normalized'] = merged_stat_df['Player'].apply(normalize_name)
    nba_salaries_df['names_normalized']= nba_salaries_df['player'].apply(normalize_name)
    cap_percent_df['names_normalized']=cap_percent_df['player'].apply(normalize_name)

    # Merge salary and cap tables to stats table
    merged_salaries_stats = merged_stat_df.merge(nba_salaries_df, how='left', left_on=['names_normalized', 'Season'], right_on=['names_normalized', 'season'])
    final_merged_stats = merged_salaries_stats.merge(cap_percent_df, how='left', left_on=['names_normalized', 'Season'], right_on=['names_normalized', 'season'])
    
    # Get first season for each player
    first_season_df = build_first_season_lookup()

    first_season_df['names_normalized'] = (
        first_season_df['Player']
        .apply(normalize_name)
    )

    final_merged_stats = final_merged_stats.merge(
        first_season_df[['names_normalized', 'First_Season']],
        on='names_normalized',
        how='left'
    )

    # Calculate season number for the player row
    final_merged_stats['season_number'] = (
        final_merged_stats['Season'].str[:4].astype(int)
        - final_merged_stats['First_Season'].str[:4].astype(int)
        + 1
    )

    # Convert position to ints
    position_dummies = pd.get_dummies(
        final_merged_stats['Pos'],
        prefix='Pos',
        dtype=int
    )

    final_merged_stats = pd.concat(
        [final_merged_stats, position_dummies],
        axis=1
    )

    # Filter final dataframe
    final_stats_df = final_merged_stats[
        ['Player', 'Age', 'Team', 'Season', 'Pos_PG', 'Pos_SG', 'Pos_SF', 'Pos_PF', 'Pos_C', 'G', 'GS', 
        'PTS_p100', 'AST_p100', 'TRB_p100', 'STL_p100', 'BLK_p100', 'TOV_p100', '3PA_p100',
        'FG%', '3P%', 'eFG%', 'FT%', 'MP', 'PER', 'TS%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP',
        'Is_Allstar', 'Is_AllNBA', 'salary_x', 'salary_y', 'season_number',
        'Games', 'Games Started', 'Minutes Played Per Game','Minutes Played', 'Player Efficiency Rating', 'True Shooting Percentage', 
        'Usage Percentage', 'Offensive Win Shares', 'Defensive Win Shares', 'Win Shares', 'Win Shares Per 48 Minutes', 
        'OBPM_playoffs', 'DBPM_playoffs', 'BPM_playoffs', 'VORP_playoffs','Field Goal Percentage', '3-Point Field Goal Percentage', 
        '3-Point Field Goal Attempts Per 100 Team Possessions', 'Total Rebounds Per 100 Team Possessions', 'Assists Per 100 Team Possessions', 
        'Steals Per 100 Team Possessions', 'Blocks Per 100 Team Possessions','Turnovers Per 100 Team Possessions', 'Points Per 100 Team Possessions']
    ]
    
    # Rename salary columns and reformat season
    final_stats_df = final_stats_df.rename(columns={'salary_x': 'Salary', 'salary_y': 'PercentofCap'})
    final_stats_df['Season'] = final_stats_df['Season'].str[:4].astype(int)

    # Rename playoff stats columns 
    playoff_column_mapping = {
        'Games': 'playoffs_G',
        'Games Started': 'playoffs_GS',
        'Minutes Played Per Game': 'playoffs_MPG',
        'Minutes Played': 'playoffs_MP',
        'Player Efficiency Rating': 'playoffs_PER',
        'True Shooting Percentage': 'playoffs_TS%',
        'Usage Percentage': 'playoffs_USG%',
        'Offensive Win Shares': 'playoffs_OWS',
        'Defensive Win Shares': 'playoffs_DWS',
        'Win Shares': 'playoffs_WS',
        'Win Shares Per 48 Minutes': 'playoffs_WS48',
        'OBPM_playoffs': 'playoffs_OBPM',
        'DBPM_playoffs': 'playoffs_DBPM',
        'BPM_playoffs': 'playoffs_BPM',
        'VORP_playoffs': 'playoffs_VORP',
        'Field Goal Percentage': 'playoffs_FG%',
        '3-Point Field Goal Percentage': 'playoffs_3P%',
        '3-Point Field Goal Attempts Per 100 Team Possessions': 'playoffs_3PA100',
        'Total Rebounds Per 100 Team Possessions': 'playoffs_TRB100',
        'Assists Per 100 Team Possessions': 'playoffs_AST100',
        'Steals Per 100 Team Possessions': 'playoffs_STL100',
        'Blocks Per 100 Team Possessions': 'playoffs_BLK100',
        'Turnovers Per 100 Team Possessions': 'playoffs_TOV100',
        'Points Per 100 Team Possessions': 'playoffs_PTS100'
    }

    final_stats_df.rename(columns=playoff_column_mapping, inplace=True)

    # Fill the NAs for players that didnt make the playoffs
    playoff_cols = [col for col in final_stats_df.columns if col.startswith('playoffs_')]
    final_stats_df[playoff_cols] = final_stats_df[playoff_cols].fillna(0)

    # Save csv
    final_stats_df.to_csv(f'{final_file_path}/final_stats.csv')

    print('Stats data transformations are complete.')


def create_signings_df():
    """Create csv file for free agent signings"""

    free_agents_df = pd.DataFrame({
        'Player': [
            "Austin Reaves",
            "Isaiah Hartenstein",
            "Coby White",
            "Ayo Dosunmu",
            "Norman Powell",
            "John Collins",
            "Tari Eason",
            "Mitchell Robinson",
            "Tobias Harris",
            "Quentin Grimes"
        ],
        'NewTeam': [
            "LAL",
            "OKC",
            "CHO",
            "MIN",
            "CHI",
            "DET",
            "HOU",
            "BOS",
            "SAS",
            "LAL"
        ],
        'AAV': [
            46189080,
            25000000,
            24666667,
            22400000,
            22037500,
            17000000,
            16289892,
            15796200,
            15420100, 
            15000000
        ],
        'ContractYears': [
            4,
            3,
            3,
            5,
            2,
            3,
            5,
            3,
            2,
            4
        ]
    })

    free_agents_df['SalaryCap'] = 164961000
    free_agents_df['PercentofCap'] = free_agents_df['AAV'] / free_agents_df['SalaryCap']

    # Save csv
    free_agents_df.to_csv(f'{final_file_path}/free_agents.csv')


def main():
    transform_league_salaries()
    transform_nba_stats()
    create_signings_df()


if __name__ == '__main__':
    main()


