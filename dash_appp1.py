import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import toml
import base64
import io
import ast
import subprocess
import csv
from pathlib import Path
import pandas as pd
import os
import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'BlueSky Model Runner'

# Define layout
app.layout = dbc.Container([
    html.H1('BlueSky Model Runner', className='text-center'),

    # Section for choosing output folder
    html.Hr(),
    html.H4('Choose Output Folder'),
    dbc.Input(id='output-folder', type='text', placeholder='Enter output folder path', debounce=True),
    dbc.Button('Confirm Output Folder', id='confirm-folder-button', className='mt-2'),
    html.Div(id='folder-status'),

    dbc.Label('Select Mode to Run:'),
    dcc.RadioItems(
        id='mode-selector',
        options=[{'label': mode, 'value': mode} for mode in ['elec', 'h2', 'residential', 'unified-combo', 'gs-combo', 'standalone']],
        value='elec',
        inline=True
    ),

    dbc.Button('Run', id='run-button', color='primary', className='mt-2'),
    dcc.Loading(dbc.Progress(id='progress', value=0, max=100, style={'height': '30px'})),

    # Section for uploading and editing TOML config file
    html.Hr(),
    html.H4('Edit Config (TOML)'),
    dcc.Upload(id='upload-toml', children=html.Button('Upload TOML'), multiple=False),
    html.Div(id='config-editor'),
    dbc.Button('Save TOML Changes', id='save-toml-button', className='mt-2', disabled=True),

    # Section for uploading and editing CSV file
    html.Hr(),
    html.H4('Edit CSV File'),
    dcc.Upload(id='upload-csv', children=html.Button('Upload CSV'), multiple=False),
    html.Div(id='csv-editor'),
    dbc.Button('Save CSV Changes', id='save-csv-button', className='mt-2', disabled=True),

    html.Div(id='output-state'),

], fluid=True)


# Verify output folder exists or create it
@app.callback(
    Output('folder-status', 'children'),
    Input('confirm-folder-button', 'n_clicks'),
    State('output-folder', 'value'),
    prevent_initial_call=True
)
def confirm_output_folder(n_clicks, folder_path):
    if folder_path:
        output_dir = Path(folder_path)
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                return f"Folder '{output_dir}' created successfully."
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return f"Folder '{output_dir}' already exists."
    return "Please enter a valid folder path."


# TOML File Handling
@app.callback(
    Output('config-editor', 'children'),
    Output('save-toml-button', 'disabled'),
    Input('upload-toml', 'contents'),
    State('upload-toml', 'filename'),
    prevent_initial_call=True
)
def upload_toml(contents, filename):
    if contents:
        # Decode the uploaded TOML file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        config_content = toml.loads(decoded.decode('utf-8'))

        # Dynamically create input fields for the TOML content
        inputs = []
        for key, value in config_content.items():
            inputs.append(html.Div([
                dbc.Label(f'{key}:'),
                dbc.Input(id={'type': 'config-input', 'index': key}, value=str(value), debounce=True),
            ], style={'margin-bottom': '10px'}))

        return inputs, False  # Enable the Save button
    return [], True  # Disable the Save button if no file is uploaded


@app.callback(
    Output('output-state', 'children'),
    Input('save-toml-button', 'n_clicks'),
    State({'type': 'config-input', 'index': dash.ALL}, 'value'),
    State({'type': 'config-input', 'index': dash.ALL}, 'id'),
    State('output-folder', 'value'),
    prevent_initial_call=True
)
def save_toml(n_clicks, input_values, input_ids, output_folder):
    if n_clicks and output_folder:
        # Create a dictionary from input values and their respective keys
        updated_config = {item['index']: convert_value(value) for item, value in zip(input_ids, input_values)}

        output_path = Path(output_folder) / "updated_config.toml"
        # Write the updated content to the specified folder
        try:
            with open(output_path, 'w') as f:
                toml.dump(updated_config, f)
            return f"Config file saved successfully as '{output_path}'."
        except Exception as e:
            return f"Error: {str(e)}"
    return "Please specify an output folder."


# CSV File Handling
@app.callback(
    Output('csv-editor', 'children'),
    Output('save-csv-button', 'disabled'),
    Input('upload-csv', 'contents'),
    State('upload-csv', 'filename'),
    prevent_initial_call=True
)
def upload_csv(contents, filename):
    if contents:
        # Decode the uploaded CSV file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        csv_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Dynamically create input fields for the CSV content
        table_header = [html.Tr([html.Th(col) for col in csv_data.columns])]
        table_rows = []

        for i, row in csv_data.iterrows():
            table_rows.append(
                html.Tr([
                    html.Td(dbc.Input(value=str(row[col]), id={'type': 'csv-input', 'index': (i, col)})) 
                    for col in csv_data.columns
                ])
            )

        table = dbc.Table(table_header + table_rows, bordered=True, striped=True, hover=True)
        return table, False  # Enable the Save button

    return [], True  # Disable the Save button if no file is uploaded


@app.callback(
    Output('output-state', 'children'),
    Input('save-csv-button', 'n_clicks'),
    State({'type': 'csv-input', 'index': dash.ALL}, 'value'),
    State({'type': 'csv-input', 'index': dash.ALL}, 'id'),
    State('output-folder', 'value'),
    prevent_initial_call=True
)
def save_csv(n_clicks, input_values, input_ids, output_folder):
    if n_clicks and output_folder:
        # Create a DataFrame from input values
        csv_data = pd.DataFrame(columns=set([col for _, col in input_ids]))

        for (i, col), value in zip(input_ids, input_values):
            if i not in csv_data.index:
                csv_data.loc[i] = [None] * len(csv_data.columns)
            csv_data.at[i, col] = value

        output_path = Path(output_folder) / 'updated_config.csv'
        # Write the updated DataFrame to the specified folder
        try:
            csv_data.to_csv(output_path, index=False)
            return f"CSV file saved successfully as '{output_path}'."
        except Exception as e:
            return f"Error: {str(e)}"
    return "Please specify an output folder."


# Function to convert values back to original types (like the original logic)
def convert_value(value):
    """Function to maintain the original type for config values"""
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


# Callback to handle run button click and show progress
@app.callback(
    Output('progress', 'value'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    State('output-folder', 'value'),
    prevent_initial_call=True
)
def run_mode(n_clicks, selected_mode, output_folder):
    if output_folder:
        output_dir = Path(output_folder) / f"{selected_mode}_run_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ['python', 'main.py', '--mode', selected_mode, '--config', str(output_dir)],
                check=True
            )
            return 100  # Complete the progress
        except subprocess.CalledProcessError as e:
            return 0  # Error, reset the progress
    return 0  # If no output folder is specified


if __name__ == '__main__':
    app.run_server(debug=True)
