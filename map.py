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
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.cluster import KMeans

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#df = pd.read_csv("data/stats.csv")
df = pd.read_csv("data/pitching_stats2.csv")

# labels dictionary for human-readable data
mylabels = dict()
mylabels["player_age"] = "Age"
mylabels["p_game"] = "G"
mylabels["p_formatted_ip"] = "IP"
mylabels["p_total_hits"] = "H"
mylabels["p_single"] = "1B"
mylabels["p_double"] = "2B"
mylabels["p_triple"] = "3B"
mylabels["p_home_run"] = "HR"
mylabels["p_strikeout"] = "K"
mylabels["p_walk"] = "BB"
mylabels["p_k_percent"] = "%K"
mylabels["p_bb_percent"] = "%BB"
mylabels["batting_avg"] = "AVG"
mylabels["slg_percent"] = "SLG"
mylabels["on_base_percent"] = "OBP"
mylabels["on_base_plus_slg"] = "OPS"
mylabels["woba"] = "WOBA"

# quantitative variables
new_df = df.iloc[:, 3:-1]

def generate_table(dataframe, max_rows=4):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col])
            for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

# -----------------------------------------------------------------------------
# scree plot

pca = PCA()
pca.fit(new_df)

loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
# sum of squared loadings
ssl = [np.sum(np.square(loading)) for loading in loadings]

# get the 4 top attributes, sorted by their sum of squared loadings
data = {"Attribute": new_df.columns, "SSL": ssl}
ssl_df = pd.DataFrame(data).sort_values(by=["SSL"], ascending=False)

exp_var_cumul = 100*np.cumsum(pca.explained_variance_ratio_)

# Create figure with secondary y-axis
scree = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]])

scree.add_trace(go.Bar(x=[i for i in range(1, len(pca.singular_values_)+1)],
                       y=pca.singular_values_, name="Eigenvalues"),
              secondary_y=False,
)

scree.add_trace(go.Scatter(
    x=[i for i in range(1, len(pca.singular_values_)+1)], y=exp_var_cumul,
    name="Explained Variance"), secondary_y=True,
)

scree.update_layout(title="Scree Plot: drag slider below x-axis to select\
 dimensionality index")

# Set x-axis title
scree.update_xaxes(title_text="Principal Component")

# Set y-axes titles
scree.update_yaxes(title_text="Eigenvalues", secondary_y=False)
scree.update_yaxes(title_text="Cum. Explained Var. %",
                   secondary_y=True)

# -----------------------------------------------------------------------------
# biplot
features = new_df.columns
pca = PCA(n_components=2)
components = pca.fit_transform(new_df)

loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

biplot = px.scatter(components, x=0, y=1, opacity=0.5)
biplot.update_layout(title="Biplot")
biplot.update_xaxes(title_text="Component 1")
biplot.update_yaxes(title_text="Component 2")

for i, feature in enumerate(features):
    biplot.add_shape(
        type='line',
        x0=0, y0=0,
        x1=loadings[i, 0],
        y1=loadings[i, 1]
    )
    biplot.add_annotation(
        x=loadings[i, 0],
        y=loadings[i, 1],
        ax=0, ay=0,
        xanchor="center",
        yanchor="bottom",
        text=mylabels[feature],
    )

# -----------------------------------------------------------------------------
# MDS plots

# run k-means
k = 3
# k-means
kmeans = KMeans(n_clusters=k).fit(new_df)

# Data MDS
mds_data = MDS(n_components=2)
data_trans = mds_data.fit_transform(new_df)

data_MDS = px.scatter(data_trans, x=data_trans[:,0], y=data_trans[:,1],
                      color=kmeans.labels_, opacity = 0.7)
data_MDS.update_layout(
    title_text="Data MDS plot, colored by k-means cluster",
    xaxis_title_text="Dimension 1",
    yaxis_title_text="Dimension 2")

# Variables MDS
mds_vars = MDS(n_components=2, dissimilarity="precomputed")
# compute dissimilarity matrix
dissimilarity_matrix = 1 - abs(np.corrcoef(new_df, rowvar=False))

vars_trans = mds_vars.fit_transform(dissimilarity_matrix)

variables_MDS = px.scatter(vars_trans, x=vars_trans[:,0], y=vars_trans[:,1])
variables_MDS.update_layout(
    title_text="Variables MDS plot (1-|correlation| dissimilarity)",
    xaxis_title_text="Dimension 1",
    yaxis_title_text="Dimension 2")

# -----------------------------------------------------------------------------
# parallel coordinates
parallel_coordinates = px.parallel_coordinates(
    new_df.iloc[:, :], color=kmeans.labels_, labels=mylabels)

# -----------------------------------------------------------------------------
# main app
app.layout = html.Div([
    html.H1("PitcherViz 2020",
            style = {"textAlign": "center"}
           ),

    html.H5("""an interactive visual-analytics tool for MLB pitching data from
             the 2020 season""",
             style = {"textAlign": "center"}
            ),

    html.Div([
        # scree plot
        dcc.Graph(figure=scree),

        # biplot
        dcc.Graph(figure=biplot)
    ], style = {"columnCount": 2}),

    html.Div([
        dcc.Slider(
            id="dim_slider",
            min=4, max=15, value=7,
            marks={i: str(i) for i in range(4,16)})
    ], style = {"margin-left": "160px", "width": "16%"}),
    html.Br(),

    html.Div([
        # scatter plot matrix
        dcc.Graph(id="scatter_mat"),
    ]),

    html.Div([
    generate_table(ssl_df)
    ], style = {"margin-left": "100px"}),
    html.Br(),

    html.Div([
        # data MDS plot
        dcc.Graph(figure=data_MDS),

        # variables MDS plot
        dcc.Graph(figure=variables_MDS)

    ], style = {"columnCount": 2}),
    html.Br(),

    html.H5("""Parallel Coordinates plot: interact to re-order columns and
            filter data""",
             style = {"textAlign": "center"}
            ),
    html.Div([
        # parallel coordinates
        dcc.Graph(figure=parallel_coordinates)
    ])
])

@app.callback(
    Output("scatter_mat", "figure"),
    Input("dim_slider", "value")
)
def update_scatter_mat(dimensionality):
    """
    Run the kmeans algorithm, then update and return a scatter plot matrix that
    is color-coded by cluster.

    Args:
        k: number of clusters.

    Returns:
        A scatter plot matrix figure.
    """
    k = 3
    # k-means
    kmeans = KMeans(n_clusters=k).fit(new_df)

    # PCA
    pca = PCA(n_components=dimensionality)
    components = pca.fit_transform(new_df)
    var = pca.explained_variance_ratio_.sum() * 100

    labels = {str(i): f"PC {i+1}"
              for i in range(dimensionality)}

    fig = px.scatter_matrix(
        components,
        color = kmeans.labels_,
        opacity = 0.5,
        dimensions = range(4),
        labels = labels,
        title = f"Scatterplot Matrix: Total Explained Variance: {var:.2f}%")
    fig.update_traces(diagonal_visible=False)

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
