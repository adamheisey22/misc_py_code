import time

# Callback to handle run button click and show progress
@app.callback(
    Output('status', 'children'),
    Output('progress', 'value'),
    Input('run-button', 'n_clicks'),
    State('mode-selector', 'value'),
    prevent_initial_call=True,
)
def run_mode(n_clicks, selected_mode):
    max_retries = 3  # Number of retries before giving up
    retries = 0
    
    while retries < max_retries:
        try:
            # Start the subprocess using Popen to capture stdout and stderr
            process = subprocess.Popen(
                ['python', 'main.py', '--mode', selected_mode],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Print the terminal outputs in real-time
            for stdout_line in iter(process.stdout.readline, ""):
                print(stdout_line.strip())  # Print each line of output
            process.stdout.close()
            return_code = process.wait()

            # If the subprocess finishes successfully
            if return_code == 0:
                return (
                    f"{selected_mode.capitalize()} mode has finished running. See results in output/'{selected_mode}'.",
                    100,
                )

            # If the subprocess encounters an error, raise an exception to trigger retry
            else:
                raise subprocess.CalledProcessError(return_code, ['python', 'main.py', '--mode', selected_mode])

        except subprocess.CalledProcessError as e:
            retries += 1
            error_message = f"Error running {selected_mode} mode (attempt {retries}/{max_retries}). Retrying..."
            with open('error_log.txt', 'a') as log_file:
                log_file.write(f"{datetime.now()}: Error running {selected_mode} mode: {str(e)}\n")
            if retries >= max_retries:
                return f"Failed to run {selected_mode} mode after {max_retries} attempts. Please check the log file.", 0

        # Wait for a short time before retrying
        time.sleep(5)
