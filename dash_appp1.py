import threading
import time
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import subprocess

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Global variable to store the terminal output
terminal_output_data = ""
completion_status = False

# Layout
app.layout = dbc.Container(
    [
        html.H1('BlueSky Model Runner', className='text-center'),
        html.Img(src="/assets/ProjectBlueSkywebheaderimageblack.jpg"),
        html.H2(id='status', className='text-center', style={'color': 'red'}),
        html.H3(id='output-state'),
        dbc.Label('Select Mode to Run:'),
        dcc.RadioItems(
            id='mode-selector',
            options=[
                {'label': mode, 'value': mode}
                for mode in ['elec', 'h2', 'residential', 'unified-combo', 'gs-combo', 'standalone']
            ],
            value='elec',
        ),
        dbc.Button('Run', id='run-button', color='primary', className='mt-2'),
        dcc.Loading(dbc.Progress(id='progress', value=0, max=100, style={'height': '30px'})),
        html.Hr(),
        dcc.Textarea(
            id='terminal-output',
            style={'width': '100%', 'height': 300},
            readOnly=True,  # Output is read-only
        ),
        dcc.Interval(id='interval-component', interval=2*1000, n_intervals=0),  # 2-second interval
        dcc.Store(id='completion-status', data={'completed': False}),  # Store to keep track of the completion
        html.Hr(),
        html.H4('Edit Config (TOML)'),
        dcc.Upload(id='upload-toml', children=html.Button('Upload TOML'), multiple=False),
        html.Div(id='config-editor'),
        dbc.Button('Save Changes', id='save-toml-button', className='mt-2', disabled=False),
    ],
    fluid=True,
)

def run_subprocess(selected_mode):
    global terminal_output_data
    global completion_status
    completion_status = False  # Reset completion status

    try:
        # Start the subprocess using Popen to capture stdout and stderr
        process = subprocess.Popen(
            ['python', 'main.py', '--mode', selected_mode],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Read the terminal outputs in real-time and update global variable
        for stdout_line in iter(process.stdout.readline, ""):
            terminal_output_data += stdout_line.strip() + "\n"

        process.stdout.close()
        process.wait()

        # If subprocess completes successfully
        completion_status = True

    except subprocess.CalledProcessError as e:
        terminal_output_data += f"Error running {selected_mode} mode: {str(e)}\n"

# Callback to start the subprocess in a new thread
@app.callback(
    Output('status', 'children'),
    Output('progress', 'value'),
    Output('completion-status', 'data'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True,
)
def run_mode(n_clicks, selected_mode):
    global terminal_output_data
    terminal_output_data = ""  # Reset terminal output when running a new mode
    threading.Thread(target=run_subprocess, args=(selected_mode,)).start()
    return f"Running {selected_mode.capitalize()} mode...", 50, {'completed': False}

# Callback to update the terminal output and completion status every interval
@app.callback(
    Output('terminal-output', 'value'),
    Output('progress', 'value'),
    Output('status', 'children'),
    Input('interval-component', 'n_intervals'),
    State('completion-status', 'data')
)
def update_terminal_output(n, completion_data):
    global terminal_output_data
    global completion_status

    # Check if the process is completed
    if completion_status:
        return terminal_output_data, 100, "Mode run completed successfully."

    return terminal_output_data, 50, "Running mode..."

if __name__ == '__main__':
    app.run_server(debug=True)
