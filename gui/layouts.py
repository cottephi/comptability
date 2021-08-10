from compta.file_getter import all_months
from pathlib import Path
import PySimpleGUI as Sg
import json

Sg.theme('Dark Brown')

previous_config = Path(__file__).parent / ".previous_configs.json"

if not previous_config.is_file():
    # Default run values
    fetch = False
    filename = "compta"
    cred = "./credentials.json"
    output = "./outputs"
    years = ["2021"]
    months = []
else:
    with open(str(previous_config), "r") as f:
        prev = json.load(f)
    fetch = prev["fetch"]
    filename = prev["filename"]
    cred = prev["cred"]
    output = prev["output"]
    years = prev["years"]
    months = prev["months"]


# First the window layout in 2 columns

line = [
    [
        Sg.Text("Output directory", size=(25, 1), justification="left"),
        Sg.In(
            size=(25, 1),
            enable_events=True,
            key="-OUTPUT-",
            default_text=Path(output).absolute(),
            justification="right",
        ),
        Sg.FolderBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Credential File", size=(25, 1), justification="left"),
        Sg.In(enable_events=True, key="-CRED-", default_text=Path(cred).absolute(), justification="right"),
        Sg.FileBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Google Sheet name\n(without the year)", size=(25, 2), justification="left"),
        Sg.InputText(enable_events=True, key="-FILENAME-", default_text=filename, justification="right"),
    ],
    [Sg.HSep()],
    [Sg.Checkbox("Fetch", default=fetch, enable_events=True, key="-FETCH-")],
    [Sg.HSep()],
    [
        Sg.Checkbox(
            month, size=(5, 1), key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False
        )
        for month in all_months[:4]
    ],
    [
        Sg.Checkbox(
            month, size=(5, 1), key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False
        )
        for month in all_months[4:8]
    ],
    [
        Sg.Checkbox(
            month, size=(5, 1), key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False
        )
        for month in all_months[8:]
    ],
    [Sg.HSep()],
    [
        Sg.Text("First year:", size=(25, 1), justification="left"),
        Sg.InputText(enable_events=True, key="-FIRSTYEAR-", default_text=years[0], justification="right"),
    ],
    [
        Sg.Text("Last year:", size=(25, 1), justification="left"),
        Sg.InputText(enable_events=True, key="-LASTYEAR-", default_text=years[-1], justification="right"),
    ],
]

layout = [[Sg.Column(line), Sg.VSep(), Sg.Column([[Sg.Button("RUN")], [Sg.Button("EXIT")]])]]


def make_layout_create_output(path):
    return [
        [
            Sg.Column([[Sg.Text(f"Output directory {path} does not exist. Do you want to create it ?")]]),
            Sg.HSep(),
            Sg.Column([[Sg.Button("YES")], [Sg.Button("NO")]]),
        ]
    ]


def make_progress_bar(value_max: int, name: str, text: str):
    return (
        [Sg.Text(text)],
        [Sg.ProgressBar(max_value=value_max, orientation="h", key=name, bar_color=("red", "black"), size=(15, 4))],
    )


def progress_layout(nyears: int, nmonths: int) -> Sg.Column:
    return Sg.Column(
        [
            *make_progress_bar(nyears, "download", "Downloading years files"),
            [Sg.HSep()],
            *make_progress_bar(nyears, "open_years", "Opening years files"),
            [Sg.HSep()],
            *make_progress_bar(nmonths, "get_months", "Extracting months spreadsheets"),
            [Sg.HSep()],
            *make_progress_bar(nyears, "read_years", "Reading years"),
            [Sg.HSep()],
            *make_progress_bar(nmonths, "read_months", "Reading months"),
        ]
    )
