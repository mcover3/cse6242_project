import streamlit as st

import plotly.express as px
import pandas as pd, numpy as np, re, json

from urllib.request import urlopen

def county_choropleth(df, var_filter):

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # color continuous scales that might fly well:
    # inferno, oxy, mint, *spectral*, deep, *thermal*
    fig = px.choropleth(
        df, geojson=counties, locations='fips', scope="usa",
        color=var_filter, color_continuous_scale = "mint", range_color = (0, 10),
        labels={"personalized_score": "Personalized Score",
        "description_pop": "Location",
        "predicted_price": "Forecasted Median Housing Price"
        },
        hover_data=[
            df.description_pop, df.personalized_score,
            df.predicted_price
            ]
        )


    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    return fig

df = pd.read_csv("county_data_final.csv", dtype={"fips": str})

st.header("US County Explorer")
st.subheader("Tailor your next move or trip based on your preferences and personality.")

with st.expander("Help & FAQ"):
    st.subheader("Q: How do I use the US County Explorer?")
    st.write("""
    A: \n
    1) Select the factors that matter to you with the checkboxes.\n
    2) If you know your Big 5 Personality percentile scores, select "Yes" \
    and you will be prompted to enter them.\n
    3) If you have a budget and would like it to be considered to filter out \
    more expensive counties, select "Mortgage Budget" or "Rent Budget" and \
    you will be prompted to enter your budget in $/month.\n
    4) If a lifestyle category feels suitable, select one. Note that counties \
    under all other lifestyle categories will be filtered out.\n
    5) Modify the factor importance slider(s) to weigh certain factors more \
    heavily than others. This greatly impacts your 'personalized score'.\n
    6) Use the 'personalized score' filter to only be shown counties scored \
    greater than the value entered.\n
    7) Explore the choropleth plot. County name, state, personalized score, \
    and forecasted median housing price are displayed. Please note that the \
    forecasted median housing price is only available for half of the counties.\n
    8) Note the top 10 recommended counties. Download your results as a .csv, \
    if desired.
    """)
    st.subheader("Q: What do the lifestyle categories mean (Star Gazing, American Dream, etc.)?")
    st.write("""
    A:\n
    **_Star Gazing_**: $\quad$ Extreme low population, extreme rural features, high employment rate, \
    high religion, low belief in science, high conscientiousness\n
    **_Country Roads_**: $\quad$ Low population, high rural features, high religion, \
    low belief in science, low employment rate, high conscientiousness\n
    **_American Dream_**: $\quad$ Somewhat high urban and population features, somewhat high gender equality, \
    somewhat high stress tolerance, somewhat high entrepreneurship, high graduation rates, high agreeableness\n
    **_Big City Life_**: $\quad$ High urban and population features, high gender equality, high stress tolerance, \
    high entrepreneurship\n
    **_Best of Both Worlds_**: $\quad$ All social stats near the median, mix of urban and rural features, high conflict awareness, comparable income to American Dream 
    """)
    st.subheader("Q: How did you determine the lifestyle categories?")
    st.write("""
    A: These categories are the result of a clustering analysis performed on \
    counties across demographic, economic, and personality factors.
    """)
    st.subheader("Q: What is the 'personalized score'?")
    st.write("""
    A: The personalized score is an aggregated statistic that summarizes your \
    selected lifestyle preferences into a single figure per county. The counties \
    are then ranked by that score and subsequently scaled to 0-10.
    """)
    st.subheader("Q: Can I provide feedback?")
    st.write("A: Yes! You can access our Google Form [here](https://docs.google.com/forms/d/e/1FAIpQLSfFyCmytOpEJ9ihBz31MHPUpxxKjUCrIL85TfxcovO5sHIecA/viewform).")

factor_colname_dict = {
    "Educated": "educated_norm",
    "Religious": "Religiosity_sc_norm",
    "Child-friendly": 'prop_population_under_18_pop_norm',

    "Low Unemployment": "employed_norm",
    "Right-Wing": "right_wing_norm",
    "Professionals-friendly": 'prop_population_18-54_pop_norm',
    
    "Entrepreneurship": "Entrepreneurship_sc_norm",
    "Left-Wing": "left_wing_norm",
    "Senior-friendly": 'prop_population_55+_pop_norm',
    
    "Income Mobility": "Income Mobility_sc_norm",
    "Gender Equality": "Gender Equality_sc_norm",
    "Single Men": 'prop_male_population_pop_norm',

    "Income Per Capita": "Income Per Capita_sc_norm",
    "Belief in Science": 'Belief In Science_sc_norm',
    "Single Women": 'prop_female_population_pop_norm'
}

factors = list(factor_colname_dict.keys())

# fillna with mean (z-score = 0)
df[list(factor_colname_dict.values())] = df[list(factor_colname_dict.values())].fillna(0)

st.write("Factors that matter to you (check all that apply):")
col1, col2, col3 = st.columns(3)
factor_dict = {}

for i, factor in enumerate(factors):
    factor_dict[factor] = {}
    factor_dict[factor]["colname"] = factor_colname_dict[factor]
    if i % 3 == 0:
        with col1:
            if i == 0:
                st.write("__Economic__")
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)
    elif i % 3 == 1:
        with col2:
            if i == 1:
                st.write("__Belief-Based__")
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)

    else:
        with col3:
            if i == 2:
                st.write("__Demographic__")
            factor_dict[factor]["checkbox-bool"] = st.checkbox(factor)

selected_factors = [
    x for x in factor_dict.keys() if factor_dict[x]["checkbox-bool"]
]

big5_data = {}
big5_traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]

big5_data["select-bool"] = st.radio("""
Have you taken the Big 5 Personality test and know your percentile scores?
""", ["Yes", "No"], index=1)
big5_data["importance"] = 0

if big5_data["select-bool"] == "Yes":
    with st.expander("Big 5 Personality Scores"):
        for trait in big5_traits:
            big5_data[f"{trait}-score"] = st.number_input(
                f"Trait {trait} percentile (1-99)", 1, 99, 
                value=50, format="%d"
                )
            big5_data[f"{trait}-colname"] = f"{trait}_sc_norm"
            # big5_data[f"{trait}-importance"] = 1
else:
    for trait in big5_traits:
        big5_data[f"{trait}-score"] = 0
        big5_data[f"{trait}-colname"] = f"{trait}_sc_norm"
        # big5_data[f"{trait}-importance"] = 0

budget_data = {}
budget_data["select-bool"] = st.radio("""
Do you have a monthly budget for buying or renting?
""", ["Mortgage Budget", "Rent Budget", "No Thanks"], index=2)

budget_data["budget-value"] = 100000
budget_data["colname"] = "median_rent"

if budget_data["select-bool"] != "No Thanks":
    with st.expander("Budget"):
        budget_type = str.lower(
            budget_data["select-bool"][
                :re.search("Budget", budget_data["select-bool"]).start()-1
                ]
            )
        budget_default_val = {
            "mortgage": 2000,
            "rent": 700
        }
        budget_data["budget-value"] = st.number_input(
            f"Monthly {budget_type} budget ($/month)", 400, 10000, 
            value=budget_default_val[budget_type], format="%d"
        )
        budget_data["colname"] = f"median_{budget_type}"

cluster_data = {}
cluster_data["select-bool"] = st.radio("""
Which lifestyle best suits you?
""", ["Star Gazing", "Country Roads", "American Dream", "Big City Life", "Best of Both Worlds", "No Preference"],
index = 5
)

importance_scale = {
    # scale text: scale weight
    "not important to me": 0,
    "of little importance": 1,
    "somewhat important": 2.5,
    "very important": 5,
    "absolutely essential": 10
}

big5_importance_scale = {
    "not important to me": 0,
    "of little importance": .001,
    "somewhat important": .003,
    "very important": .01,
    "absolutely essential": .075
}

st.write("**Be sure to modify how important each factor is to you:**")
with st.expander("Factor Importance"):
    for factor in selected_factors:
        factor_dict[factor]["importance"] = importance_scale[st.select_slider(factor, list(importance_scale.keys()))]
    if big5_data["select-bool"] == "Yes":
        big5_data["importance"] = big5_importance_scale[st.select_slider("Big 5 Personality Profile", list(big5_importance_scale.keys()))]

df["personalized_score"] = pd.Series(
    [
        np.array([
            (big5_data[f"{trait}-score"]*big5_data["importance"])*df.loc[x, big5_data[f"{trait}-colname"]]
            for trait in big5_traits
            ]).sum() +
        np.array([
            factor_dict[factor]["importance"]*df.loc[x, factor_dict[factor]["colname"]]
            for factor in selected_factors
        ]).sum()
        for x in df.index
    ]
)

# remove counties out of budget
df = df.drop(
    df[df[budget_data["colname"]] > budget_data["budget-value"]].index
)

# remove counties not in cluster
if cluster_data["select-bool"] != "No Preference":
    df = df.drop(
        df[df.cluster_label != cluster_data["select-bool"]].index
    )

df.personalized_score = (df.personalized_score.rank(pct=True)*10).round(2)

df.personalized_score = df.personalized_score.fillna(0)

county_show_cutoff = st.number_input(
    "Show me counties with a personalized score greater than:",
    0.0, 9.9, value=2.5
)
# remove counties with a personalized score < 50%
df = df.drop(
    df[df.personalized_score <= county_show_cutoff].index
)

if df.shape[0] != 0:
    st.plotly_chart(county_choropleth(df, var_filter="personalized_score"))
else:
    st.write("**No matches. Please modify preferences.**")

df_sorted = df.sort_values(by="personalized_score", ascending=False)

st.subheader("Top 10 Counties for You")

table_col1, table_col2 = st.columns(2)

for top_county, personalized_score in df_sorted[["description_pop", "personalized_score"]].head(10).values:
    
    with table_col1:
        st.write(top_county)
    
    with table_col2:
        st.write(f"{round(personalized_score, 2)}/10")

df_download = df_sorted[["description_pop", "personalized_score"]].head(100)

@st.cache
def convert_df(df):
     return df.to_csv().encode('utf-8')

if df.shape[0] != 0:
    csv = convert_df(df_download)

    num_downloadable_counties = min([100, df.shape[0]])

    st.download_button(
        label=f"Download top {num_downloadable_counties} counties for you as .csv",
        data=csv,
        file_name='personalized_counties.csv',
        mime='text/csv',
    )

st.write("Have feedback or a suggestion? You can access our Google Form [here](https://docs.google.com/forms/d/e/1FAIpQLSfFyCmytOpEJ9ihBz31MHPUpxxKjUCrIL85TfxcovO5sHIecA/viewform)!")

for _ in range(4):
    st.write("")

with st.expander("Data Sources"):
    st.write("""Market hotness Realtor data, for Forecasted Median House Prices: [link to data](https://www.realtor.com/research/data/)""")
    st.write("StatsAmerica demographic, social context data: [link to data](https://www.statsamerica.org/downloads/default.aspx)")
    st.write("USDA education, unemployment, household income data: [link to data](https://www.ers.usda.gov/data-products/county-level-data-sets/download-data/)")