import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from api.spotify_api import search_track, get_track_features, compare_two_tracks, get_track_details

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Step 1: Search and select a single track
    dcc.Input(id='track-name', type='text', placeholder='Enter track name'),
    dcc.Input(id='artist-name', type='text', placeholder='Enter artist name (optional)'),
    html.Button(id='search-button', children='Search'),
    dcc.Dropdown(id='dropdown-track', placeholder='Select track'),
    
    # Display radar chart for the selected track
    dcc.Graph(id='single-track-radar-chart'),
    
    # Button to trigger comparison with another track
    html.Button(id='compare-button', children='Compare with another track', style={'display': 'none'}),
    
    # Step 2: Search and select another track for comparison (initially hidden)
    html.Div(id='compare-div', children=[
        dcc.Input(id='track-name-2', type='text', placeholder='Enter second track name'),
        dcc.Input(id='artist-name-2', type='text', placeholder='Enter second artist name (optional)'),
        html.Button(id='search-button-2', children='Search Second Track'),
        dcc.Dropdown(id='dropdown-track-2', placeholder='Select second track')
    ], style={'display': 'none'}),
    
    # Display radar chart comparing both tracks
    dcc.Graph(id='comparison-radar-chart', style={'display': 'block'})
])

# Update dropdown with search results for the first track
@app.callback(
    Output('dropdown-track', 'options'),
    [Input('search-button', 'n_clicks')],
    [State('track-name', 'value'),
     State('artist-name', 'value')]
)
def update_dropdown(n_clicks, track_name, artist_name):
    if n_clicks is None or not track_name:
        return []
    
    results = search_track(track_name, artist_name, limit=10)
    options = [{'label': f"{track['name']} by {track['artists'][0]['name']} (Popularity: {track['popularity']})", 'value': track['id']} for track in results]
    
    return options

# Display the radar chart for the selected track and show compare button
@app.callback(
    [Output('single-track-radar-chart', 'figure'),
     Output('compare-button', 'style')],
    [Input('dropdown-track', 'value')]
)
def display_single_track_features(track_id):
    if not track_id:
        return go.Figure(), {'display': 'none'}
    
    features = get_track_features(track_id)
    track_details = get_track_details(track_id)
    artist_name = track_details['artist']
    track_name = track_details['name']

    selected_features = ["valence", "danceability", "energy"]
    
    filtered_features = {
        key: value for key, value in features.items()
        if key in selected_features and isinstance(value, (int, float)) and 0 <= value <= 1
    }

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(filtered_features.values()),
        theta=list(filtered_features.keys()),
        fill='toself',
        name=f"{artist_name} - {track_name}",
        line=dict(color='blue')
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True
    )
    
    return fig, {'display': 'block'}

# Show the comparison UI when the Compare button is clicked
@app.callback(
    Output('compare-div', 'style'),
    [Input('compare-button', 'n_clicks')]
)
def show_comparison_ui(n_clicks):
    if n_clicks:
        return {'display': 'block'}
    return {'display': 'none'}

# Update the dropdown for the second track
@app.callback(
    Output('dropdown-track-2', 'options'),
    [Input('search-button-2', 'n_clicks')],
    [State('track-name-2', 'value'),
     State('artist-name-2', 'value')]
)
def update_dropdown_2(n_clicks, track_name_2, artist_name_2):
    if n_clicks is None or not track_name_2:
        return []
    
    results_2 = search_track(track_name_2, artist_name_2, limit=10)
    options_2 = [{'label': f"{track['name']} by {track['artists'][0]['name']} (Popularity: {track['popularity']})", 'value': track['id']} for track in results_2]
    
    return options_2

# Update the radar chart for the comparison
@app.callback(
    Output('comparison-radar-chart', 'figure'),
    [Input('dropdown-track-2', 'value')],
    [State('dropdown-track', 'value')]
)
def update_comparison_chart(track_id_2, track_id_1):
    if track_id_1 and track_id_2:
        comparison = compare_two_tracks(track_id_1, track_id_2)
        filtered_comparison = {
            feature: values
            for feature, values in comparison.items()
            if feature not in ['id', 'track_1_details', 'track_2_details'] and 
            0 <= values['track_1'] <= 1 and 
            0 <= values['track_2'] <= 1
        }

        features = list(filtered_comparison.keys())
        values_1 = [filtered_comparison[feature]['track_1'] for feature in features]
        values_2 = [filtered_comparison[feature]['track_2'] for feature in features]
        track_label_1 = f"{comparison['track_1_details']['artist']} - {comparison['track_1_details']['name']}"
        track_label_2 = f"{comparison['track_2_details']['artist']} - {comparison['track_2_details']['name']}"

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

    return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
