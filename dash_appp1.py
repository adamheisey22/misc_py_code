import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import toml
import base64
import io
from pathlib import Path
import ast

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'BlueSky Model Runner'

# Define layout
app.layout = dbc.Container([
    html.H1('BlueSky Model Runner', className='text-center'),

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
    dbc.Button('Save Changes', id='save-toml-button', className='mt-2', disabled=True),

    html.Div(id='output-state'),

], fluid=True)

# Store the TOML content in memory
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


# Save the modified TOML file
@app.callback(
    Output('output-state', 'children'),
    Input('save-toml-button', 'n_clicks'),
    State({'type': 'config-input', 'index': dash.ALL}, 'value'),
    State({'type': 'config-input', 'index': dash.ALL}, 'id'),
    prevent_initial_call=True
)
def save_toml(n_clicks, input_values, input_ids):
    if n_clicks:
        # Create a dictionary from input values and their respective keys
        updated_config = {item['index']: convert_value(value) for item, value in zip(input_ids, input_values)}

        # Write the updated content to a new TOML file
        with open("updated_config.toml", 'w') as f:
            toml.dump(updated_config, f)

        return f"Config file saved successfully as 'updated_config.toml'."
    return ''


# Function to convert values back to original types (like the original logic)
def convert_value(value):
    """Function to maintain the original type for config values"""
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


# Callback to handle run button click
@app.callback(
    Output('progress', 'value'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True
)
def run_mode(n_clicks, selected_mode):
    # Placeholder logic to simulate running a process
    return 100  # Progress is set to complete


if __name__ == '__main__':
    app.run_server(debug=True)
