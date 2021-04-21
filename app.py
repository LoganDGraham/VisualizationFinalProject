import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import MDS

external_stylesheets = ['stylesheet.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

h_max = 550
margin_val = 30

df = pd.read_csv('data.csv')
feature_names = df.drop(['neighborhood code','neighborhood name','district name'], axis=1).head()

fig_map=px.scatter(df['total population'],df['average monthly rent'],hover_name=df['neighborhood name'])
fig_map.update_layout(
    xaxis_title='component 1',
    yaxis_title='component 2',
    height=h_max,
    margin_l=margin_val,
    margin_r=margin_val,
    margin_t=margin_val,
    margin_b=margin_val
)

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

fig_corr=px.scatter(df['total population'],df['average monthly rent'],hover_name=df['neighborhood name'])
fig_corr.update_layout(
    xaxis_title='component 1',
    yaxis_title='component 2',
    height=0.4*h_max,
    margin_l=margin_val,
    margin_r=margin_val,
    margin_t=margin_val,
    margin_b=margin_val
)

fig_scatter=px.scatter(x=df['number car accidents'],y=df['average monthly rent'],size=df['total population'],color=df['district name'],hover_name=df['neighborhood name'])
fig_scatter.update_layout(
    xaxis_title='number car accidents',
    yaxis_title='average monthly rent',
    showlegend=False,
    height=0.5*h_max,
    margin_l=margin_val,
    margin_r=margin_val,
    margin_t=margin_val,
    margin_b=margin_val
)

app.layout = html.Div([
    html.Div([
        html.H2("Exploring the Features and Neighborhoods of Barcelona",style={"textAlign": "center"})
        ]),
    html.Div([
        html.Div([dcc.Dropdown(
                id='drop-1',
                options=[{'label': i, 'value': i} for i in feature_names],
                value='number car accidents')],style={'width':'60%','display':'inline-block'}),
        html.Div([dcc.RadioItems(
                id='btn-1',
                options=[{'label':'feature exploration','value':'feat'},{'label':'neighborhood exploration','value':'nbhd'},],
                value='feat')],style={'width':'40%', 'display':'inline-block'})
        ]),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(figure=fig_map)])
            ],style={'width':'50%','display':'inline-block'}),
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)],style={'width':'50%','display':'inline-block'}),
            html.Div([dcc.Graph(figure=fig_corr)],style={'width':'50%','display':'inline-block'}),
            html.Div([
                html.Div([dcc.Graph(figure=fig_scatter)],style={'width':'100%','display':'inline-block'}),
                    html.Div([dcc.Dropdown(
                            id='drop-2',
                            options=[{'label':i,'value':i} for i in feature_names],
                            value='average monthly rent')],style={'width':'60%','display':'inline-block'}),
                    html.Div([dcc.RadioItems(
                            id='btn-2',
                            options=[{'label':'x axis','value':'xaxis'},{'label':'y axis','value':'yaxis'},],
                            value='yaxis')],style={'width':'40%', 'display':'inline-block'})
                    ],style={'width':'100%','display':'inline-block'})],style={'width':'50%','height':'200','display':'inline-block'})
        ])
])

if __name__ == '__main__':
    app.run_server(debug=False)
