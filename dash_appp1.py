import threading
import time

# Add an interval for real-time updates
app.layout = dbc.Container(
    [
        html.H1('BlueSky Model Runner', className='text-center'),
        html.Img(src=image_src),
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
        # Textarea for real-time subprocess output
        html.Hr(),
        dcc.Textarea(
            id='terminal-output',
            style={'width': '100%', 'height': 300},
            readOnly=True,  # Output is read-only
        ),
        # Interval to trigger periodic updates to terminal output
        dcc.Interval(id='interval-component', interval=2*1000, n_intervals=0),  # 2-second interval
        # Section for uploading and editing TOML config file
        html.Hr(),
        html.H4('Edit Config (TOML)'),
        dcc.Upload(id='upload-toml', children=html.Button('Upload TOML'), multiple=False),
        html.Div(id='config-editor'),
        dbc.Button('Save Changes', id='save-toml-button', className='mt-2', disabled=False),
    ],
    fluid=True,
)

# Global variable to store the terminal output
terminal_output_data = ""

def run_subprocess(selected_mode):
    global terminal_output_data
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

    except subprocess.CalledProcessError as e:
        terminal_output_data += f"Error running {selected_mode} mode: {str(e)}\n"

# Callback to start the subprocess in a new thread
@app.callback(
    Output('status', 'children'),
    Output('progress', 'value'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True,
)
def run_mode(n_clicks, selected_mode):
    global terminal_output_data
    terminal_output_data = ""  # Reset terminal output when running a new mode
    threading.Thread(target=run_subprocess, args=(selected_mode,)).start()
    return f"Running {selected_mode.capitalize()} mode...", 50

# Callback to update the terminal output every interval
@app.callback(
    Output('terminal-output', 'value'),
    Input('interval-component', 'n_intervals'),
)
def update_terminal_output(n):
    global terminal_output_data
    return terminal_output_data
