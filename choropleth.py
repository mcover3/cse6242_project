import plotly.express as px
import pandas as pd

from urllib.request import urlopen
import json

def county_choropleth(df, var_filter):

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # color continuous scales that might fly well:
    # inferno, oxy, mint, *spectral*, deep, *thermal*

    fig = px.choropleth(
        df, geojson=counties, locations='fips', scope="usa",
        color=var_filter, color_continuous_scale = "mint", range_color = (0, 10),
        labels={"personalized_score": "Personalized Score"},
        )


    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    return fig