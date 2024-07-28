import dash
from dash import dcc, html
import plotly.graph_objs as go
from api.spotify_api import search_track, compare_two_tracks

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='track-name-1', type='text', placeholder='Enter first track name'),
    dcc.Input(id='track-name-2', type='text', placeholder='Enter second track name'),
    html.Button(id='submit-button', children='Compare'),
    dcc.Graph(id='radar-chart')
])

@app.callback(
    dash.dependencies.Output('radar-chart', 'figure'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('track-name-1', 'value'),
     dash.dependencies.State('track-name-2', 'value')]
)
def update_chart(n_clicks, track_name_1, track_name_2):
    if n_clicks is None or not track_name_1 or not track_name_2:
        return go.Figure()

    track_1 = search_track(track_name_1)
    track_2 = search_track(track_name_2)

    if not track_1 or not track_2:
        return go.Figure()

    track_id_1 = track_1['id']
    track_id_2 = track_2['id']
    comparison = compare_two_tracks(track_id_1, track_id_2)

    # Remove 'id' and any feature not in the range [0, 1]
    filtered_comparison = {
        feature: values
        for feature, values in comparison.items()
        if feature != 'id' and 
        feature != 'mode' and
        feature != 'speechiness' and
        feature != 'instrumentalness' and
        0 <= values['track_1'] <= 1 and 
        0 <= values['track_2'] <= 1
    }

    # Radar chart data preparation
    features = list(filtered_comparison.keys())
    values_1 = [filtered_comparison[feature]['track_1'] for feature in features]
    values_2 = [filtered_comparison[feature]['track_2'] for feature in features]

    # Normalize values for a better comparison (optional)
    #values_1 = [val / max(values_1) if max(values_1) != 0 else 0 for val in values_1]
    #values_2 = [val / max(values_2) if max(values_2) != 0 else 0 for val in values_2]

    # Get artist names for labels
    artist_name_1 = track_1['artists'][0]['name']
    artist_name_2 = track_2['artists'][0]['name']
    track_label_1 = f"{artist_name_1} - {track_name_1}"
    track_label_2 = f"{artist_name_2} - {track_name_2}"

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_1,
        theta=features,
        fill='toself',
        name=track_label_1,
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_2,
        theta=features,
        fill='toself',
        name=track_label_2,
        line=dict(color='red')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
