from compta.file_getter import all_months
from pathlib import Path
import PySimpleGUI as Sg
import json

Sg.theme("Dark Brown")

previous_config = Path(__file__).parent / ".previous_configs.json"

configs = {
    "fetch": False,
    "filename": "compta",
    "cred": Path("./credentials.json"),
    "output": Path("./outputs"),
    "years": ["2021"],
    "months": [],
    "names": ["Mop", "Philippe"],
    "common": "Commun",
}

if previous_config.is_file():
    with open(str(previous_config), "r") as f:
        prev = json.load(f)
    for conf in configs:
        if conf in prev:
            if conf == "output" or conf == "cred":
                configs[conf] = Path(prev[conf])
            else:
                configs[conf] = prev[conf]

output_content = []
if configs["output"].is_dir():
    output_content = [p.name for p in configs["output"].glob("*")]

# First the window layout in 2 columns

line = [
    [
        Sg.Text("Output directory", size=(25, 1), justification="left"),
        Sg.In(
            size=(25, 1),
            enable_events=True,
            key="-OUTPUT-",
            default_text=configs["output"].absolute(),
            justification="right",
        ),
        Sg.FolderBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Credential File", size=(25, 1), justification="left"),
        Sg.In(enable_events=True, key="-CRED-", default_text=configs["cred"].absolute(), justification="right"),
        Sg.FileBrowse(),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Google Sheet name\n(without the year)", size=(25, 2), justification="left"),
        Sg.InputText(enable_events=True, key="-FILENAME-", default_text=configs["filename"], justification="right"),
    ],
    [Sg.HSep()],
    [Sg.Checkbox("Fetch", default=configs["fetch"], enable_events=True, key="-FETCH-")],
    [Sg.HSep()],
    [
        Sg.Checkbox(
            month,
            size=(5, 1),
            key=f"-MONTH-{month}",
            enable_events=True,
            default=True if month in configs["months"] else False,
        )
        for month in all_months[:4]
    ],
    [
        Sg.Checkbox(
            month,
            size=(5, 1),
            key=f"-MONTH-{month}",
            enable_events=True,
            default=True if month in configs["months"] else False,
        )
        for month in all_months[4:8]
    ],
    [
        Sg.Checkbox(
            month,
            size=(5, 1),
            key=f"-MONTH-{month}",
            enable_events=True,
            default=True if month in configs["months"] else False,
        )
        for month in all_months[8:]
    ],
    [Sg.HSep()],
    [
        Sg.Text("First year:", size=(25, 1), justification="left"),
        Sg.InputText(enable_events=True, key="-FIRSTYEAR-", default_text=configs["years"][0], justification="right"),
    ],
    [
        Sg.Text("Last year:", size=(25, 1), justification="left"),
        Sg.InputText(enable_events=True, key="-LASTYEAR-", default_text=configs["years"][-1], justification="right"),
    ],
    [Sg.HSep()],
    [
        Sg.Text("Names:", size=(25, 1), justification="left"),
        Sg.InputText(
            enable_events=True,
            key="-NAMES-",
            default_text=str(configs["names"]).replace("[", "").replace("]", "").replace("'", ""),
            justification="right",
        ),
    ],
    [
        Sg.Text("Common:", size=(25, 1), justification="left"),
        Sg.InputText(enable_events=True, key="-COMMON-", default_text=configs["common"], justification="right"),
    ],
]

layout = [
    [
        Sg.Column(line),
        Sg.VSep(),
        Sg.Column([[Sg.Button("RUN")], [Sg.Button("EXIT")]]),
        Sg.VSep(),
        Sg.Column([[Sg.Listbox(values=output_content, bind_return_key=True, key="-PLOTS-", size=(30, 6))]]),
    ]
]


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
