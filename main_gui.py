# main_gui.py
import json
import PySimpleGUI as Sg
from pathlib import Path
from compta.file_reader import read_excel
from compta.plotter import graph_plotter
from gui.layouts import (
    layout,
    make_layout_create_output,
    filename,
    cred,
    output,
    months,
    fetch,
    years,
    progress_layout,
    previous_config
)


window = Sg.Window("Compta", layout)
first_year = years[0]
last_year = years[-1]

# Run the Event Loop
while True:
    event, values = window.read()

    if event == "Exit" or event == Sg.WIN_CLOSED:
        break

    if event == "-OUTPUT-":
        output = values[event]
    elif event == "-CRED-":
        cred = values[event]
    elif event == "-FILENAME-":
        filename = values[event]
    elif "-MONTH-" in event:
        month = event.replace("-MONTH-", "")
        if month in months:
            months.remove(month)
        else:
            months.append(month)
    elif "YEAR-" in event:
        try:
            int(values[event])
            if "FIRST" in event:
                first_year = values[event]
            else:
                last_year = values[event]
        except ValueError:
            Sg.Popup(f"Invalide year '{values['-FIRSTYEAR-']}'")
            continue
    elif event == "-FETCH-":
        fetch = bool(values["-FETCH-"])
    elif event == "RUN":
        if len(months) == 0:
            Sg.Popup("You must select at least one month!")
            continue
        cred = Path(cred)
        output = Path(output)
        if int(first_year) > int(last_year):
            Sg.Popup(f"First year '{first_year}' can not be greater than last year '{last_year}'")
            continue
        else:
            years = [str(y) for y in list(range(int(first_year), int(last_year)+1))]
        if not output.is_dir():
            window_create_output = Sg.Window("Compta", make_layout_create_output(output))
            event2, value2 = window_create_output.read()
            if event2 == "YES":
                output.mkdir(parents=True)
            window_create_output.close()
        if output.is_dir():
            window_layout = Sg.Window("Progressions", [[progress_layout(len(years), len(months))]], finalize=True)
            graph_plotter(
                dataframe=read_excel(
                    filename=filename,
                    fetch=fetch,
                    output_dir=output,
                    cred=cred,
                    months=months,
                    years=years,
                    prgbar=window_layout,
                ),
                output=str(Path(output) / f"{filename}.html"),
            )
            window_layout.close()
    elif event == "EXIT":
        break

window.close()

prev = {
    "fetch": fetch,
    "filename": filename,
    "output": str(Path(output).absolute()),
    "years": [first_year, last_year],
    "cred": str(Path(cred).absolute()),
    "months": months
}

with open(str(previous_config), "w") as f:
    json.dump(prev, f)
