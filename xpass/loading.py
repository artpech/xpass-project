"""Load the data from the Statsbomb open data folder."""

import os

import json
import pandas as pd

from xpass.params import PROJECT_HOME, STATSBOMB_DATA, THREE_SIXTY, MATCHES, EVENTS, GENDER
from xpass.utils import return_as_list

def get_data():
    pass


def get_competitions() -> pd.DataFrame:
    """Get a DataFrame with the list of competitions available in Statsbomb
    open data.

    Returns:
        A pandas DataFrame"""

    csv_file = os.path.join(PROJECT_HOME, "data", f"competitions_{GENDER}.csv")

    if os.path.isfile(csv_file):
        competitions = pd.read_csv(csv_file)

    else:
        competitions = pd.read_json(os.path.join(STATSBOMB_DATA, "competitions.json"))
        competitions = competitions[~competitions["match_available_360"].isnull()]

        if GENDER.lower() in ["male", "female"]:
            competitions = competitions[competitions["competition_gender"] == GENDER.lower()]

        competitions.to_csv(csv_file, index = False)

    return competitions


def get_matches(competitions_df: pd.DataFrame) -> pd.DataFrame:
    """Get a DataFrame with the list of matches available in Statsbomb open data.

    Inputs:
        competitions_df: A pd.DataFrame with a list of competitions

    Returns:
        A pandas DataFrame"""

    csv_file = os.path.join(PROJECT_HOME, "data", f"matches_{GENDER}.csv")

    if os.path.isfile(csv_file):
        matches = pd.read_csv(csv_file)

    else:

        comp_dict = competitions_df[["competition_id", "season_id"]].to_dict("split")

        matches_df_ls = []
        for competition, season in comp_dict["data"]:

            file = os.path.join(STATSBOMB_DATA, "matches", str(competition), f"{season}.json")

            with open(file) as f:
                data = json.load(f)
                matches_df  = pd.json_normalize(data, sep = "_")
                matches_df_ls.append(matches_df)

        matches = pd.concat(matches_df_ls).reset_index(drop = True)

        matches.to_csv(csv_file, index = False)

    return matches


def get_frames_and_events(matches_df: pd.DataFrame) -> tuple:
    """Get a tuple of DataFrame with the freeze frames and events
    in a list of matches.
    The 1st DataFrame is the freeze frames pd.DataFrame.
    The second DataFrame is the events pd.DataFrame.

    Inputs:
        matches_df: A pd.DataFrame with a list of matches

    Returns:
        A tuple of two pandas DataFrame: (frames, events)"""

    csv_file_frames = os.path.join(PROJECT_HOME, "data", f"frames_{GENDER}.csv")
    csv_file_events = os.path.join(PROJECT_HOME, "data", f"events_{GENDER}.csv")

    if os.path.isfile(csv_file_frames) and os.path.isfile(csv_file_events):
        frames = pd.read_csv(csv_file_frames)
        events = pd.read_csv(csv_file_events)

    else:

        frames_df_ls = []
        frames_not_found = []

        for match_id in matches_df["match_id"].unique():

            file = os.path.join(THREE_SIXTY, f"{match_id}.json")
            try:
                with open(file) as f:
                    data = json.load(f)
                    frames_df  = pd.json_normalize(data, sep = "_")
                    frames_df_ls.append(frames_df)
            except:
                frames_not_found.append(match_id)

        frames = pd.concat(frames_df_ls).reset_index(drop = True)

        events_df_ls = []
        events_not_found = []

        for match_id in matches_df["match_id"].unique():

            if match_id in frames_not_found:
                pass # events have no freeze frames

            else:
                file = os.path.join(EVENTS, f"{match_id}.json")
                try:
                    with open(file) as f:
                        data = json.load(f)
                        events_df  = pd.json_normalize(data, sep = "_")
                        events_df["match_id"] = match_id
                        events_df_ls.append(events_df)
                except:
                    events_not_found.append(match_id)

        events = pd.concat(events_df_ls).reset_index(drop = True)

        col_origin = [
            "match_date", "competition_competition_name", "home_team_home_team_gender",
            "home_team_home_team_name", "away_team_away_team_name",
        ]

        col_destination = [
            "match_date", "competition_name", "gender",
            "home_team_name", "away_team_name"
        ]

        events[col_destination] = events.apply(
            lambda x : matches_df[matches_df["match_id"] == x["match_id"]].iloc[0][col_origin],
            axis = 1, result_type = "expand"
        )

        frames.to_csv(csv_file_frames, index = False)
        events.to_csv(csv_file_events, index = False)

    return frames, events


def get_passes(events_df: pd.DataFrame, frames_df: pd.DataFrame) -> pd.DataFrame:
    """Get a DataFrame with the passes and relevent data
    from a DataFrame of events and a DataFrame of freeze frames.

    Inputs:
        events_df: A pd.DataFrame with a list of events
        frames_df: A pd.DataFrame with the freeze frames

    Returns:
        A pandas DataFrame with all the passes and their associated freeze frames"""

    csv_file = os.path.join(PROJECT_HOME, "data", f"passes_{GENDER}.csv")

    if os.path.isfile(csv_file):
        passes = pd.read_csv(csv_file)

    else:

        passes = events_df[events_df["type_name"] == "Pass"].reset_index(drop = True)

        columns_to_keep = [
            "id", "match_date", "competition_name", "gender",
            "home_team_name", "away_team_name",
            "index", "period", "timestamp", "minute", "second",
            "possession", "duration", "type_id", "type_name",
            "possession_team_id", "possession_team_name", "play_pattern_id",
            "play_pattern_name", "team_id", "team_name", "related_events",
            "location", "player_id", "player_name", "position_id",
            "position_name", "pass_recipient_id", "pass_recipient_name",
            "pass_length", "pass_angle", "pass_height_id", "pass_height_name",
            "pass_end_location", "pass_body_part_id", "pass_body_part_name",
            "pass_type_id", "pass_type_name", "pass_cross", "pass_outcome_id",
            "pass_outcome_name", "under_pressure", "pass_assisted_shot_id",
            "pass_shot_assist", "off_camera", "pass_deflected", "counterpress",
            "pass_aerial_won", "pass_switch", "out", "pass_outswinging",
            "pass_technique_id", "pass_technique_name", "pass_cut_back",
            "pass_goal_assist", "pass_through_ball", "pass_miscommunication",
            "match_id", "pass_no_touch", "pass_straight", "pass_inswinging"
            ]

        passes = passes[columns_to_keep]

        passes = passes.merge(
            frames_df, how = "left", left_on = "id", right_on = "event_uuid")

        passes = passes[~passes["freeze_frame"].isnull()]

        passes.to_csv(csv_file, index = False)

    return passes


def get_passes_preprocessed(passes_df: pd.DataFrame, balance_ratio = 2) -> pd.DataFrame:
    """Returns the DataFrame of passes for ML pipeline

    Inputs:
        passes_df (pd.DataFrame): The pd.DataFrame of passes
        balance_ratio (int): The ratio between the number of sucessful and unsuccesful passes.
            Default ratio is 2. Specify a ratio of 1 for exact same number of sucessful
            and unsuccesful passes. Specify "None" to keep imbalanced data.

    Returns:
        A preprocessed passes pd.DataFrame

    """

    csv_file = os.path.join(PROJECT_HOME, "data", f"passes_preprocessed_{GENDER}.csv")

    if os.path.isfile(csv_file):
        passes_preprocessed = pd.read_csv(csv_file)

    else:
        passes_df["location"] = passes_df["location"].map(return_as_list)
        passes_df["location_x"] = passes_df["location"].map(lambda x : x[0])
        passes_df["location_y"] = passes_df["location"].map(lambda x : x[1])

        failure = ["Incomplete", "Out", "Pass Offside"]
        passes_df["success"] = passes_df["pass_outcome_name"].map(lambda x: int(x not in failure))

        useful_col = [
            "location_x", "location_y", "play_pattern_name",
            "pass_angle", "pass_height_id", "pass_body_part_name",
            "freeze_frame", "success"]

        passes_preprocessed = passes_df[useful_col]

        passes_preprocessed.to_csv(csv_file, index = False)

    if balance_ratio:
        print(f"Balancing the data with a ratio of {balance_ratio} between successful and unsuccessful passes...")
        n_unsuccesful = passes_preprocessed["success"].value_counts()[0]
        passes_preprocessed_0 = passes_preprocessed[passes_preprocessed["success"] == 0]
        passes_preprocessed_1 = passes_preprocessed[passes_preprocessed["success"] == 1].sample(balance_ratio * n_unsuccesful)
        passes_preprocessed = pd.concat([passes_preprocessed_0, passes_preprocessed_1]).sample(frac = 1)
        print("Data was correctly balanced.")

    return passes_preprocessed





if __name__ == "__main__":
    competitions = get_competitions()
    print("competitions: Done")
    # matches = get_matches(competitions)
    # print("matches: Done")
    # frames, events = get_frames_and_events(matches)
    # print("freeze frames and events: Done")
    # passes = get_passes(events, frames)
    # print("passes: Done")
    # print(passes.sample(1).iloc[0])
    # passes_preprocessed = get_passes_preprocessed(passes)
    # print("passes preprocessed: Done")
    # print(passes_preprocessed.sample(1).iloc[0])
