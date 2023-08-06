"""Load the data from the Statsbomb open data folder."""

import os
import json
import pandas as pd

from xpass.params import STATSBOMB_DATA, THREE_SIXTY, MATCHES, EVENTS, GENDER


def get_data():
    pass


def get_competitions(three_sixty: bool = False, gender: str = "All") -> pd.DataFrame:
    """Get a DataFrame with the list of competitions available in Statsbomb
    open data.

    Inputs:
        three_sixty (bool): Set to true to filter on competitions with Statsbomb 360 data
        gender (str): Set to "male", "female" or "all"

    Returns:
        A pandas DataFrame"""

    competitions = pd.read_json(
        os.path.join(os.path.join(STATSBOMB_DATA, "competitions.json"))
        )

    if three_sixty:
        competitions = competitions[~competitions["match_available_360"].isnull()]

    if gender in ["male", "female"]:
        competitions = competitions[competitions["competition_gender"] == gender]

    return competitions


def get_matches(competitions_df: pd.DataFrame) -> pd.DataFrame:
    """Get a DataFrame with the list of matches available in Statsbomb open data.

    Inputs:
        competitions_df: A pd.DataFrame with a list of competitions

    Returns:
        A pandas DataFrame"""

    comp_dict = competitions_df[["competition_id", "season_id"]].to_dict("split")

    matches_df_ls = []
    for competition, season in comp_dict["data"]:

        file = os.path.join(STATSBOMB_DATA, "matches", str(competition), f"{season}.json")

        with open(file) as f:
            data = json.load(f)
            matches_df  = pd.json_normalize(data, sep = "_")
            matches_df_ls.append(matches_df)

    matches = pd.concat(matches_df_ls).reset_index(drop = True)

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

    return frames, events



if __name__ == "__main__":
    competitions = get_competitions(three_sixty=True, gender="female")
    print("competitions: Done")
    matches = get_matches(competitions)
    print("matches: Done")
    frames, events = get_frames_and_events(matches)
    print("freeze frames and events: Done")
    print(frames)
