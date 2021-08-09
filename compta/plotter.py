# plotter.py
import os
import platform
import pandas as pd
import numpy as np
import plotly.express as px
from .logger import log as logger


def graph_plotter(dataframe: pd.DataFrame, output: str):
    logger.info("")
    logger.info(f"Plotting years...")
    dataframe = dataframe.loc[~np.array([dataframe.loc[s]["category_1"] == "Total" for s in dataframe.index])]
    categories = [c for c in dataframe.columns if "category" in c]
    fig = px.sunburst(
        dataframe,
        path=['Year', 'Month'] + categories,
        values='total',
        hover_data=["total"],
        color="category_1"
    )
    fig.write_html(output)
    logger.info(f"...all years plotted")
    if platform.system() == "Linux":
        os.system(f"sensible-browser {output} &")
    elif platform.system() == "Darwin":
        os.system(f"open {output} &")
    elif platform.system() == "Windows":
        os.system(f"start {output}")
    else:
        raise OSError(f"Unsupported OS {platform.system()}")
