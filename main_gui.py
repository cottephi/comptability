# main_gui.py
import json
import PySimpleGUI as Sg
from pathlib import Path
from compta.file_reader import read_excel
from compta.plotter import graph_plotter, openfile
from gui.layouts import (
    layout,
    make_layout_create_output,
    configs,
    progress_layout,
    previous_config,
)

current_location = configs["output"]

window = Sg.Window("Compta", layout)
first_year = configs["years"][0]
last_year = configs["years"][-1]

# Run the Event Loop
while True:
    event, values = window.read()

    if event == "Exit" or event == Sg.WIN_CLOSED:
        break

    if event == "-OUTPUT-":
        configs["output"] = Path(values[event])
    elif event == "-CRED-":
        configs["cred"] = Path(values[event])
    elif event == "-FILENAME-":
        configs["filename"] = values[event]
    elif "-MONTH-" in event:
        month = event.replace("-MONTH-", "")
        if month in configs["months"]:
            configs["months"].remove(month)
        else:
            configs["months"].append(month)
    elif "-NAMES-" in event:
        configs["names"] = values[event].replace(" ", "").split(",")
    elif "-COMMON-" in event:
        configs["common"] = values[event]
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
        configs["fetch"] = bool(values["-FETCH-"])
    elif event == "-PLOTS-":
        pressed_path = current_location / values[event][0]
        if pressed_path.is_dir():
            current_location = pressed_path
            newcontent = [p.name for p in current_location.glob("*")]
            if current_location.stat() != configs["output"].stat():
                newcontent = [".."] + newcontent
            window["-PLOTS-"].update(newcontent)
        else:
            openfile(pressed_path)

    elif event == "RUN":
        if len("months") == 0:
            Sg.Popup("You must select at least one month!")
            continue
        if int(first_year) > int(last_year):
            Sg.Popup(f"First year '{first_year}' can not be greater than last year '{last_year}'")
            continue
        else:
            configs["years"] = [str(y) for y in list(range(int(first_year), int(last_year)+1))]
        if not configs["output"].is_dir():
            window_create_output = Sg.Window("Compta", make_layout_create_output(configs["output"]))
            event2, value2 = window_create_output.read()
            if event2 == "YES":
                configs["output"].mkdir(parents=True)
            window_create_output.close()
        if configs["output"].is_dir():
            window_layout = Sg.Window("Progressions", [[progress_layout(len(configs["years"]), len(configs["months"]))]], finalize=True)
            graph_plotter(
                dataframe=read_excel(
                    filename=configs["filename"],
                    fetch=configs["fetch"],
                    output_dir=configs["output"],
                    cred=configs["cred"],
                    months=configs["months"],
                    years=configs["years"],
                    prgbar=window_layout,
                ),
                output=configs["output"] / f"{configs['filename']}.html",
                names=configs["names"],
                common=configs["common"]
            )
            window_layout.close()

            if Path(configs["output"]).is_dir():
                newcontent = [p.name for p in current_location.glob("*")]
                if current_location.stat() != configs["output"].stat():
                    newcontent = [".."] + newcontent
                window["-PLOTS-"].update(newcontent)

    elif event == "EXIT":
        break

window.close()

prev = {
    "fetch": configs["fetch"],
    "filename": configs["filename"],
    "output": str(configs["output"].absolute()),
    "years": configs["years"],
    "cred": str(configs["cred"].absolute()),
    "months": configs["months"],
    "names": configs["names"],
    "common": configs["common"]
}

with open(str(previous_config), "w") as f:
    json.dump(prev, f)
