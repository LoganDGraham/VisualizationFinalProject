import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
# for debugging purposes
import json

external_stylesheets = ['stylesheet.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

h_max = 550
margin_val = 30

df = pd.read_csv("data/data.csv")
feature_names = df.drop(['neighborhood code','neighborhood name',
                         'district name'], axis=1).head()

# relative path; ensure that the present script contains the data subdirectory
data_path = "data/barris.geojson"
gdf = gpd.read_file(data_path)
gdf.rename(columns={"BARRI": "neighborhood code"}, inplace=True)
gdf["neighborhood code"] = gdf["neighborhood code"].apply(int)
gdf["nbd code"] = gdf["neighborhood code"]
df_merged = pd.merge(gdf, df, on="neighborhood code").set_index(
    "neighborhood code")

# categorical variables
categorical_vars = set(["most common age range immigrants",
                        "most common immigrant origin",
                        "most common age range emigrants",
                        "month most unemployment",
                        "most common car accident day",
                        "leading cause of car accidents"])

# main app
app.layout = html.Div([
    html.Div([
        html.H1("Exploring the Features and Neighborhoods of Barcelona",
                style={'font-family': 'Arial',"textAlign": "center"})
        ]),
    html.Div([
        html.Div([dcc.Dropdown(
                id='drop-1',
                options=[{'label': i, 'value': i} for i in feature_names],
                value='total population')],
            style={'font-family': 'Arial','width':'50%',
                   'display':'inline-block'}),
        ]),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id="map", clear_on_unhover=True)])
            ],style={'width':'50%','display':'inline-block'}),
        html.Div([
            html.Div([dcc.Graph(id="hist_bar")],
                     style={'font-family': 'Arial','width':'50%',
                            'display':'inline-block'}),
            html.Div([html.P(['Most correlated features:'],
                             id='my-p-element1'),
                    html.Table([
                        html.Tr([html.Td(['x']), html.Td(id='square')]),
                        html.Tr([html.Td(['x']), html.Td(id='cube')])]),
                    html.P(['Least correlated features:'],id='my-p-element2'),
                    html.Table([
                        html.Tr([html.Td(['x']), html.Td(id='square1')]),
                        html.Tr([html.Td(['x']), html.Td(id='cube1')])]),
                    html.P([html.Br(),html.Br()])],
                     style={'font-family':'Arial','width':'50%',
                            'display':'inline-block',
                            'height':'0.4*h_max'}),
            html.Div([
                    html.Div([dcc.Dropdown(
                            id='drop-2',
                            options=[
                                {'label':i,'value':i} for i in feature_names],
                            value='unemployment rate')],
                        style={'font-family':'Arial','width':'60%',
                               'display':'inline-block'}),
                    html.Div([dcc.RadioItems(
                            id="radio",
                            options=[{"label":"x-axis","value":"x"},
                                     {"label":"y-axis","value":"y"},],
                            value="y")],
                        style={'font-family': 'Arial','width':'40%',
                               'display':'inline-block'})
                    ],
                style={'width':'100%',
                       'display':'inline-block',
                       'padding-left':'10%'}),
            html.Div([dcc.Graph(id="scatter", clear_on_unhover=True)],
                     style={'font-family': 'Arial','width':'100%',
                            'display':'inline-block'})
            ],
            style={'width':'50%','height':'200','display':'inline-block'}),
        ]),
        # for debugging purposes
        #html.Div(className="row", children=[
        #    html.Div([
        #        dcc.Markdown("""
        #            **Click Data (for debugging purposes)**

        #            Click a dot in the scatter plot.
        #        """),
        #        html.Pre(id="click_data")
        #    ], className="three columns")
        #])
])

# map callback
@app.callback(
    Output("map", "figure"),
    Input("drop-1", "value"),
    Input("scatter", "hoverData")
)
def update_map(dropdown_val, scatter_hover):
    if scatter_hover:
        df_hovered = df_merged.loc[df_merged["nbd code"] == scatter_hover["points"][0]["customdata"][0]]
        fig_map = px.choropleth_mapbox(df_hovered,
                                       geojson=df_hovered.geometry,
                                       locations=df_hovered.index,
                                       color=dropdown_val,
                                       opacity=0.65,
                                       center={"lat": 41.3915, "lon": 2.1734},
                                       mapbox_style="carto-positron",
                                       zoom=10.5,
                                       labels={"color":dropdown_val},
                                       hover_name="neighborhood name")
    else:
        fig_map = px.choropleth_mapbox(df_merged,
                                       geojson=df_merged.geometry,
                                       locations=df_merged.index,
                                       color=dropdown_val,
                                       opacity=0.65,
                                       center={"lat": 41.3915, "lon": 2.1734},
                                       mapbox_style="carto-positron",
                                       zoom=10.5,
                                       labels={"color":dropdown_val},
                                       hover_name="neighborhood name")

    fig_map.update_traces(hoverinfo="z",selector=dict(type='choropleth'))

    # layout
    fig_map.update_layout(
        height=h_max,
        margin_l=margin_val,
        margin_r=margin_val,
        margin_t=margin_val,
        margin_b=margin_val,
        showlegend=False,
        coloraxis_showscale=False,
        hoverlabel=dict(bgcolor="white",font_size=12,font_family="Arial")
    )

    return fig_map

# scatterplot callback
@app.callback(
    Output("scatter", "figure"),
    Input("drop-2", "value"),
    Input("radio", "value"),
    Input("drop-1", "value"),
    Input("map", "hoverData")
)
def update_scatter(dropdown2_val, radio_val, dropdown1_val, map_hover):
    if radio_val == "x":
        # second dropdown selects x variable, first dropdown selects y
        x, y = dropdown2_val, dropdown1_val
    elif radio_val == "y":
        # first dropdown selects x variable, second dropdown selects y
        x, y = dropdown1_val, dropdown2_val

    fig_scatter = px.scatter(df_merged,
                             x=x,
                             y=y,
                             custom_data=["nbd code"],
                             size="total population",
                             color="district name",
                             hover_name="neighborhood name"
                            )

    if map_hover:
        # highlight based on map_hover
        nbd_code = map_hover["points"][0]["location"]

        fig_scatter.add_trace(
            go.Scatter(mode="markers",
                       marker = dict(
                           symbol="x",
                           color="black",
                           size=12),
                       x=df_merged.loc[df_merged["nbd code"] == nbd_code][x],
                       y=df_merged.loc[df_merged["nbd code"] == nbd_code][y])
        )

    # layout
    fig_scatter.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        showlegend=False,
        height=0.5*h_max,
        margin_l=margin_val,
        margin_r=margin_val,
        margin_t=margin_val,
        margin_b=margin_val,
        hoverlabel=dict(font_size=12,font_family="Arial"),
        clickmode="event+select"
    )

    return fig_scatter

@app.callback(
    Output("hist_bar", "figure"),
    Input("drop-1", "value"),
    Input("map", "hoverData")
)
def update_hist_bar(dropdown_val, map_hover):
    # barchart
    if dropdown_val in categorical_vars:
        fig_hist_bar = px.bar(df_merged,
                              x=dropdown_val,
                              color_discrete_sequence=["red"]
                             )
    # histogram
    else:
        fig_hist_bar = px.histogram(df_merged,
                                    x=dropdown_val,
                                    color_discrete_sequence=["red"],
                                    opacity=0.5)
        fig_hist_bar.update_layout(
            xaxis_title=dropdown_val,
            yaxis_title='counts',
            showlegend=False,
            height=0.4*h_max,
            margin_l=margin_val,
            margin_r=margin_val,
            margin_t=margin_val,
            margin_b=margin_val
        )

    return fig_hist_bar

# text callback

# for debugging purposes
#@app.callback(
#    Output("hover_data", "children"),
#    Input("map", "hoverData")
#)
#def display_hover_data(map_hover):
#    return json.dumps(map_hover, indent=2)
#@app.callback(
#    Output("click_data", "children"),
#    Input("scatter", "clickData")
#)
#def display_click_data(scatter_click):
#    return json.dumps(scatter_click, indent=2)


if __name__ == '__main__':
    app.run_server(debug=False)
