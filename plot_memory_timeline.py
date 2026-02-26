import matplotlib.pyplot as plt
from plotting_utils import bytes_to_mb


def plot_memory_timeline_group(group, registry, config):
    fig, ax = plt.subplots()

    column = "physical_bytes" if config.memory_metric == "physical" else "virtual_bytes"

    for ds_id in group.dataset_ids:
        dataset = registry.get(ds_id)
        df = dataset.raw_df

        for run_id, run_df in df.groupby("run_index"):
            x = run_df["timestamp_ms"].values
            y = bytes_to_mb(run_df[column].values)

            label = config.label_map.get(ds_id, dataset.display_name)

            if config.timeline_alignment == "per_run":
                ax.plot(x, y, alpha=0.4, label=f"{label} (run {run_id})")
            else:
                ax.plot(x, y, alpha=0.7, label=label)

    ax.set_ylabel("Memory (MB)")
    ax.set_xlabel("Time (ms)")
    ax.set_title(group.name)
    ax.set_yscale(config.y_scale)

    return fig
