import pandas as pd

# loads player data from Excel and prepares a list of all eligible positions for each player
def load_and_prepare_data(file_path):
    df = pd.read_excel(file_path, sheet_name='Lineup')
    for i in range(1, 7):
        df[f"Position{i}"] = df[f"Position{i}"].fillna("").str.strip()
    df["All_Positions"] = df[[f"Position{i}" for i in range(1, 7)]].values.tolist()
    return df

# calculates a custom batting score for a player based on weighted stats
def batting_score(player, contact_col, power_col):
    return (
        player[contact_col] * 0.3 +
        player[power_col] * 0.25 +
        player["Vision"] * 0.15 +
        player["Clutch"] * 0.15 +
        player["Speed"] * 0.10 +
        player["AtBats"] * 0.05 +
        player["HR"] * 0.05 +
        player["RBI"] * 0.05 +
        player["Average"] * 0.05
    )

# builds a dictionary mapping each needed position to all eligible player candidates, with scores
def build_position_candidates(df, positions_needed, contact_col, power_col):
    position_candidates = {}
    for pos in positions_needed:
        # filter players who can play this position
        candidates = df[df["All_Positions"].apply(lambda x: pos in x)].copy()
        # calculate and add the batting score for each candidate
        candidates["Score"] = candidates.apply(lambda row: batting_score(row, contact_col, power_col), axis=1)
        position_candidates[pos] = candidates
    return position_candidates

# recursively tries all possible unique player assignments to positions to maximize total score
def backtrack_lineup(position_candidates, positions_needed, idx, used_players, current_lineup, best_result):
    # best case: all positions filled
    if idx == len(positions_needed):
        total_score = sum(player["Score"] for player in current_lineup)
        # update best result if this lineup is better
        if total_score > best_result["score"]:
            best_result["score"] = total_score
            best_result["lineup"] = list(current_lineup)
        return

    pos = positions_needed[idx]
    candidates = position_candidates[pos]
    for _, player in candidates.iterrows():
        player_name = player["Player"]
        # skip if player already used
        if player_name in used_players:
            continue
        # add player to current lineup and recurse
        current_lineup.append({
            "Position": pos,
            "Player": player_name,
            "Bats": player["Bats"],
            "Average": player["Average"],
            "HR": player["HR"],
            "RBI": player["RBI"],
            "Speed": player["Speed"],
            "AtBats": player["AtBats"],
            "Score": round(player["Score"], 2)
        })
        used_players.add(player_name)
        backtrack_lineup(position_candidates, positions_needed, idx + 1, used_players, current_lineup, best_result)
        # backtrack: remove player and try next candidate
        used_players.remove(player_name)
        current_lineup.pop()

# finds the best possible lineup using backtracking, ensuring one unique player per position
def find_best_lineup_backtracking(df, positions_needed, contact_col, power_col):
    position_candidates = build_position_candidates(df, positions_needed, contact_col, power_col)
    best_result = {"score": float('-inf'), "lineup": []}
    backtrack_lineup(position_candidates, positions_needed, 0, set(), [], best_result)
    # if not all positions could be filled, fill with N/A
    lineup = best_result["lineup"]
    if len(lineup) < len(positions_needed):
        for i in range(len(lineup), len(positions_needed)):
            lineup.append({
                "Position": positions_needed[i],
                "Player": "N/A",
                "Bats": "",
                "Average": 0,
                "HR": 0,
                "RBI": 0,
                "Speed": 0,
                "AtBats": 0,
                "Score": 0
            })
    # sort by score for optimal batting order
    lineup_sorted = sorted(lineup, key=lambda x: x["Score"], reverse=True)
    return pd.DataFrame(lineup_sorted)

# main entry point: loads data, generates lineups for RHP and LHP, and prints results
def main():
    file_path = 'MLB2K25-AI.xlsx'
    positions_needed = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
    df_updated = load_and_prepare_data(file_path)
    lineup_vs_rhp_sorted = find_best_lineup_backtracking(df_updated, positions_needed, contact_col="ContactR", power_col="PowerR")
    lineup_vs_lhp_sorted = find_best_lineup_backtracking(df_updated, positions_needed, contact_col="ContactL", power_col="PowerL")

    print("Lineup vs Right-Handed Pitching:")
    print(lineup_vs_rhp_sorted)
    print("\nLineup vs Left-Handed Pitching:")
    print(lineup_vs_lhp_sorted)

if __name__ == "__main__":
    main()