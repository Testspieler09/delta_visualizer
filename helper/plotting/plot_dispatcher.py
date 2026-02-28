from core_models import Group, DatasetRegistry, PlotConfig
from plot_time import plot_time_group
from plot_memory_max import plot_memory_max_group
from plot_memory_timeline import plot_memory_timeline_group


def plot_group(group: Group, registry: DatasetRegistry, config: PlotConfig):
    if group.type == "time":
        return plot_time_group(group, registry, config)

    if group.type == "memory_max":
        return plot_memory_max_group(group, registry, config)

    if group.type == "memory_timeline":
        return plot_memory_timeline_group(group, registry, config)

    raise ValueError("Unsupported group type")
