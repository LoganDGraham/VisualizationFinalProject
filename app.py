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

#fig_scatter=px.scatter(df['total population'], df['average monthly rent'],
#                       hover_name=df['neighborhood name'])
#fig_scatter.update_layout(
#    xaxis_title='component 1',
#    yaxis_title='component 2',
#    height=h_max,
#    margin_l=margin_val,
#    margin_r=margin_val,
#    margin_t=margin_val,
#    margin_b=margin_val
#)

# relative path; ensure that the present script contains the data subdirectory
data_path = "data/barris.geojson"
gdf = gpd.read_file(data_path)
gdf.rename(columns={"NOM": "neighborhood name", "BARRI": "neighborhood code"},
           inplace=True)
gdf["neighborhood code"] = gdf["neighborhood code"].apply(int)
df_merged = pd.merge(gdf, df, on="neighborhood code").set_index(
    "neighborhood code")

# histogram
fig_hist=px.histogram(df['number car accidents'])
fig_hist.update_layout(
    xaxis_title='number car accidents',
    yaxis_title='counts',
    showlegend=False,
    height=0.4*h_max,
    margin_l=margin_val,
    margin_r=margin_val,
    margin_t=margin_val,
    margin_b=margin_val
)

fig_corr=px.scatter(df['total population'],
                    df['average monthly rent'],
                    hover_name=df['neighborhood name'])
fig_corr.update_layout(
    xaxis_title='component 1',
    yaxis_title='component 2',
    height=0.4*h_max,
    margin_l=margin_val,
    margin_r=margin_val,
    margin_t=margin_val,
    margin_b=margin_val
)

app.layout = html.Div([
    html.Div([
        html.H2("Exploring the Features and Neighborhoods of Barcelona",
                style={"textAlign": "center"})
        ]),
    html.Div([
        html.Div([dcc.Dropdown(
                id='drop-1',
                options=[{'label': i, 'value': i} for i in feature_names],
                value='number car accidents')],
            style={'width':'60%','display':'inline-block'}),
        ]),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id="map")])
            ],style={'width':'50%','display':'inline-block'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)],
                     style={'width':'50%','display':'inline-block'}),
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
                     style={'width':'50%',
                            'display':'inline-block',
                            'height':'0.4*h_max'}),
            html.Div([
                    html.Div([dcc.Dropdown(
                            id='drop-2',
                            options=[
                                {'label':i,'value':i} for i in feature_names],
                            value='unemployment rate')],
                        style={'width':'60%','display':'inline-block'}),
                    html.Div([dcc.RadioItems(
                            id="radio",
                            options=[{"label":"x-axis","value":"x"},
                                     {"label":"y-axis","value":"y"},],
                            value="y")],
                        style={'width':'40%', 'display':'inline-block'})
                    ],
                style={'width':'100%',
                       'display':'inline-block',
                       'padding-left':'10%'}),
            html.Div([dcc.Graph(id="scatter")],
                     style={'width':'100%','display':'inline-block'})
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
    # draw map
    fig_map = px.choropleth_mapbox(geojson=df_merged.geometry,
                                   locations=df_merged.index,
                                   color=df_merged[dropdown_val],
                                   opacity=0.65,
                                   center={"lat": 41.3915, "lon": 2.1734},
                                   mapbox_style="open-street-map",
                                   zoom=10.5,
                                   labels={"color": dropdown_val})

    # layout
    fig_map.update_layout(
        height=h_max,
        margin_l=margin_val,
        margin_r=margin_val,
        margin_t=margin_val,
        margin_b=margin_val
    )

    return fig_map

# scatterplot callback
@app.callback(
    Output("scatter", "figure"),
    Input("drop-2", "value"),
    State("radio", "value"),
    State("drop-1", "value")
)
def update_scatter(dropdown2_val, radio_val, dropdown1_val):
    if radio_val == "x":
        # second dropdown selects x variable, first dropdown selects y
        x, y = dropdown2_val, dropdown1_val
    elif radio_val == "y":
        # first dropdown selects x variable, second dropdown selects y
        x, y = dropdown1_val, dropdown2_val

    fig_scatter = px.scatter(df,
                             x=x,
                             y=y,
                             size=df['total population'],
                             color=df['district name'],
                             hover_name=df['neighborhood name'])

    # layout
    fig_scatter.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        showlegend=False,
        height=0.5*h_max,
        margin_l=margin_val,
        margin_r=margin_val,
        margin_t=margin_val,
        margin_b=margin_val
    )

    return fig_scatter

if __name__ == '__main__':
    app.run_server(debug=True)
