import streamlit as st
import pandas as pd


df = pd.DataFrame([
    {"name": "HDFC", "ltp": 123, "quantity": 11, "final": 0},
    {"name": "Infy", "ltp": 123, "quantity": 11,  "final": 0},
    {"name": "RBL", "ltp": 123, "quantity": 11,  "final": 0},
])


def df_on_change(df):
    state = st.session_state["df_editor"]
    for index, updates in state["edited_rows"].items():
        
        for key, value in updates.items():
            st.session_state["df"].loc[st.session_state["df"].index == index, key] = value
            ltp = st.session_state["df"].loc[st.session_state["df"].index == index, "ltp"]
            quantity = st.session_state["df"].loc[st.session_state["df"].index == index, "quantity"]  
            print(ltp, quantity)
            st.session_state["df"].loc[st.session_state["df"].index == index, "final"] = ltp * quantity


def editor():
    if "df" not in st.session_state:
        st.session_state["df"] = df
    st.data_editor(st.session_state["df"], key="df_editor", on_change=df_on_change, args=[df], num_rows='dynamic')


editor()