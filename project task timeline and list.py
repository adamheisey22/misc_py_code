import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

def tasks_to_markdown(tasks_list):
    # Initialize an empty markdown string
    markdown_text = "## Project Plan\n\n"
    markdown_text += "Below is the list of tasks with their respective start and end dates:\n\n"

    # Iterate over the tasks and add each to the markdown string
    for task in tasks_list:
        markdown_text += f"- **{task['Task']}**: Start: `{task['Start']}`, Finish: `{task['Finish']}`\n"

    return markdown_text


# Define the project tasks and their start and end dates in a list of dictionaries
tasks_list = [
    {"Task": "Meet with Mala -- coordinate documentation efforts", "Start": "2024-01-28", "Finish": "2024-02-04"},
    {"Task": "Research sphinx methods (python, AIMMS, R)", "Start": "2024-02-11", "Finish": "2024-03-03"},
    {"Task": "[Stretch Goal] use case for sphinx with R and AIMMS", "Start": "2024-03-10", "Finish": "2024-03-17"},
    {"Task": "Guide - template development", "Start": "2024-03-24", "Finish": "2024-04-07"},
    {"Task": "Write/develop documentation for demo/prototype", "Start": "2024-04-14", "Finish": "2024-05-05"},
    {"Task": "System Demand Shapes model/code support (30 year normalized profile)", "Start": "2024-02-18", "Finish": "2024-03-10"},
    {"Task": "End-Use load profile model/code support (30 year normalized profile)", "Start": "2024-03-17", "Finish": "2024-04-07"},
    {"Task": "Workflow support", "Start": "2024-04-14", "Finish": "2024-04-28"},
    {"Task": "[Stretch goal] document project code for publishing", "Start": "2024-05-05", "Finish": "2024-05-12"},
    {"Task": "Demo/prototype repository organization scope", "Start": "2024-05-19", "Finish": "2024-05-26"},
    {"Task": "Ad hoc tech support", "Start": "2024-01-28", "Finish": "2024-06-23"},
    {"Task": "python/sql presentation python user group", "Start": "2024-06-02", "Finish": "2024-06-09"}
]

# Convert list of dictionaries to a DataFrame
df = pd.DataFrame(tasks_list)

# Convert dates from string to datetime
df['Start'] = pd.to_datetime(df['Start'])
df['Finish'] = pd.to_datetime(df['Finish'])

# Plotting
fig, ax = plt.subplots(figsize=(14, 8))
# Create a list of colors, one for each task
colors = plt.cm.viridis(np.linspace(0, 1, len(df)))

# Create the bars for the Gantt chart
for i, task in df.iterrows():
    start = mdates.date2num(task['Start'])
    finish = mdates.date2num(task['Finish'])
    ax.barh(task['Task'], finish - start, left=start, height=0.4, color=colors[i])

# Set the x-axis as dates
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

# Format the plot
plt.title('Project Timeline')
plt.xlabel('Date')
plt.ylabel('Task')
plt.grid(True)
plt.tight_layout()

# Generate the markdown text
markdown_output = tasks_to_markdown(tasks_list)

# Print the markdown output
print(markdown_output)

# Show plot
plt.show()
