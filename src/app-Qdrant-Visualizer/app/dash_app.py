from app.utils import fetch_and_process_data, get_nearest_neighbors
from dash import Dash, dcc, html, Input, Output, State
from dash.dependencies import ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

def create_dash_app():
    vectors_2d, cluster_labels, outlier_indices, payloads, vectors = fetch_and_process_data()

    df = pd.DataFrame({
        'x': [vec[0] for vec in vectors_2d],
        'y': [vec[1] for vec in vectors_2d],
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
        html.Pre(id='click-data', style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'}),
        html.Div(id='neighbors-section')
    ])

    @app.callback(
        Output('click-data', 'children'),
        Output('neighbors-section', 'children'),
        Input('scatter-plot', 'clickData')
    )
    def display_click_data(clickData):
        if clickData and clickData['points']:
            idx = clickData['points'][0]['pointIndex']
            selected_vector = vectors[idx]
            selected_payload = payloads[idx]
            selected_cluster = int(cluster_labels[idx])

            data = {
                "payload": selected_payload,
                "vector": selected_vector.tolist(),
                "cluster": selected_cluster
            }

            # Obter vizinhos mais próximos
            neighbors = get_nearest_neighbors(selected_vector, top_k=5)

            # Criar a lista de vizinhos
            neighbors_list = html.Ul([
                html.Li([
                    html.Span(f"ID: {neighbor['id']}, Score: {neighbor['score']:.4f} "),
                    html.Button('Ver detalhes', id={'type': 'neighbor-button', 'index': neighbor['id']}, n_clicks=0)
                ]) for neighbor in neighbors
            ])

            return json.dumps(data, indent=2), html.Div([
                html.H4("Vizinhos mais próximos:"),
                neighbors_list
            ])
        return "Clique em um ponto para ver os dados da ocorrência e seus vizinhos.", ""

    @app.callback(
        Output('click-data', 'children'),
        Output('neighbors-section', 'children'),
        Input({'type': 'neighbor-button', 'index': ALL}, 'n_clicks'),
        State({'type': 'neighbor-button', 'index': ALL}, 'id')
    )
    def display_neighbor_data(n_clicks_list, ids):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            button_id_dict = json.loads(button_id)
            neighbor_id = button_id_dict['index']

            # Obter dados do vizinho selecionado
            client = QdrantClient(host="qdrant", port=6333)
            point = client.retrieve(
                collection_name="ocorrencias_resumo_collection",
                ids=[neighbor_id]
            )[0]

            neighbor_vector = point.vector
            neighbor_payload = point.payload

            data = {
                "payload": neighbor_payload,
                "vector": neighbor_vector,
                "cluster": "N/A"
            }

            # Obter vizinhos do vizinho
            neighbors = get_nearest_neighbors(neighbor_vector, top_k=5)

            neighbors_list = html.Ul([
                html.Li([
                    html.Span(f"ID: {neighbor['id']}, Score: {neighbor['score']:.4f} "),
                    html.Button('Ver detalhes', id={'type': 'neighbor-button', 'index': neighbor['id']}, n_clicks=0)
                ]) for neighbor in neighbors
            ])

            return json.dumps(data, indent=2), html.Div([
                html.H4("Vizinhos mais próximos:"),
                neighbors_list
            ])

    return app.server
