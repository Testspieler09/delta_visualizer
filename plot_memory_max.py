import matplotlib.pyplot as plt
from core_models import Group, DatasetRegistry, PlotConfig
from plotting_utils import bytes_to_mb


def plot_memory_max_group(group: Group, registry: DatasetRegistry, config: PlotConfig):
    fig, ax = plt.subplots()

    data = []
    labels = []

    column = "physical_bytes" if config.memory_metric == "physical" else "virtual_bytes"

    for ds_id in group.dataset_ids:
        dataset = registry.get(ds_id)
        values = dataset.raw_df[column].values
        converted = bytes_to_mb(values)

        data.append(converted)
        labels.append(config.label_map.get(ds_id, dataset.display_name))

    ax.boxplot(data, labels=labels)
    ax.set_yscale(config.y_scale)
    ax.set_ylabel("Memory (MB)")
    ax.set_title(group.name)

    return fig
