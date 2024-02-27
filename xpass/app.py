import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from xpass.utils import plot_pass

from mplsoccer import Pitch

st.write("Welcome to the xpass-project app.")

with st.sidebar:

    teams = ["Home Team", "Away Team"]
    freeze_frame = []

    for team in teams:

        with st.expander(f"{team}"):
            st.write()
            n_players = st.number_input(f"Number of players on {team}", 1, 11, step = 1, format = "%i")
            if team == "Home Team":
                n_home_players = n_players
            col1, col2 = st.columns(2)
            for i in range(n_players):
                x_i = col1.number_input(f"Coordinate x for player {i+1}", 0, 120, 60, key = f"{team}_{i}_x")
                y_i = col2.number_input(f"Coordinate y for player {i+1}", 0, 80, 40, key = f"{team}_{i}_y")
                player = {
                    "teammate" : team == "Home Team",
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
        x_end = col1.number_input(f"Coordinate x", 0, 120, 60)
        y_end = col2.number_input(f"Coordinate y", 0, 80, 40)

    freeze_frame[passer - 1]["actor"] = True
    x_start = freeze_frame[passer - 1]["location"][0]
    y_start = freeze_frame[passer - 1]["location"][1]
    pass_length = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
    if y_end >= y_start:
        pass_angle = np.arccos((x_end - x_start) / pass_length)
    else:
        pass_angle = - 1 * np.arccos((x_end - x_start) / pass_length)

st.write(f"Pass length: {pass_length}")
st.write(f"Pass angle: {pass_angle}")
st.write(f"Freeze frame: {str(freeze_frame)}")

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
