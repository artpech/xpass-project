import streamlit as st

import ast
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from xpass.utils import plot_pass
from xpass.params import *

from mplsoccer import Pitch

st.title("Demo - xpass-project")
st.write("Welcome to the xpass-project app.")


# Load validation file

val_file = os.path.join(PROJECT_HOME, "data", f"validation_{GENDER}_{SIZE}.csv")
validation = pd.read_csv(val_file)
sample_pass = validation.sample(1)
val_freeze_frame = sample_pass.iloc[0]["freeze_frame"]
val_freeze_frame = ast.literal_eval(val_freeze_frame)
teammates = [dct for dct in val_freeze_frame if dct["teammate"]]
opponents = [dct for dct in val_freeze_frame if not dct["teammate"]]
end_loc_innit = ast.literal_eval(sample_pass.iloc[0]["pass_end_location"])
end_loc_x_innit = end_loc_innit[0]
end_loc_y_innit = end_loc_innit[1]


teams_innit = {
    "Teammates" : {
        "n_players" : len(teammates),
        "x" : [dct["location"][0] for dct in teammates],
        "y" : [dct["location"][1] for dct in teammates]
    },
    "Opponents" : {
        "n_players" : len(opponents),
        "x" : [dct["location"][0] for dct in opponents],
        "y" : [dct["location"][1] for dct in opponents]
    }
}

with st.sidebar:

    teams = ["Teammates", "Opponents"]
    freeze_frame = []

    for team in teams:

        with st.expander(f"{team}"):
            st.write()
            innit_value = teams_innit[team]["n_players"]
            n_players = st.number_input(f"Number of players on team {team}", 1, 11, value = innit_value, step = 1, format = "%i")
            if team == "Teammates":
                n_home_players = n_players
            col1, col2 = st.columns(2)
            for i in range(n_players):
                x_innit = teams_innit[team]["x"][i]
                x_i = col1.number_input(f"Coordinate x for player {i+1}", 0.0, 120.0, value = x_innit, key = f"{team}_{i}_x")
                y_innit = teams_innit[team]["y"][i]
                y_i = col2.number_input(f"Coordinate y for player {i+1}", 0.0, 80.0, value = y_innit, key = f"{team}_{i}_y")
                player = {
                    "teammate" : team == "Teammates",
                    "actor" : False,
                    "keeper" : False,
                    "location" : [ x_i, y_i ]
                }
                freeze_frame.append(player)


    with st.expander("Other params"):
        passer = st.selectbox("Pick the passer", [f"player {i+1}" for i in range(n_home_players)])
        passer = int(passer.split(" ")[-1])
        st.write("End location of the pass:")
        col1, col2 = st.columns(2)
        x_end = col1.number_input(f"Coordinate x", 0.0, 120.0, value = end_loc_x_innit)
        y_end = col2.number_input(f"Coordinate y", 0.0, 80.0, value = end_loc_y_innit)

    freeze_frame[passer - 1]["actor"] = True
    x_start = freeze_frame[passer - 1]["location"][0]
    y_start = freeze_frame[passer - 1]["location"][1]
    pass_length = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
    if y_end >= y_start:
        pass_angle = np.arccos((x_end - x_start) / pass_length)
    else:
        pass_angle = - 1 * np.arccos((x_end - x_start) / pass_length)

# st.write(f"Pass length: {pass_length}")
# st.write(f"Pass angle: {pass_angle}")
# st.write(f"Freeze frame: {str(freeze_frame)}")

cols = ["location", "pass_end_location", "pass_angle", "freeze_frame"]
data = [[
    [x_start, y_start],
    [x_end, y_end],
    pass_angle,
    freeze_frame
]]
pass_df = pd.DataFrame(
    data = data,
    columns = cols
)

st.dataframe(pass_df)

fig, ax = plt.subplots()
ax = plot_pass(pass_df.iloc[0])
st.pyplot(fig)
