# plotter.py
import os
import math
import PySimpleGUI as Sg
import platform
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from typing import Tuple, List
from plotly.subplots import make_subplots
from .logger import log as logger


def get_rows_cols(n: int) -> Tuple[int, int]:
    sqrtn = math.sqrt(n)
    fisqrtn = float(int(sqrtn))
    if fisqrtn == sqrtn:
        return int(sqrtn), int(sqrtn)
    if sqrtn - fisqrtn > 0.5:
        return int(sqrtn) + 1, int(sqrtn) + 1
    else:
        return int(sqrtn), int(sqrtn) + 1


def get_row_col(i: int, cols: int) -> Tuple[int, int]:
    row = ((i - 1) // cols) + 1
    col = i - ((row - 1) * cols)
    return row, col


def reorder_dataframe(dataframe, categories, first_category, to_categorize):

    if first_category is None:
        logger.warning(f"None of {to_categorize} were found in the Google Sheets")
    else:
        i_first = int(first_category.split("category_")[1])
        index_first = list(dataframe.columns).index(first_category)

        for cat in categories:
            j = int(cat.split("category_")[1])
            if j <= i_first:
                continue
            subdf = dataframe.loc[dataframe.loc[:, cat].isin(to_categorize)]
            badly_named = subdf.loc[subdf.loc[:, first_category].isin(to_categorize)]
            if len(badly_named) > 0:
                raise ValueError(
                    "In a single table, a category appeared twice at different depths. That should not happen."
                )
            index_cat = list(subdf.columns).index(cat)
            cols = list(subdf.columns)
            cols[index_cat], cols[index_first] = cols[index_first], cols[index_cat]
            subdf.columns = cols
            dataframe.loc[dataframe.loc[:, cat].isin(to_categorize)] = subdf

            subdf = dataframe.loc[~dataframe.loc[:, first_category].isin(to_categorize)]
            subdf.columns = cols
            subdf.loc[:, first_category] = to_categorize[-1]
            dataframe.loc[~dataframe.loc[:, first_category].isin(to_categorize)] = subdf
    return dataframe


def make_figures(dataframe, categories, first_category, dropped: List[str] = None):

    root_path = ["Year", "Month"]
    if dropped is not None:
        for drop in dropped:
            if drop in root_path:
                root_path.remove(drop)
            elif drop in categories:
                categories = categories[:]
                categories.remove(drop)

    first_name = "year"
    if dropped == ["Year"]:
        first_name = "month"
    elif dropped == ["Year", "Month"]:
        first_name = None
    if first_name is not None:
        figs = {
            f"By {first_name}": px.sunburst(
                dataframe, path=root_path + categories, values="total", hover_data=["total"], color="category_1"
            )["data"][0],
        }
    else:
        figs = {}

    for c in categories:
        subdf = dataframe.loc[dataframe.loc[:, c].dropna().index]
        if c == first_category:
            title = "By payers"
        else:
            title = f"By category {c.split('_')[-1]}"
        figs[title] = px.sunburst(
            subdf,
            path=[c] + root_path + [oc for oc in categories if oc != c],
            values="total",
            hover_data=["total"],
            color="category_1",
        )["data"][0]

    rows, cols = get_rows_cols(len(figs))
    final_fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=list(figs.keys()),
        specs=[[{"type": "domain"}] * cols for _ in range(rows)],
        vertical_spacing=0.075,
        horizontal_spacing=0.075,
    )

    for i, fig in enumerate(figs):
        row, col = get_row_col(i + 1, cols)
        final_fig.add_trace(figs[fig], row=row, col=col)

    return final_fig


def graph_plotter(dataframe: pd.DataFrame, output: Path, names: List[str], common: str):
    logger.info("")
    logger.info(f"Plotting general plots...")
    dataframe = dataframe.loc[~np.array([dataframe.loc[s]["category_1"] == "Total" for s in dataframe.index])]
    categories = [c for c in dataframe.columns if "category" in c]
    to_categorize = names + [common]
    first_category = None
    for col in dataframe:
        if any(dataframe[col].isin(to_categorize)):
            first_category = col
            if col == "Year" or col == "Month":
                raise ValueError(f"Malformed Google Sheet : got unexpected value in {col}")
            break
    dataframe = reorder_dataframe(
        dataframe=dataframe, categories=categories, first_category=first_category, to_categorize=to_categorize
    )

    make_figures(dataframe=dataframe, categories=categories, first_category=first_category).write_html(str(output))

    logger.info(f"...all years plotted")

    to_drop = [["Year"], ["Month"], ["Year", "Month"]]
    for drop in to_drop:
        logger.info(f"Plotting each {drop} separately...")
        grpyear = dataframe.groupby(drop)
        for i, (stuff, df) in enumerate(grpyear):
            df = df.drop(drop, axis=1)
            out = Path(str(output.with_suffix("").absolute()) + f"_by_{'_'.join(drop)}")
            if not out.is_dir():
                out.mkdir()
            string_stuff = stuff
            if not isinstance(string_stuff, str):
                string_stuff = '_'.join(stuff)
            make_figures(dataframe=df, categories=categories, first_category=first_category, dropped=drop).write_html(
                str(out / f"{string_stuff}.html")
            )
        logger.info(f"...plotted")


def openfile(afile: Path):
    if afile.suffix == ".html":
        if platform.system() == "Linux":
            os.system(f"sensible-browser {afile} &")
        elif platform.system() == "Darwin":
            os.system(f"open {afile} &")
        elif platform.system() == "Windows":
            os.system(f"start {afile}")
        else:
            raise OSError(f"Unsupported OS {platform.system()}")

    elif (afile.suffix == ".csv" or afile.suffix == ".xlsx") and os.system(f"libreoffice {str(afile)}") != 0:
        Sg.Popup(f"Can not open {afile}. Do you have libreoffice ?")
