from app.utils import fetch_and_process_data
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_dash_app():
    vectors_2d, cluster_labels, outlier_indices, payloads = fetch_and_process_data()

    df = pd.DataFrame({
        'x': vectors_2d[:, 0],
        'y': vectors_2d[:, 1],
        'cluster': cluster_labels,
        'payload': payloads
    })

    fig = px.scatter(df, x='x', y='y', color=df['cluster'].astype(str), title="Qdrant Vector Clusters")

    fig.add_trace(go.Scatter(
        x=df.iloc[outlier_indices]['x'],
        y=df.iloc[outlier_indices]['y'],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Outliers'
    ))

    app = Dash(__name__)
    app.layout = html.Div([
        html.H1("Qdrant Visualization"),
        dcc.Graph(id='scatter-plot', figure=fig),
        html.H3("Occurrence Data:"),
        html.Pre(id='click-data', style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'})
    ])

    @app.callback(
        Output('click-data', 'children'),
        Input('scatter-plot', 'clickData')
    )
    def display_click_data(clickData):
        if clickData and clickData['points']:
            idx = clickData['points'][0]['pointIndex']
            return str(payloads[idx])
        return "Click a point to see its occurrence data."

    return app.server
