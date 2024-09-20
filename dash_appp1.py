import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import toml
import base64
import io
import ast
import subprocess
from pathlib import Path
import datetime
import zipfile

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

    html.Hr(),
    html.Div(id='download-section')  # This will be where the download button/link is conditionally shown
], fluid=True)


# Store the TOML content in memory and create input fields for editing
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


# Callback to handle run button click and show progress
@app.callback(
    Output('progress', 'value'),
    Output('download-section', 'children'),
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
        # Zip the output and create the download link
        download_button = dbc.Button('Download Output Files', id='download-button', className='mt-2')
        return 100, download_button  # Run successful, show download button
    except subprocess.CalledProcessError as e:
        return 0, ''  # Error occurred, no download button


# Helper function to zip the output directory
def zip_output_directory(output_dir):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in output_dir.rglob('*'):
            zip_file.write(file, file.relative_to(output_dir))
    zip_buffer.seek(0)
    return zip_buffer


# Callback to handle downloading the output directory
@app.callback(
    Output('download-output', 'data'),
    Input('download-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True
)
def download_output(n_clicks, selected_mode):
    if n_clicks:
        output_dir = Path("OUTPUT_ROOT") / f"{selected_mode}_run_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        if output_dir.exists() and any(output_dir.iterdir()):
            zip_buffer = zip_output_directory(output_dir)
            encoded_zip = base64.b64encode(zip_buffer.read()).decode('utf-8')

            return dict(content=encoded_zip, filename=f"{selected_mode}_output.zip")
    return None


if __name__ == '__main__':
    app.run_server(debug=True)
