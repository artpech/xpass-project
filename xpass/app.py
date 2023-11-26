import streamlit as st
import numpy as np

st.write("Welcome to the xpass-project app.")

teams = ["Home Team", "Away Team"]

for team in teams:

    with st.expander(f"{team}"):
        st.write()
        nhome_players = st.slider(f"Number of players on {team}", 1, 11, 1)
        col1, col2 = st.columns(2)
        for i in range(nhome_players):
            col1.number_input(f"Coordinate x for player {i}", 0, 100, np.random.randint(1, 100))
            col2.number_input(f"Coordinate y for player {i}", 0, 100, np.random.randint(1, 100))
