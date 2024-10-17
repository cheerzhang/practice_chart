import streamlit as st
import pandas as pd
import os, datetime


def load_data(csv_name):
    if os.path.exists(csv_name):
        df = pd.read_csv(csv_name)
    else:
        df = None
    return df


def main():
    df = load_data('./.local_db/main.csv')
    # menu
    menu = ["Simulation", "Real"]
    choice = st.sidebar.radio("Menu", menu)
    if choice == "Simulation":
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        start_date = st.date_input("When's the start day?", datetime.date.today())
        if start_date not in df['date'].values:
            st.write('not fond')
        else:
            st.write(df[df['date'] == start_date]['baseline'].values[0])