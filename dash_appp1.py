import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import toml
from pathlib import Path
from definitions import PROJECT_ROOT, OUTPUT_ROOT
from src.integrator.utilities import make_output_dir, setup_logger
from src.integrator.runner import run_elec_solo, run_h2_solo
from src.integrator.gs_elec_hyd_res import run_gs_combo
from src.integrator.unified_elec_hyd_res import run_unified_res_elec_h2
import os

# Specify default config path
default_config_path = Path(PROJECT_ROOT, 'src/integrator', 'run_config.toml')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Model Runner"), width={"size": 6, "offset": 3}),
    ]),
    dbc.Row([
        dbc.Col(html.Label("Select Mode to Run:"), width=12),
        dbc.Col(
            dcc.RadioItems(
                id='mode-selector',
                options=[
                    {'label': 'elec', 'value': 'elec'},
                    {'label': 'h2', 'value': 'h2'},
                    {'label': 'unified-combo', 'value': 'unified-combo'},
                    {'label': 'gs-combo', 'value': 'gs-combo'}
                ],
                value='elec',
                labelStyle={'display': 'block'}
            ), width=6
        ),
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Run", id='run-button', color="primary", className="me-1"), width={"size": 2, "offset": 5}),
    ], style={"paddingTop": "20px"}),
    dbc.Row([
        dbc.Col(dbc.Spinner(html.Div(id='progress-output')), width=12),
    ], style={"paddingTop": "20px"}),
    dbc.Row([
        dbc.Col(html.Div(id='status-output'), width=12),
    ], style={"paddingTop": "10px"}),
    dbc.Row([
        dbc.Col(dbc.Button("Edit Config (TOML)", id='edit-config-button', color="secondary", className="me-1"), width={"size": 2, "offset": 5}),
    ], style={"paddingTop": "20px"}),
])

# Combined callback to handle both running the mode and editing the TOML file
@app.callback(
    [Output('progress-output', 'children'), Output('status-output', 'children')],
    [Input('run-button', 'n_clicks'), Input('edit-config-button', 'n_clicks')],
    [State('mode-selector', 'value')],
    prevent_initial_call=True
)
def handle_mode_and_edit(run_clicks, edit_clicks, mode):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", "No action triggered."

    # Determine which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'run-button':
        if mode:
            progress_message = f"Running {mode} mode... Please wait."
            try:
                OUTPUT_ROOT.mkdir(exist_ok=True)
                output_dir = make_output_dir(OUTPUT_ROOT)
                logger = setup_logger(output_dir)
                logger.info('Starting Logging')
                with open(default_config_path, 'r') as src:
                    config = toml.load(src)

                if mode == 'elec':
                    run_elec_solo(config_path=default_config_path)
                elif mode == 'h2':
                    HYDROGEN_ROOT = PROJECT_ROOT / 'src/models/hydrogen'
                    data_path = HYDROGEN_ROOT / 'inputs/single_region'
                    run_h2_solo(data_path=data_path, config_path=default_config_path)
                elif mode == 'gs-combo':
                    run_gs_combo(config_path=default_config_path)
                elif mode == 'unified-combo':
                    run_unified_res_elec_h2(config_path=default_config_path)
                status_message = f"{mode.capitalize()} mode finished successfully!"
            except Exception as e:
                status_message = f"An error occurred: {str(e)}"
        else:
            progress_message = ""
            status_message = "Please select a mode to run."
        return progress_message, status_message

    elif button_id == 'edit-config-button':
        filepath = default_config_path  # Simplified for demo; normally you'd select the file
        if os.path.exists(filepath):
            with open(filepath, 'r') as src:
                config = toml.load(src)
            config_summary = f"Config file {Path(filepath).name} loaded successfully. Editing feature to be implemented."
            return "", config_summary

        return "", "No config file found."


if __name__ == '__main__':
    app.run_server(debug=True)
