import pandas as pd

source_file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/raw'
dest_file_path = '/Users/natemekonen/Desktop/Data_Projects/nba_ml_salary_analysis/data/processed'

def clean_stats(seasons, stat_type):
    """Clean and concatenate player stats tables"""

    print(f'Cleaning regular season {stat_type} stats data..')

    all_dfs = []

    for season in seasons:
        df = pd.read_csv(f'{source_file_path}/nba_stats/{stat_type}/regular_{season}_{stat_type}_stats.csv', index_col=0)

        # Data transformations
        df = df[df['Player'] != 'League Average']

        df.drop_duplicates(subset=['Rk', 'Player'], inplace=True)

        df['Is_Allstar'] = df['Awards'].str.contains('AS', na=False).astype(int)

        df['Is_AllNBA'] = df['Awards'].str.contains('NBA', na=False).astype(int)

        df['Season'] = f'{str(season-1)}-{str(season)}'

        df['Awards'] = df['Awards'].fillna('None')

        if stat_type == 'per_game' or stat_type == 'per_poss':
            df[['FG%', '3P%', '2P%', 'eFG%', 'FT%']] = df[['FG%', '3P%', '2P%', 'eFG%', 'FT%']].fillna(0)
        
        if stat_type == 'advanced':
            df[['TS%', '3PAr', 'FTr', 'TOV%']] = df[['TS%', '3PAr', 'FTr', 'TOV%']].fillna(0)
        
        # Add dataframe to list of dataframes
        all_dfs.append(df)

    print(f'Concatenating regular season {stat_type} stats data..')

    # Concatenate dataframes
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Save csv
    final_df.to_csv(f'{dest_file_path}/regular_{stat_type}_stats.csv')

    print(f'Regular season {stat_type} stats data has been cleaned and concatenated.')


def clean_playoff_stats(seasons, stat_type):
    """Clean and concatenate playoff stats tables"""

    print(f'Cleaning playoff {stat_type} stats data..')

    all_dfs = []

    for season in seasons:
        df = pd.read_csv(f'{source_file_path}/nba_stats/{stat_type}/playoffs_{season}_{stat_type}_stats.csv', index_col=0)

        # Data transformations
        df = df[df['Player'] != 'Player']

        df['Player'] = df['Player'].str.replace('*', '', regex=False).str.strip()

        df.drop_duplicates(subset=['Rk', 'Player'], inplace=True)

        df['Season'] = f'{str(season-1)}-{str(season)}'

        if stat_type == 'per_game':
            df[['Field Goal Percentage', '3-Point Field Goal Percentage', '2-Point Field Goal Percentage', 'Effective Field Goal Percentage', 'Free Throw Percentage']] = df[
                ['Field Goal Percentage', '3-Point Field Goal Percentage', '2-Point Field Goal Percentage', 'Effective Field Goal Percentage', 'Free Throw Percentage']
            ].fillna(0)
        
        if stat_type == 'per_poss':
            df[['Field Goal Percentage', '3-Point Field Goal Percentage', '2-Point Field Goal Percentage', 'Free Throw Percentage']] = df[
                ['Field Goal Percentage', '3-Point Field Goal Percentage', '2-Point Field Goal Percentage', 'Free Throw Percentage']
            ].fillna(0)

        if stat_type == 'advanced':
            df[['True Shooting Percentage', '3-Point Attempt Rate', 'Free Throw Attempt Rate', 'Turnover Percentage']] = df[
                ['True Shooting Percentage', '3-Point Attempt Rate', 'Free Throw Attempt Rate', 'Turnover Percentage']
            ].fillna(0)
        
        # Add dataframe to list of dataframes
        all_dfs.append(df)

    print(f'Concatenating playoff {stat_type} stats data..')

    # Concatenate dataframes
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Save csv
    final_df.to_csv(f'{dest_file_path}/playoffs_{stat_type}_stats.csv')

    print(f'Playoff {stat_type} stats data has been cleaned and concatenated.')


def clean_salaries(seasons, league):
    """Clean NBA player salaries tables"""

    print(f'Cleaning {league} salary data..')

    all_dfs = []

    for season in seasons:
        df = pd.read_csv(f'{source_file_path}/{league}/{league}_{season}_salaries.csv', index_col=0)

        # Data transformations
        df['season'] = f'{str(season)}-{str(season+1)}'

        df = df[df['salary'].str.contains(r'\$', na=False, regex=True)]

        df = df[['season', 'player', 'salary']]

        # Add dataframe to list of dataframes
        all_dfs.append(df)

    print(f'Concatenating {league} salary data..')

    # Concatenate dataframes
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Save csv
    final_df.to_csv(f'{dest_file_path}/{league}_salaries.csv')


def clean_nba_cap_percentages(seasons):
    """Clean NBA player cap percentage tables"""

    print(f'Cleaning cap data..')

    all_dfs = []

    for season in seasons:
        df = pd.read_csv(f'{source_file_path}/nba/nba_{season}_cap_percentages.csv', index_col=0)

        # Data transformations
        df['season'] = f'{str(season)}-{str(season+1)}'

        df = df[df['salary'].str.contains(r'\%', na=False, regex=True)]

        df = df[['season', 'player', 'salary']]

        # Add dataframe to list of dataframes
        all_dfs.append(df)

    print(f'Concatenating cap data..')

    # Concatenate dataframes
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Save csv
    final_df.to_csv(f'{dest_file_path}/nba_cap_percentages.csv')


def clean_logos():
    """Clean logos table"""
    
    df = pd.read_csv(f'{source_file_path}/nba_stats/player_images.csv', index_col=0)

    # Filter df and drop duplicates
    df = df[['Player', 'Images']].drop_duplicates()

    # Save csv
    df.to_csv(f'{dest_file_path}/player_images_cleaned.csv')


def main():
    stat_seasons = list(range(2012, 2027))
    salary_seasons = list(range(2011, 2026))

    clean_stats(stat_seasons, 'per_game')
    clean_stats(stat_seasons, 'advanced')
    clean_stats(stat_seasons, 'per_poss')

    clean_playoff_stats(stat_seasons, 'per_game')
    clean_playoff_stats(stat_seasons, 'advanced')
    clean_playoff_stats(stat_seasons, 'per_poss')

    clean_salaries(salary_seasons, 'nba')
    clean_salaries(salary_seasons, 'nhl')
    clean_salaries(salary_seasons, 'nfl')
    clean_salaries(salary_seasons, 'mlb')
    clean_nba_cap_percentages(salary_seasons)

    clean_logos()


if __name__ == '__main__':
    main()