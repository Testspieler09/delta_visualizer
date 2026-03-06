import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plotting_utils import bytes_to_mb


def plot_memory_timeline_group(group, registry, config):
    fig, ax = plt.subplots()

    dataset_ids = group.dataset_ids
    colors = _stable_color_mapping(dataset_ids, config.palette)

    for ds_id in dataset_ids:
        dataset = registry.get(ds_id)

        # no mutation
        df = dataset.raw_df.copy(deep=False)

        value_col = _select_memory_column(config.memory_metric)

        display_name = config.label_map.get(ds_id, dataset.display_name)

        color = colors[ds_id]

        # ----------------------------
        # TRUNCATE / INTERPOLATE
        # ----------------------------
        if config.timeline_alignment in ("truncate", "interpolate"):
            if config.timeline_alignment == "truncate":
                aligned = _truncate_alignment(df, value_col)
            else:
                aligned = _interpolate_alignment(df, value_col)

            x = aligned["timestamp_ms"].values
            y = _convert_memory(aligned[value_col].values, config.memory_unit)

            ax.plot(
                x,
                y,
                label=display_name,
                color=color,
                alpha=0.7,
            )

        # ----------------------------
        # PER RUN
        # ----------------------------
        elif config.timeline_alignment == "per_run":
            first = True

            for _, run_df in _per_run_data(df):
                x = run_df["timestamp_ms"].values
                y = _convert_memory(run_df[value_col].values, config.memory_unit)

                ax.plot(
                    x,
                    y,
                    color=color,
                    alpha=0.4,
                    label=display_name if first else None,
                )
                first = False

        else:
            raise ValueError("Invalid timeline_alignment")

    # ----------------------------
    # Axis configuration
    # ----------------------------
    ax.set_xlabel("Time (ms)")

    if config.memory_unit == "mb":
        ax.set_ylabel("Memory (MB)")
    else:
        ax.set_ylabel("Memory (bytes)")

    ax.set_title(group.name)
    ax.set_yscale(config.y_scale)

    ax.legend(title=config.legend_title)
    fig.tight_layout()

    return fig


def _convert_memory(values, unit: str):
    if unit == "bytes":
        return values
    if unit == "mb":
        return bytes_to_mb(values)
    raise ValueError(f"Unsupported memory_unit: {unit}")


def _select_memory_column(metric: str) -> str:
    if metric == "physical":
        return "physical_bytes"
    if metric == "virtual":
        return "virtual_bytes"
    raise ValueError(f"Unsupported memory_metric: {metric}")


def _aggregate_mean(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    return (
        df.groupby("timestamp_ms", as_index=False)[value_col]
        .mean()
        .sort_values("timestamp_ms")
    )


def _truncate_alignment(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    # max timestamp per run
    max_per_run = df.groupby("run_index")["timestamp_ms"].max()

    # shared cutoff
    shared_max = max_per_run.min()

    truncated = df[df["timestamp_ms"] <= shared_max]

    return _aggregate_mean(truncated, value_col)


def _interpolate_alignment(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    runs = []

    min_per_run = df.groupby("run_index")["timestamp_ms"].min()
    max_per_run = df.groupby("run_index")["timestamp_ms"].max()

    start = min_per_run.max()
    end = max_per_run.min()

    if start >= end:
        raise ValueError("No overlapping timeline range for interpolation.")

    # Common grid = union of timestamps inside overlap
    grid = df[(df["timestamp_ms"] >= start) & (df["timestamp_ms"] <= end)][
        "timestamp_ms"
    ].unique()

    grid = np.sort(grid)

    for _, run_df in df.groupby("run_index"):
        run_df = run_df.sort_values("timestamp_ms")

        run_df = run_df[
            (run_df["timestamp_ms"] >= start) & (run_df["timestamp_ms"] <= end)
        ]

        run_df = run_df.set_index("timestamp_ms")

        reindexed = (
            run_df[[value_col]].reindex(grid).interpolate(method="linear").reset_index()
        )

        runs.append(reindexed)

    combined = pd.concat(runs, ignore_index=True)

    return _aggregate_mean(combined, value_col)


def _per_run_data(df: pd.DataFrame):
    for run_id, run_df in df.groupby("run_index"):
        yield run_id, run_df.sort_values("timestamp_ms")


def _stable_color_mapping(dataset_ids: list[str], palette: dict[str, str]):
    colors = {}
    default_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for i, ds_id in enumerate(sorted(dataset_ids)):
        if ds_id in palette:
            colors[ds_id] = palette[ds_id]
        else:
            colors[ds_id] = default_cycle[i % len(default_cycle)]

    return colors
