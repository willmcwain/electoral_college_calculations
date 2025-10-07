# Name:         Will McWain
# Email:        mcwainw@oregonstate.edu
# Description:  Program to build dataframes of election data for each US presidential
#               election since 2000, calculate the electoral vote allocation to
#               each state based on voter turnout via the Huntington-Hill method,
#               # and determine the number of electoral votes a candidate would
#               receive using proportional apportionment via the Sainte-Lague method.


import math
from collections import Counter, defaultdict
import pandas as pd

def build_turnout_from_pandas(csv_path, year):
    # Read the entire MIT county-level dataset
    df = pd.read_csv(csv_path)
    
    # Filter only the desired year (e.g., 2020 or 2016)
    df = df[df['year'] == year]

    # Drop rows with missing candidate or party first
    df = df.dropna(subset=['candidate', 'party'])
    
    # Strip whitespace from candidate and party names
    df['candidate'] = df['candidate'].str.strip()
    df['party'] = df['party'].str.strip()
    
    # Filter out only true summary rows (not candidate="OTHER" which represents third parties)
    df = df[~df['candidate'].str.upper().isin(['TOTAL VOTES CAST', 'REGISTERED VOTERS - TOTAL'])]

    # Handle mode column: Keep only TOTAL rows where they exist, otherwise keep all modes
    # This prevents double-counting in states with TOTAL rows while preserving states without them
    if 'mode' in df.columns:
        # Check if each state has TOTAL rows
        states_with_total = df[df['mode'].isin(['TOTAL', 'TOTAL VOTES'])]['state'].unique()
        
        # For states with TOTAL rows, keep only TOTAL. For others, keep all rows (will be summed later)
        df = df[
            (df['state'].isin(states_with_total) & df['mode'].isin(['TOTAL', 'TOTAL VOTES'])) |
            (~df['state'].isin(states_with_total))
        ]

    # Standardize party labels
    df['party'] = df['party'].str.upper().str.strip()
    
    # Normalize party names using substring matching
    def normalize_party(party):
        if 'DEMOCRAT' in party:
            return 'DEMOCRAT'
        elif 'REPUBLICAN' in party:
            return 'REPUBLICAN'
        else:
            return 'OTHER'
    
    df['party_normalized'] = df['party'].apply(normalize_party)

    # Group by state, county, candidate, and party to handle duplicate rows
    df = df.groupby(['state', 'county_name', 'candidate', 'party_normalized'], as_index=False)['candidatevotes'].sum()

    # Aggregate by state and party
    grouped = df.groupby(['state', 'party_normalized'], as_index=False)['candidatevotes'].sum()

    # Initialize output dict
    data = {}

    for state in grouped['state'].unique():
        state_data = grouped[grouped['state'] == state]

        dem_votes = int(state_data.loc[state_data['party_normalized'] == 'DEMOCRAT', 'candidatevotes'].sum())
        rep_votes = int(state_data.loc[state_data['party_normalized'] == 'REPUBLICAN', 'candidatevotes'].sum())
        other_votes = int(state_data.loc[state_data['party_normalized'] == 'OTHER', 'candidatevotes'].sum())
        total_votes = dem_votes + rep_votes + other_votes

        data[state] = {
            'Dem': dem_votes,
            'Rep': rep_votes,
            'Other': other_votes,
            'Total': total_votes
        }

    data = dict(sorted(data.items(), key=lambda kv: kv[0]))

    return data

voting_turnout_2024 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2024)

voting_turnout_2020 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2020)

voting_turnout_2016 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2016)

voting_turnout_2012 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2012)

voting_turnout_2008 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2008)

voting_turnout_2004 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2004)

voting_turnout_2000 = build_turnout_from_pandas('/Users/willmcwain/Downloads/countypres_2000-2024.csv', 2000)

total_electors = 538
floor = 1
national_totals = Counter()
# Calculate national totals first
national_raw_totals = Counter()
for state_data in voting_turnout_2000.values():
    for cand, votes in state_data.items():
        if cand != 'Total':
            national_raw_totals[cand] += votes

# Apply 5% threshold
total_votes_national = sum(national_raw_totals.values())
eligible_candidates = {
    cand for cand, votes in national_raw_totals.items()
    if votes / total_votes_national >= 0.05
}

print("Eligible candidates:", eligible_candidates)

electors = {state: floor for state in voting_turnout_2000}

remaining_electors = total_electors - sum(electors.values())

def priority(votes, n):
    if n == 0:
        return votes / math.sqrt(1 * 2)
    return votes / math.sqrt(n * (n + 1))

def sl_priority(votes, n):
    return votes / (2 * n + 1)

for _ in range(remaining_electors):
    state_priorities = {state: priority(voting_turnout_2000[state]['Total'], electors[state]) for state in electors}
    next_state = max(state_priorities, key=state_priorities.get)
    electors[next_state] += 1

def apportion_within_state(vote_dict, electors, eligible):
    # Start each candidate with 0
    allocation = {cand: 0 for cand in vote_dict if cand in eligible}

    if not allocation:
        return {}

    # Sainte-Lague loop for the given number of electors
    for _ in range(electors):
        cand_priorities = {
            cand: sl_priority(vote_dict[cand], allocation[cand])
            for cand in allocation
        }
        next_cand = max(cand_priorities, key=cand_priorities.get)
        allocation[next_cand] += 1

    return allocation

final_allocation = {}

for state, num_electors in electors.items():
    state_votes = voting_turnout_2000[state]
    final_allocation[state] = apportion_within_state(state_votes, num_electors, eligible_candidates)

for state, allocation in final_allocation.items():
    print(f"{state}: {allocation}")
    national_totals.update(allocation)
print("\nNational totals:", dict(national_totals))
