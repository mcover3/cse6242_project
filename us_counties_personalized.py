import streamlit as st

import plotly.express as px
import pandas as pd, numpy as np

from collections import defaultdict

from choropleth import county_choropleth

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})


st.header("US County Explorer")
st.subheader("Tailor your next move or trip based on your preferences and personality.")

st.write("First, let's learn a bit about you. Your data is not collected.")

factors = [
    "Select All", "Religion", "Eco-Conscious", "Low Crime", "Low Pollution", "Good Schools",
    "People my age", "Rent within my budget", "Air BnBs within my budget", "Great food",
]

# relevant_factors_chosen = st.multiselect("Factors that matter to you (check all that apply):", relevant_factors)
col1, col2, col3 = st.columns(3)
factor_bool_dict = defaultdict(int)

for i, factor in enumerate(factors):
    if i % 3 == 0:
        with col1:
            factor_bool_dict[factor] = st.checkbox(factor)
    elif i % 3 == 1:
        with col2:
            factor_bool_dict[factor] = st.checkbox(factor)

    else:
        with col3:
            factor_bool_dict[factor] = st.checkbox(factor)

selected_factors = [
    x for x in factor_bool_dict.keys() if factor_bool_dict[x]
]

big5_bool = st.radio("""
Have you taken the Big 5 Personality test and know your percentile scores?
""", ["Yes", "No"], index=1)

# st.slider("Importance of feature X, scale 1-5", 0, 5)

importance_scale = {
    "not important to me": 0,
    "of little importance": 1,
    "somewhat important": 2,
    "very important": 4,
    "absolutely essential": 8
}

def importance_slider(county_variable, importance_scale=importance_scale):

    st.select_slider(county_variable, list(importance_scale.keys()))

# st.number_input("Trait Openness percentile", 0, 100)

with st.expander("Demographic Options"):
    for factor in selected_factors:
        importance_slider(factor)

if big5_bool == "Yes":
    with st.expander("Big 5 Personality Scores"):
        for trait in ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]:
            st.number_input(f"Trait {trait} percentile (1-99)", 1, 99, value=50, format="%d")
# st.download_button("Download your recommendations", 0)

st.plotly_chart(county_choropleth(df))

st.write("Sources:")