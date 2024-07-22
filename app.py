import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# Read the CSV file
artist_name = 'Ignomala'  # Replace with your artist name
filename = f"{artist_name}_features.csv"
df = pd.read_csv(filename)

# Initialize the Dash app
app = dash.Dash(__name__)

# Example visualization: bar chart of features
app.layout = html.Div(children=[
    html.H1(children=f'{artist_name} Track Features'),

    dcc.Graph(
        id='track-features-bar',
        figure={
            'data': [
                {'x': df['name'], 'y': df['danceability'], 'type': 'bar', 'name': 'Danceability'},
                {'x': df['name'], 'y': df['energy'], 'type': 'bar', 'name': 'Energy'}
                # Add more features as needed
            ],
            'layout': {
                'title': 'Track Features'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
