import matplotlib.pyplot as plt
from core_models import Group, DatasetRegistry, PlotConfig
from plotting_utils import convert_duration


def plot_time_group(group: Group, registry: DatasetRegistry, config: PlotConfig):
    fig, ax = plt.subplots()

    data = []
    labels = []

    for ds_id in group.dataset_ids:
        dataset = registry.get(ds_id)
        durations = dataset.raw_df["duration_ns"].values
        converted = convert_duration(durations, config.duration_format)

        data.append(converted)
        labels.append(config.label_map.get(ds_id, dataset.display_name))

    ax.boxplot(data, labels=labels)

    ax.set_yscale(config.y_scale)
    ax.set_ylabel(f"Duration ({config.duration_format})")
    ax.set_title(group.name)

    return fig
