import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium", app_title="Visualize delta results")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    # TODO: read into a var output_dir via dir
    mo.vstack([mo.ui.file_browser(filetypes=["csv"], selection_mode="directory", multiple=False)])
    return


@app.cell
def _():
    # Read the csv files
    # delta generates the files at memory/ and time/
    return


if __name__ == "__main__":
    app.run()
