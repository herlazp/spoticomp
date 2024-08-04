import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from api.spotify_api import search_track, compare_two_tracks

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='track-name-1', type='text', placeholder='Enter first track name'),
    dcc.Input(id='artist-name-1', type='text', placeholder='Enter first artist name (optional)'),
    dcc.Input(id='track-name-2', type='text', placeholder='Enter second track name'),
    dcc.Input(id='artist-name-2', type='text', placeholder='Enter second artist name (optional)'),
    html.Button(id='search-button', children='Search'),
    dcc.Dropdown(id='dropdown-track-1', placeholder='Select first track'),
    dcc.Dropdown(id='dropdown-track-2', placeholder='Select second track'),
    html.Button(id='compare-button', children='Compare'),
    dcc.Graph(id='radar-chart')
])

@app.callback(
    [Output('dropdown-track-1', 'options'),
     Output('dropdown-track-2', 'options')],
    [Input('search-button', 'n_clicks')],
    [State('track-name-1', 'value'),
     State('artist-name-1', 'value'),
     State('track-name-2', 'value'),
     State('artist-name-2', 'value')]
)
def update_dropdowns(n_clicks, track_name_1, artist_name_1, track_name_2, artist_name_2):
    if n_clicks is None or not track_name_1 or not track_name_2:
        return [], []

    results_1 = search_track(track_name_1, artist_name_1, limit=50)
    results_2 = search_track(track_name_2, artist_name_2, limit=50)

    options_1 = [{'label': f"{track['name']} by {track['artists'][0]['name']} (Popularity: {track['popularity']})", 'value': track['id']} for track in results_1]
    options_2 = [{'label': f"{track['name']} by {track['artists'][0]['name']} (Popularity: {track['popularity']})", 'value': track['id']} for track in results_2]

    return options_1, options_2

@app.callback(
    Output('radar-chart', 'figure'),
    [Input('compare-button', 'n_clicks')],
    [State('dropdown-track-1', 'value'),
     State('dropdown-track-2', 'value')]
)
def update_chart(n_clicks, track_id_1, track_id_2):
    if n_clicks is None or not track_id_1 or not track_id_2:
        return go.Figure()

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

    # Get track and artist details for labels
    track_label_1 = f"{comparison['id']['track_1']['artists'][0]['name']} - {comparison['id']['track_1']['name']}"
    track_label_2 = f"{comparison['id']['track_2']['artists'][0]['name']} - {comparison['id']['track_2']['name']}"

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
