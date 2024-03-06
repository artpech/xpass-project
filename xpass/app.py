import streamlit as st

import ast
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

from xpass.utils import plot_pass
from xpass.loading import get_passes_preprocessed
from xpass.params import *
from xpass.model import load_model

from mplsoccer import Pitch


# ------ FUNCTIONS ------

#@st.cache
# def init_page_with_demo_pass():
#     demo_file = os.path.join(PROJECT_HOME, "data", f"demo_{GENDER}_{SIZE}.csv")
#     demo = pd.read_csv(demo_file)
#     sample_pass_init = demo.sample(1)
#     sample_freeze_frame = sample_pass_init.iloc[0]["freeze_frame"]
#     sample_freeze_frame = ast.literal_eval(sample_freeze_frame)
#     teammates = [dct for dct in sample_freeze_frame if dct["teammate"]]
#     actor_index = [teammates.index(dct) for dct in teammates if dct["actor"]][0]
#     opponents = [dct for dct in sample_freeze_frame if not dct["teammate"]]
#     end_loc_init = ast.literal_eval(sample_pass_init.iloc[0]["pass_end_location"])
#     end_loc_x_init = end_loc_init[0]
#     end_loc_y_init = end_loc_init[1]

#     teams_init = {
#         "Teammates" : {
#             "n_players" : len(teammates),
#             "actor_index" : actor_index,
#             "x" : [dct["location"][0] for dct in teammates],
#             "y" : [dct["location"][1] for dct in teammates]
#         },
#         "Opponents" : {
#             "n_players" : len(opponents),
#             "x" : [dct["location"][0] for dct in opponents],
#             "y" : [dct["location"][1] for dct in opponents]
#         }
#     }

#     return sample_pass_init, teams_init, end_loc_x_init, end_loc_y_init


# ------ INITIALIZATION ------

# sample_pass_init, teams_init, end_loc_x_init, end_loc_y_init = init_page_with_demo_pass()
# sample_pass_preprocessed_init = get_passes_preprocessed(sample_pass_init)

# model = load_model()


if "model" not in st.session_state:
    st.session_state["model"] = load_model()

if "demo" not in st.session_state:
    demo_file = os.path.join(PROJECT_HOME, "data", f"demo_{GENDER}_{SIZE}.csv")
    st.session_state["demo"] = pd.read_csv(demo_file)

# Initialize pass information

if "sample_pass_init" not in st.session_state:
    st.session_state["sample_pass_init"] = st.session_state["demo"].sample(1)

if "sample_pass_preprocessed_init" not in st.session_state:
    st.session_state["sample_pass_preprocessed_init"] = get_passes_preprocessed(st.session_state["sample_pass_init"])

if "freeze_frame_init" not in st.session_state:
    freeze_frame = st.session_state["sample_pass_init"].iloc[0]["freeze_frame"]
    st.session_state["freeze_frame_init"] = ast.literal_eval(freeze_frame)

if "teams_init" not in st.session_state:
    teammates = [dct for dct in st.session_state["freeze_frame_init"] if dct["teammate"]]
    actor_index = [teammates.index(dct) for dct in teammates if dct["actor"]][0]
    opponents = [dct for dct in st.session_state["freeze_frame_init"] if not dct["teammate"]]

    st.session_state["teams_init"] = {
        "Teammates" : {
            "n_players" : len(teammates),
            "actor_index" : actor_index,
            "x" : [dct["location"][0] for dct in teammates],
            "y" : [dct["location"][1] for dct in teammates]
        },
        "Opponents" : {
            "n_players" : len(opponents),
            "x" : [dct["location"][0] for dct in opponents],
            "y" : [dct["location"][1] for dct in opponents]
        }
    }

if "end_loc_init" not in st.session_state:
    st.session_state["end_loc_init"] = ast.literal_eval(
        st.session_state["sample_pass_init"].iloc[0]["pass_end_location"])

play_pattern_name = st.session_state["sample_pass_preprocessed_init"]["play_pattern_name"].iloc[0]
st.write(play_pattern_name)
pass_height_id = st.session_state["sample_pass_preprocessed_init"]["pass_height_id"].iloc[0]
pass_body_part_name = st.session_state["sample_pass_preprocessed_init"]["pass_body_part_name"].iloc[0]



# ------ APP ------

st.title("Demo - xpass-project")

st.subheader("Randomly selected pass:")

st.write("""
         Here is a pass randomly selected from the validation set of passes.
         You can manually change the settings of the pass using the sidebar on the left
         (number of players in both team, location of the players, passing player, end location of the pass).
         """)

st.dataframe(st.session_state["sample_pass_init"])
st.dataframe(st.session_state["sample_pass_preprocessed_init"])

with st.sidebar:

    st.subheader("Randomly select a new pass:")
    if st.button("New pass"):
        st.session_state.clear()
        st.experimental_rerun()


    st.subheader("Change the pass parameters:")

    teams = ["Teammates", "Opponents"]

    if "freeze_frame" not in st.session_state:
        st.session_state["freeze_frame"] = []

    for team in teams:

        with st.expander(f"{team}"):
            st.write()
            init_value = st.session_state["teams_init"][team]["n_players"]
            n_players = st.number_input(f"Number of players on team {team}", 1, 11, value = init_value, step = 1, format = "%i")
            if team == "Teammates":
                n_home_players = n_players
            col1, col2 = st.columns(2)
            for i in range(int(n_players)):
                try:
                    x_init = st.session_state["teams_init"][team]["x"][i]
                except:
                    x_init = 60.0
                x_i = col1.number_input(f"Coordinate x for player {i+1}", 0.0, 120.0, value = x_init, key = f"{team}_{i}_x")
                try:
                    y_init = st.session_state["teams_init"][team]["y"][i]
                except:
                    y_init = 40.0
                y_i = col2.number_input(f"Coordinate y for player {i+1}", 0.0, 80.0, value = y_init, key = f"{team}_{i}_y")
                player = {
                    "teammate" : team == "Teammates",
                    "actor" : False,
                    "keeper" : False,
                    "location" : [ x_i, y_i ]
                }
                st.session_state["freeze_frame"].append(player)


    with st.expander("Other params"):
        preselected_index = st.session_state["teams_init"]["Teammates"]["actor_index"]
        passer = st.selectbox(
            "Pick the passer", [f"player {i+1}" for i in range(int(n_home_players))],
            index = preselected_index
            )
        passer = int(passer.split(" ")[-1])
        st.write("End location of the pass:")
        col1, col2 = st.columns(2)
        x_end = col1.number_input(f"Coordinate x", 0.0, 120.0, value = st.session_state["end_loc_init"][0])
        y_end = col2.number_input(f"Coordinate y", 0.0, 80.0, value = st.session_state["end_loc_init"][1])

    st.session_state["freeze_frame"][passer - 1]["actor"] = True
    x_start = st.session_state["freeze_frame"][passer - 1]["location"][0]
    y_start = st.session_state["freeze_frame"][passer - 1]["location"][1]
    pass_length = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
    if y_end >= y_start:
        pass_angle = np.arccos((x_end - x_start) / pass_length)
    else:
        pass_angle = - 1 * np.arccos((x_end - x_start) / pass_length)

    # ------ PASS FOR PREDICTION ------

    cols = ["location_x", "location_y", "play_pattern_name", "pass_angle",
            "pass_height_id", "pass_body_part_name", "freeze_frame", "pass_end_location"]

    data = [[x_start, y_start, play_pattern_name, pass_angle, pass_height_id,
             pass_body_part_name, st.session_state["freeze_frame"], [x_end, y_end]]]

    # st.write(data)

    # data = [[x_start, y_start,
    #     x_end, y_end],
    #     pass_angle,
    #     st.session_state["freeze_frame"]
    # ]]

    pass_df = pd.DataFrame(data = data, columns = cols)
    st.write(len(st.session_state["freeze_frame"]))

    # ------ PREDICTION ------
    st.write("")
    if st.button("Predict"):

        # sample_pass_preprocessed = get_passes_preprocessed(st.session_state["sample_pass_init"])
        # pass_preprocessed = get_passes_preprocessed(pass_df)

        outcome = st.session_state["model"].predict(pass_df)
        outcome_map = {0 : "incomplete pass", 1 : "succesful pass"}
        outcome = outcome_map[outcome[0]]

        proba = st.session_state["model"].predict_proba(pass_df)
        proba = round(100 * proba[0][1], 1)

        # col1, col2 = st.columns(2)
        # col1.write("Outcome prediction:")
        # col1.write(f"{outcome}")

        # col2.write("Success probability:")

        # col2.write(f"{proba}%")

        st.dataframe(
            pd.DataFrame.from_dict(
                [{
                    "Outcome prediction" : f"{outcome}",
                    "Success probability" : f"{proba}%"
                }]
            )
        )


# st.write(f"Pass length: {pass_length}")
# st.write(f"Pass angle: {pass_angle}")
# st.write(f"Freeze frame: {str(freeze_frame)}")

st.subheader("Model input")
st.dataframe(pass_df)

st.subheader("Pass plot")
st.dataframe(pass_df)
fig, ax = plt.subplots()
ax = plot_pass(pass_df.iloc[0])
st.pyplot(fig)
