# Delta ($\Delta$) Visualizer

> [!NOTE]
>
> This tool is designed to work with the output of [Delta](https://github.com/Testspieler09/delta) ($\Delta$).

An interactive **marimo notebook** for data visualization, managed with **uv** for fast, reproducible Python environments.

This project is designed to be run as a live, reactive notebook rather than a static script or report.

## Requirements

* Python 3.10+
* [`uv`](https://github.com/astral-sh/uv)
* [`marimo`](https://marimo.io)

## Setup

Clone the repository and install dependencies using `uv`:

```bash
uv sync
```

This will create a virtual environment and install all dependencies exactly as locked in `uv.lock`.

## Running the notebook

Start the marimo app with:

```bash
uv run marimo run visualize.py
```

This launches an interactive UI in your browser.

Marimo will:

* execute cells reactively
* persist layout state
* render tables, charts, and callouts inline

## Layouts

The `layouts/visualize.grid.json` file stores a saved marimo layout (cell positions, visibility, etc.).

Marimo will automatically pick this up when opening the notebook, allowing consistent presentation across runs.

## Why marimo?

Marimo combines the strengths of notebooks and apps:

* Reactive execution (no hidden state)
* UI components as first-class values
* Reproducible layouts
* Scriptable, version-controlled notebooks

This makes it ideal for exploratory analysis that needs to stay maintainable.

## Why uv?

`uv` provides:

* Extremely fast dependency resolution
* Deterministic environments via `uv.lock`
* No manual virtualenv management

Together with marimo, this keeps the workflow tight and reproducible.
## License

This project is licensed under the terms of the license in `LICENSE`.
