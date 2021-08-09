from compta.file_getter import all_months
from pathlib import Path
import PySimpleGUI as Sg
import json

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
        Sg.Text("Output directory"),
        Sg.In(size=(25, 1), enable_events=True, key="-OUTPUT-", default_text=Path(output).absolute()),
        Sg.FolderBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Credential File"),
        Sg.In(size=(25, 1), enable_events=True, key="-CRED-", default_text=Path(cred).absolute()),
        Sg.FileBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Google Sheet name (without the year)"),
        Sg.InputText(enable_events=True, key="-FILENAME-", default_text=filename),
    ],
    [Sg.HSep()],
    [Sg.Checkbox("Fetch", default=fetch, enable_events=True, key="-FETCH-")],
    [Sg.HSep()],
    [
        Sg.Checkbox(month, key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False)
        for month in all_months[:4]
    ],
    [
        Sg.Checkbox(month, key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False)
        for month in all_months[4:8]
    ],
    [
        Sg.Checkbox(month, key=f"-MONTH-{month}", enable_events=True, default=True if month in months else False)
        for month in all_months[8:]
    ],
    [Sg.HSep()],
    [Sg.Text("First year:"), Sg.InputText(enable_events=True, key="-FIRSTYEAR-", default_text=years[0])],
    [Sg.Text("Last year:"), Sg.InputText(enable_events=True, key="-LASTYEAR-", default_text=years[-1])],
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
        [Sg.ProgressBar(max_value=value_max, orientation="h", key=name, bar_color=("red", "blue"), size=(20, 5))],
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
