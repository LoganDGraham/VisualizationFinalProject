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
                        "leading cause of car accidents",
                        "nbd code"])

quant_vars = set(["average tax revenue by person",
                  "average monthly rent",
                  "total population",
                  "average number residents per home",
                  "female life expectancy",
                  "male life expectancy",
                  "birth rate",
                  "mortality rate",
                  "number elder care homes",
                  "number hospitals",
                  "immigration rate",
                  "emigration rate",
                  "unemployment rate",
                  "number bus stops",
                  "number public transport stops",
                  "number car accidents",
                  "number shopping galleries",
                  "number state administration facilities",
                  "number cemeteries",
                  "number police stations",
                  "number street trees",
                  "number hotels",
                  "number music and dance venues",
                  "number libraries and museums",
                  "number places of worship"])

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
                        html.Tr([html.Td(id="pos_cor1")]),
                        html.Tr([html.Td(id="pos_cor2")])]),
                    html.P(['Least correlated features:'],id='my-p-element2'),
                    html.Table([
                        html.Tr([html.Td(id="neg_cor1")]),
                        html.Tr([html.Td(id="neg_cor2")])]),
                    html.P([html.Br()])],
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
        ])
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

# compute correlations offline and store
correlations = dict()
correlation_vars = dict()
pos_corr = dict()
pos_corr_vars = dict()
neg_corr = dict()
neg_corr_vars = dict()
for var1 in df_merged.columns:
    if var1 in quant_vars:
        correlations[var1] = []
        correlation_vars[var1] = []
        pos1, pos2, neg1, neg2 = None, None, None, None
        pos1_val, pos2_val, neg1_val, neg2_val = -np.inf, -np.inf, np.inf, np.inf
        for var2 in df_merged.columns:
            if var2 in quant_vars:
                if var1 != var2:
                    corr_val = round(df_merged[var1].corr(df_merged[var2]), 2)
                    correlations[var1].append(corr_val)
                    correlation_vars[var1].append(var2)
                    if corr_val < neg1_val:
                        neg2, neg2_val = neg1, neg1_val
                        neg1, neg1_val = var2, corr_val
                    elif corr_val < neg2_val:
                        neg2, neg2_val = var2, corr_val

                    if corr_val > pos1_val:
                        pos2, pos2_val = pos1, pos1_val
                        pos1, pos1_val = var2, corr_val
                    elif corr_val > pos2_val:
                        pos2, pos2_val = var2, corr_val

                    neg_corr[var1] = [neg1_val, neg2_val]
                    neg_corr_vars[var1] = [neg1, neg2]
                    pos_corr[var1] = [pos1_val, pos2_val]
                    pos_corr_vars[var1] = [pos1, pos2]

# text callback
@app.callback(
    Output("pos_cor1", "children"),
    Output("pos_cor2", "children"),
    Output("neg_cor1", "children"),
    Output("neg_cor2", "children"),
    Input("drop-1", "value")
)
def update_text(dropdown_val):
    if dropdown_val not in quant_vars:
        pos1 = "select a quantitative variable to see correlation"
        pos2 = ""
        neg1 = "select a quantitative variable to see correlation"
        neg2 = ""
    else:
        pos1 = pos_corr_vars[dropdown_val][0]+": "+str(pos_corr[dropdown_val][0])
        pos2 = pos_corr_vars[dropdown_val][1]+": "+str(pos_corr[dropdown_val][1])
        neg1 = neg_corr_vars[dropdown_val][0]+": "+str(neg_corr[dropdown_val][0])
        neg2 = neg_corr_vars[dropdown_val][1]+": "+str(neg_corr[dropdown_val][1])

    return pos1, pos2, neg1, neg2

if __name__ == '__main__':
    app.run_server(debug=True)
