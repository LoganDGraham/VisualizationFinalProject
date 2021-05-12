import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd

# relative path; ensure that the present script contains the data subdirectory
data_path = "data/barris.geojson"
gdf = gpd.read_file(data_path)

# draw map
fig = px.choropleth_mapbox(geojson=gdf.geometry,
                           locations=gdf.index,
                           opacity=0.5,
                           center={"lat": 41.3915, "lon": 2.1734},
                           mapbox_style="open-street-map",
                           zoom=10)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

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
