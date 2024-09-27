import tomli  # tomli for reading
import tomlkit  # tomlkit for preserving comments

# Upload the TOML file, preserving comments
@app.callback(
    Output('config-editor', 'children'),
    Output('save-toml-button', 'disabled'),
    Input('upload-toml', 'contents'),
    State('upload-toml', 'filename'),
    prevent_initial_call=True,
)
def upload_toml(contents, filename):
    if contents:
        # Decode the uploaded TOML file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Read the TOML file with tomli to preserve comments
        config_content = tomli.loads(decoded.decode('utf-8'))

        # Dynamically create input fields for the TOML content
        inputs = []

        for key, value in config_content.items():
            inputs.append(
                html.Div(
                    [
                        dbc.Label(f'{key}:'),
                        dbc.Input(
                            id={'type': 'config-input', 'index': key},
                            value=str(value),
                            debounce=True,
                        ),
                    ],
                    style={'margin-bottom': '10px'},
                )
            )

        return inputs, False  # Enable the Save button
    return [], True  # Disable the Save button if no file is uploaded


# Save the modified TOML file, preserving comments
@app.callback(
    Output('output-state', 'children'),
    Input('save-toml-button', 'n_clicks'),
    State({'type': 'config-input', 'index': dash.ALL}, 'value'),
    State({'type': 'config-input', 'index': dash.ALL}, 'id'),
    prevent_initial_call=True,
)
def save_toml(n_clicks, input_values, input_ids):
    if n_clicks:
        # Load the original file to preserve its structure and comments
        with open('src/integrator/run_config.toml', 'r') as f:
            config_doc = tomlkit.parse(f.read())

        # Update the config_doc with new values
        for item, value in zip(input_ids, input_values):
            config_doc[item['index']] = convert_value(value)

        # Write the updated content back, preserving comments
        with open('src/integrator/run_config.toml', 'w') as f:
            f.write(tomlkit.dumps(config_doc))

        return f"Config file saved successfully as 'run_config.toml'."
    return ''
