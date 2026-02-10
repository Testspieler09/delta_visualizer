import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium", app_title="Visualize delta results")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    from pathlib import Path

    return Path, mo, pd


@app.cell(hide_code=True)
def _(mo):
    output_dir_browser = mo.ui.file_browser(
        label="Select benchmark output/ directory",
        selection_mode="directory",
        multiple=False,
    ).form()

    output_dir_browser
    return (output_dir_browser,)


@app.cell(hide_code=True)
def _(Path, output_dir_browser, pd):
    memory_dfs = {}
    time_dfs = {}

    warnings = []

    if (
        output_dir_browser.value is None
        or output_dir_browser.value == ()
        or output_dir_browser.value[0].path == ()
    ):
        warnings.append("No output directory selected.")
    else:
        output_dir = Path(output_dir_browser.value[0].path)

        memory_dir = output_dir / "memory"
        time_dir = output_dir / "time"

        # Load memory CSVs
        if memory_dir.exists():
            for csv_path in memory_dir.rglob("*.csv"):
                try:
                    memory_dfs[csv_path.name] = pd.read_csv(csv_path)
                except Exception as e:
                    warnings.append(f"Failed to load {csv_path}: {e}")
        else:
            warnings.append(f"Missing directory: {memory_dir}")

        # Load time CSVs
        if time_dir.exists():
            for csv_path in time_dir.rglob("*.csv"):
                try:
                    time_dfs[csv_path.name] = pd.read_csv(csv_path)
                except Exception as e:
                    warnings.append(f"Failed to load {csv_path}: {e}")
        else:
            warnings.append(f"Missing directory: {time_dir}")
    return memory_dfs, time_dfs, warnings


@app.cell(hide_code=True)
def _(mo, warnings):
    if warnings:
        warning_str = "Visualization could not be created:\n\n" + "\n".join(
            f"- {w}" for w in warnings
        )
        output = mo.callout(
            mo.plain_text(warning_str),
            kind="warn",
        )
    else:
        output = mo.callout(
            "Successfully loaded benchmark data",
            kind="success",
        )

    output
    return


@app.cell(hide_code=True)
def _(memory_dfs, mo):
    mo.carousel(
        [
            mo.vstack(
                [
                    mo.md(f"### {key}"),
                    value,
                ]
            )
            for key, value in memory_dfs.items()
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo, time_dfs):
    mo.carousel(
        [
            mo.vstack(
                [
                    mo.md(f"### {key}"),
                    value,
                ]
            )
            for key, value in time_dfs.items()
        ]
    )
    return


if __name__ == "__main__":
    app.run()
