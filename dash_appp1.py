import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import toml
import csv
import subprocess
from pathlib import Path
import datetime
import ast

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'BlueSky Model Runner'

# Define layout
app.layout = dbc.Container([
    html.H1('BlueSky Model Runner', className='text-center'),
    html.Div(id='status', className='text-center'),

    dbc.Label('Select Mode to Run:'),
    dcc.RadioItems(
        id='mode-selector',
        options=[{'label': mode, 'value': mode} for mode in ['elec', 'h2', 'residential', 'unified-combo', 'gs-combo', 'standalone']],
        value='elec',
        inline=True
    ),

    dbc.Button('Run', id='run-button', color='primary', className='mt-2'),
    dcc.Loading(dbc.Progress(id='progress', value=0, max=100, style={'height': '30px'})),

    dbc.Button('Edit Config (TOML)', id='edit-toml-button', className='mt-2'),
    dcc.Upload(id='upload-toml', children=html.Button('Upload TOML'), multiple=False),
    dcc.Upload(id='upload-csv', children=html.Button('Upload CSV'), multiple=False),

    html.Div(id='output-state')
], fluid=True)

# Callback to handle run button click
@app.callback(
    Output('status', 'children'),
    Output('progress', 'value'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True
)
def run_mode(n_clicks, selected_mode):
    output_dir = Path("OUTPUT_ROOT") / f"{selected_mode}_run_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ['python', 'main.py', '--mode', selected_mode, '--config', str(Path("default_config_path"))],
            check=True
        )
        return f"{selected_mode.capitalize()} mode has finished running. See results in '{output_dir}'.", 100
    except subprocess.CalledProcessError as e:
        return f'Error: {str(e)}', 0

# Callback to handle TOML file upload
@app.callback(
    Output('output-state', 'children'),
    Input('upload-toml', 'contents'),
    prevent_initial_call=True
)
def upload_toml(contents):
    # Here you would handle the TOML file upload
    pass

# Callback to handle CSV file upload
@app.callback(
    Output('output-state', 'children'),
    Input('upload-csv', 'contents'),
    prevent_initial_call=True
)
def upload_csv(contents):
    # Here you would handle the CSV file upload
    pass

if __name__ == '__main__':
    app.run_server(debug=True)
