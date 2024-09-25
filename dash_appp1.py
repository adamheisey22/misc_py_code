# Add a Textarea to display output in real-time
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
        # Section for uploading and editing TOML config file
        html.Hr(),
        html.H4('Edit Config (TOML)'),
        dcc.Upload(id='upload-toml', children=html.Button('Upload TOML'), multiple=False),
        html.Div(id='config-editor'),
        dbc.Button('Save Changes', id='save-toml-button', className='mt-2', disabled=False),
    ],
    fluid=True,
)

# Callback to handle run button click, update progress, and show real-time terminal output
@app.callback(
    [Output('status', 'children'), Output('progress', 'value'), Output('terminal-output', 'value')],
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True,
)
def run_mode(n_clicks, selected_mode):
    max_retries = 3  # Number of retries before giving up
    retries = 0
    terminal_output = ""  # Initialize the output string
    
    while retries < max_retries:
        try:
            # Start the subprocess using Popen to capture stdout and stderr
            process = subprocess.Popen(
                ['python', 'main.py', '--mode', selected_mode],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Read the terminal outputs in real-time and update the text area
            for stdout_line in iter(process.stdout.readline, ""):
                terminal_output += stdout_line.strip() + "\n"
                yield "", 50, terminal_output  # Progress stays at 50 while running

            process.stdout.close()
            return_code = process.wait()

            # If the subprocess finishes successfully
            if return_code == 0:
                return (
                    f"{selected_mode.capitalize()} mode has finished running. See results in output/'{selected_mode}'.",
                    100,  # Progress is complete
                    terminal_output
                )

            # If the subprocess encounters an error, raise an exception to trigger retry
            else:
                raise subprocess.CalledProcessError(return_code, ['python', 'main.py', '--mode', selected_mode])

        except subprocess.CalledProcessError as e:
            retries += 1
            error_message = f"Error running {selected_mode} mode (attempt {retries}/{max_retries}). Retrying...\n"
            terminal_output += error_message
            with open('error_log.txt', 'a') as log_file:
                log_file.write(f"{datetime.now()}: Error running {selected_mode} mode: {str(e)}\n")
            if retries >= max_retries:
                return f"Failed to run {selected_mode} mode after {max_retries} attempts. Please check the log file.", 0, terminal_output

        # Wait for a short time before retrying
        time.sleep(5)

