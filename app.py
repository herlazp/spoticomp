import dash
import dash_core_components as dcc
import dash_html_components as html
from api.spotify_api import get_track_features

# Initialize the Dash app
app = dash.Dash(__name__)

# Example track ID for demonstration
track_id = 'your_track_id'

# Fetch track features using the function from spotify_api.py
track_features = get_track_features(track_id)

# Layout of the Dash app
app.layout = html.Div(children=[
    html.H1(children='Spotify Track Features'),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': list(track_features.keys()), 'y': list(track_features.values()), 'type': 'bar'}
            ],
            'layout': {
                'title': 'Track Features'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
