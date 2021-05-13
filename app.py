import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import geopandas as gpd
import numpy as np

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
df_merged = pd.merge(gdf, df, on="neighborhood code").set_index(
    "neighborhood code")

# categorical variables
categorical_vars = set(["most common age range immigrants",
                        "most common immigrant origin",
                        "most common age range emigrants",
                        "month most unemployment",
                        "most common car accident day"])

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
                value='number car accidents')],
            style={'font-family': 'Arial','width':'50%','display':'inline-block'}),
        ]),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id="map")])
            ],style={'width':'50%','display':'inline-block'}),
        html.Div([
            html.Div([dcc.Graph(id="hist_bar")],
                     style={'font-family': 'Arial','width':'50%','display':'inline-block'}),
            html.Div([html.P(['Most correlated features:',
                              html.Br(),
                              '- number public transit stops',
                              html.Br(),
                              '- number bus stops',
                              html.Br(),
                              '- total population',
                              html.Br(),html.Br(),
                              'Least correlated features:',
                              html.Br(),
                              '- unemployment rate',
                              html.Br(),
                              '- female life expectancy',
                              html.Br(),'- birth rate',
                              html.Br(),html.Br(),html.Br()],
                             id='my-p-element')],
                     style={'font-family':'Arial','width':'50%',
                            'display':'inline-block',
                            'height':'0.4*h_max'}),
            html.Div([
                    html.Div([dcc.Dropdown(
                            id='drop-2',
                            options=[
                                {'label':i,'value':i} for i in feature_names],
                            value='unemployment rate')],
                        style={'font-family':'Arial','width':'60%','display':'inline-block'}),
                    html.Div([dcc.RadioItems(
                            id="radio",
                            options=[{"label":"x-axis","value":"x"},
                                     {"label":"y-axis","value":"y"},],
                            value="y")],
                        style={'font-family': 'Arial','width':'40%', 'display':'inline-block'})
                    ],
                style={'width':'100%',
                       'display':'inline-block',
                       'padding-left':'10%'}),
            html.Div([dcc.Graph(id="scatter")],
                     style={'font-family': 'Arial','width':'100%','display':'inline-block'})
            ],
            style={'width':'50%','height':'200','display':'inline-block'}),
        ])
])

# map callback
@app.callback(
    Output("map", "figure"),
    Input("drop-1", "value")
)
def update_map(dropdown_val):
    df_merged["map_text"] = df_merged["neighborhood name"] + "<br>" + \
            dropdown_val + " = " + str(df_merged[dropdown_val])
    # draw map
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
                                   # hover_data=["neighborhood name"])

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
    Input("drop-1", "value")
)
def update_scatter(dropdown2_val, radio_val, dropdown1_val):
    if radio_val == "x":
        # second dropdown selects x variable, first dropdown selects y
        x, y = dropdown2_val, dropdown1_val
    elif radio_val == "y":
        # first dropdown selects x variable, second dropdown selects y
        x, y = dropdown1_val, dropdown2_val

    fig_scatter = px.scatter(df_merged,
                             x=x,
                             y=y,
                             size="total population",
                             color="district name",
                             hover_name="neighborhood name"
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
        hoverlabel=dict(font_size=12,font_family="Arial")
    )

    return fig_scatter

@app.callback(
    Output("hist_bar", "figure"),
    Input("drop-1", "value")
)
def update_hist_bar(dropdown_val):
    # barchart
    if dropdown_val in categorical_vars:
        fig_hist_bar = px.bar(df_merged,
                              x=dropdown_val,
                              color_discrete_sequence=["red"],
                              #color="neighborhood name",
                              #hover_data=df_merged.columns
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

if __name__ == '__main__':
    app.run_server(debug=False)
