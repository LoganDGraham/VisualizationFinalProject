# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from urllib.request import urlopen
import json

json_data_url = "https://raw.githubusercontent.com/plotly/datasets/master/\
geojson-counties-fips.json"

with urlopen(json_data_url) as response:
    counties = json.load(response)

csv_data_url = "https://raw.githubusercontent.com/plotly/datasets/master/\
fips-unemp-16.csv"
df = pd.read_csv(csv_data_url, dtype={"fips": str})

fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
                           color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'unemp':'unemployment rate'}
                          )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# main app
app.layout = html.Div([
    html.H1("Map Test",
            style = {"textAlign": "center"}
           ),

    html.Div([
        # draw map
        dcc.Graph(figure=fig),
    ]),
])

if __name__ == "__main__":
    app.run_server(debug=True)
