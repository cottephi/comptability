# plotter.py
import os
import math
import platform
import pandas as pd
import numpy as np
import plotly.express as px
from typing import Tuple
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
    row = ((i-1) // cols) + 1
    col = i - ((row-1) * cols)
    return row, col


def graph_plotter(dataframe: pd.DataFrame, output: str):
    logger.info("")
    logger.info(f"Plotting years...")
    dataframe = dataframe.loc[~np.array([dataframe.loc[s]["category_1"] == "Total" for s in dataframe.index])]
    categories = [c for c in dataframe.columns if "category" in c]
    figs = {"By year": px.sunburst(
        dataframe,
        path=['Year', 'Month'] + categories,
        values='total',
        hover_data=["total"],
        color="category_1"
    )["data"][0]}
    for c in categories:
        subdf = dataframe.loc[dataframe.loc[:, c].dropna().index]
        figs[f"By category {c.split('_')[-1]}"] = px.sunburst(
            subdf,
            path=[c, 'Year', 'Month'] + [oc for oc in categories if oc != c],
            values='total',
            hover_data=["total"],
            color="category_1"
        )["data"][0]

    rows, cols = get_rows_cols(len(figs))
    final_fig = make_subplots(rows=rows, cols=cols, subplot_titles=list(figs.keys()),
                              specs=[[{"type": "domain"}] * cols for _ in range(rows)])

    for i, fig in enumerate(figs):
        row, col = get_row_col(i+1, cols)
        final_fig.add_trace(figs[fig], row=row, col=col)

    final_fig.write_html(output)
    logger.info(f"...all years plotted")
    if platform.system() == "Linux":
        os.system(f"sensible-browser {output} &")
    elif platform.system() == "Darwin":
        os.system(f"open {output} &")
    elif platform.system() == "Windows":
        os.system(f"start {output}")
    else:
        raise OSError(f"Unsupported OS {platform.system()}")
