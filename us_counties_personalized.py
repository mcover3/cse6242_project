import streamlit as st

import plotly.express as px
import pandas as pd, numpy as np

from collections import defaultdict

from choropleth import county_choropleth

df = pd.read_csv("cluster_merge_clean_normalized.csv", dtype={"fips": str})

st.header("US County Explorer")
st.subheader("Tailor your next move or trip based on your preferences and personality.")

factor_colname_dict = {
    "Belief in Science": 'Belief In Science_sc_norm',
    "Collectivism": "Collectivism_sc_norm",
    "Employment Rate": "Employment Rate_sc_norm",
    "Entrepreneurship": "Entrepreneurship_sc_norm",
    "Gender Equality": "Gender Equality_sc_norm",
    "Income Mobility": "Income Mobility_sc_norm",
    "Income Per Capita": "Income Per Capita_sc_norm",
    "Religious": "Religiosity_sc_norm",
    "Child-friendly": 'prop_population_under_18_pop_norm',
    "Working-age People": 'prop_population_18-54_pop_norm',
    "Seniors": 'prop_population_55+_pop_norm',
    "More Men": 'prop_male_population_pop_norm',
    "More Women": 'prop_female_population_pop_norm'
}

factor_colname_dict["Select All"] = list(factor_colname_dict.values())

factors = list(factor_colname_dict.keys())

st.write("Factors that matter to you (check all that apply):")
col1, col2, col3 = st.columns(3)
factor_dict = {}

for i, factor in enumerate(factors):
    factor_dict[factor] = {}
    factor_dict[factor]["colname"] = factor_colname_dict[factor]
    if i % 3 == 0:
        with col1:
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)
    elif i % 3 == 1:
        with col2:
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)

    else:
        with col3:
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)

selected_factors = [
    x for x in factor_dict.keys() if factor_dict[x]["checkbox-bool"]
]

big5_data = {}
big5_traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]

big5_data["select-bool"] = st.radio("""
Have you taken the Big 5 Personality test and know your percentile scores?
""", ["Yes", "No"], index=1)

importance_scale = {
    # scale text: scale weight
    "not important to me": 0,
    "of little importance": 1,
    "somewhat important": 2,
    "very important": 4,
    "absolutely essential": 8
}

with st.expander("Factor Importance"):
    for factor in selected_factors:
        factor_dict[factor]["importance"] = importance_scale[st.select_slider(factor, list(importance_scale.keys()))]

if big5_data["select-bool"] == "Yes":
    with st.expander("Big 5 Personality Scores"):
        for trait in big5_traits:
            big5_data[f"{trait}-score"] = st.number_input(f"Trait {trait} percentile (1-99)", 1, 99, value=50, format="%d")
            big5_data[f"{trait}-colname"] = f"{trait}_sc_norm"
            big5_data[f"{trait}-importance"] = 1
else:
    for trait in big5_traits:
        big5_data[f"{trait}-score"] = 0
        big5_data[f"{trait}-colname"] = f"{trait}_sc_norm"
        big5_data[f"{trait}-importance"] = 0



df["personalized_score"] = pd.Series(
    [
        np.array([
            big5_data[f"{trait}-score"]*big5_data[f"{trait}-importance"]*df.loc[x, big5_data[f"{trait}-colname"]]
            for trait in big5_traits
            ]).sum() +
        np.array([
            factor_dict[factor]["importance"]*df.loc[x, factor_dict[factor]["colname"]]
            for factor in selected_factors
        ]).sum()
        for x in df.index
    ]
)

df.personalized_score = df.personalized_score.rank(pct=True)*10

st.plotly_chart(county_choropleth(df, var_filter="personalized_score"))

df_sorted = df.sort_values(by="personalized_score", ascending=False)

st.subheader("Top 10 Counties for You")
table_col1, table_col2 = st.columns(2)

for top_county, personalized_score in df_sorted[["description_pop", "personalized_score"]].head(10).values:
    
    with table_col1:
        st.write(top_county)
    
    with table_col2:
        st.write(f"{round(personalized_score, 2)}/10")

for _ in range(4):
    st.write(" ")

# st.download_button("Download your recommendations", 0)

with st.expander("Sources"):
    st.write("Source1")
    st.write("Source2")