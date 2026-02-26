import marimo

__generated_with = "0.20.2"
app = marimo.App(
    width="medium",
    app_title="Visualize delta results",
    layout_file="layouts/visualize.grid.json",
)


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    from pathlib import Path

    return Path, mo, np, pd


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


@app.cell(hide_code=True)
def _(DEFAULT_PALETTE, np, os, pd, plt, sns):
    DURATION_FORMATS = {
        "ns": 1,
        "ms": 1_000_000,
        "s": 1_000_000_000,
    }
    SCALES = ["linear", "log"]
    FIGSIZE = (10, 6)

    def load_benchmark_directory(root_dir):
        """
        Loads all CSV files from:
            root_dir/
                memory/
                time/

        Returns:
            {
                "memory": { task: { lang: [dfs] } },
                "time": { task: { lang: [dfs] } }
            }
        """

        data = {"memory": {}, "time": {}}

        for root, _, files in os.walk(root_dir):
            for f in files:
                if not f.endswith(".csv"):
                    continue

                full_path = os.path.join(root, f)
                df = pd.read_csv(full_path)

                task_name = os.path.splitext(f)[0]
                lang = os.path.basename(os.path.dirname(full_path))

                # Detect type by columns
                if {"timestamp_ms", "physical_bytes"}.issubset(df.columns):
                    kind = "memory"
                elif "duration_ns" in df.columns:
                    kind = "time"
                else:
                    continue

                data[kind].setdefault(task_name, {}).setdefault(lang, []).append(df)

        return data

    def aggregate_memory_runs(dfs):
        """
        If multiple runs exist → return mean timeline.
        """
        if len(dfs) == 1:
            df = dfs[0].copy()
            df["timestamp_ms"] -= df["timestamp_ms"].iloc[0]
            df["physical_mb"] = df["physical_bytes"] / (1024 * 1024)
            return df[["timestamp_ms", "physical_mb"]]

        aligned = []
        min_len = min(len(df) for df in dfs)

        for df in dfs:
            df = df.copy()
            df["timestamp_ms"] -= df["timestamp_ms"].iloc[0]
            df["physical_mb"] = df["physical_bytes"] / (1024 * 1024)
            aligned.append(df["physical_mb"].iloc[:min_len].values)

        stacked = np.stack(aligned)
        mean_vals = np.mean(stacked, axis=0)
        timestamps = dfs[0]["timestamp_ms"].iloc[:min_len].values

        return pd.DataFrame({"timestamp_ms": timestamps, "physical_mb": mean_vals})

    def maybe_save(fig, save_dir, filename, overwrite):
        if save_dir is None:
            return

        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)

        if os.path.exists(path) and not overwrite:
            print(f"Skipping existing file: {path}")
            return

        fig.savefig(path, bbox_inches="tight")
        print(f"Saved: {path}")

    def plot_memory_task(
        task,
        task_data,
        save_dir=None,
        overwrite=False,
    ):
        fig, ax = plt.subplots(figsize=FIGSIZE)

        for lang, dfs in task_data.items():
            agg_df = aggregate_memory_runs(dfs)
            ax.plot(
                agg_df["timestamp_ms"],
                agg_df["physical_mb"],
                label=lang,
                color=DEFAULT_PALETTE.get(lang),
            )

        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Physical Memory (MB)")
        ax.set_title(f"{task} - Memory Usage")
        ax.legend()
        ax.grid(True)

        maybe_save(
            fig,
            save_dir,
            f"{task}_memory_line.png",
            overwrite,
        )

        plt.show()
        plt.close(fig)

    def plot_time_task(
        task,
        task_data,
        duration_format="ms",
        scale="linear",
        save_dir=None,
        overwrite=False,
    ):
        multiplier = DURATION_FORMATS[duration_format]

        rows = []

        for lang, dfs in task_data.items():
            for df in dfs:
                if "duration_ns" not in df.columns:
                    continue

                for val in df["duration_ns"]:
                    rows.append({"lang": lang, "duration": val / multiplier})

        plot_df = pd.DataFrame(rows)

        fig, ax = plt.subplots(figsize=FIGSIZE)

        sns.boxplot(
            data=plot_df, x="lang", y="duration", palette=DEFAULT_PALETTE, ax=ax
        )

        ax.set_yscale(scale)
        ax.set_xlabel("Language")
        ax.set_ylabel(f"Duration ({duration_format})")
        ax.set_title(f"{task} - Execution Time")
        ax.grid(True, axis="y", linestyle="--", alpha=0.6)

        maybe_save(
            fig,
            save_dir,
            f"{task}_time_boxplot_{duration_format}_{scale}.png",
            overwrite,
        )

        plt.show()
        plt.close(fig)

    def plot_all_tasks(
        root_dir,
        duration_format="ms",
        scale="linear",
        save_dir=None,
        overwrite=False,
    ):
        data = load_benchmark_directory(root_dir)

        for task, task_data in data["memory"].items():
            plot_memory_task(
                task,
                task_data,
                save_dir,
                overwrite,
            )

        for task, task_data in data["time"].items():
            plot_time_task(
                task,
                task_data,
                duration_format,
                scale,
                save_dir,
                overwrite,
            )

    return


if __name__ == "__main__":
    app.run()
