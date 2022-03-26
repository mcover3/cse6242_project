import plotly.express as px
import pandas as pd

from urllib.request import urlopen
import json

def county_choropleth(df):

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # color continuous scales that might fly well:
    # inferno, oxy, mint, *spectral*, deep, *thermal*

    fig = px.choropleth(
        df, geojson=counties, locations='fips', scope="usa",
        color="unemp", color_continuous_scale = "thermal", range_color = (0, 12)
        )
        

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    return fig