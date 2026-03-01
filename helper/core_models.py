from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional
import pandas as pd
import matplotlib as plt


DatasetType = Literal["time", "memory_max", "memory_timeline"]


@dataclass(frozen=True)
class Dataset:
    id: str
    source_path: Path
    display_name: str
    type: DatasetType
    raw_df: pd.DataFrame


@dataclass
class DatasetRegistry:
    datasets: Dict[str, Dataset] = field(default_factory=dict)

    def add(self, dataset: Dataset):
        if dataset.id in self.datasets:
            raise ValueError(f"Dataset id '{dataset.id}' already exists.")
        self.datasets[dataset.id] = dataset

    def get(self, dataset_id: str) -> Dataset:
        return self.datasets[dataset_id]

    def list(self) -> List[Dataset]:
        return list(self.datasets.values())


@dataclass
class Group:
    id: str
    name: str
    dataset_ids: List[str]
    type: DatasetType


@dataclass
class PlotConfig:
    duration_format: Literal["ns", "ms", "s"] = "ms"
    y_scale: Literal["linear", "log"] = "linear"

    memory_metric: Literal["physical", "virtual"] = "physical"
    memory_unit: Literal["bytes", "mb"] = "mb"

    timeline_alignment: Literal["truncate", "interpolate", "per_run"] = "truncate"

    palette: Dict[str, str] = field(default_factory=dict)
    label_map: Dict[str, str] = field(default_factory=dict)

    save_dir: Optional[Path] = None


@dataclass
class AppState:
    registry: DatasetRegistry = field(default_factory=DatasetRegistry)
    groups: Dict[str, Group] = field(default_factory=dict)
    config: PlotConfig = field(default_factory=PlotConfig)

    def is_valid(self) -> bool:
        if self.registry is None or self.registry.list() == []:
            raise ValueError(
                "No data within registry. Please select csv files that contain data to plot somthing meaningfull."
            )
        if self.groups is None or self.groups == {}:
            raise ValueError("No groups present that could be plotted")
        if self.config is None:
            raise ValueError("Plotconfig was not set")

        return True

    def plot_all(self) -> List[plt.figure.Figure]:
        from helper.plotting.plot_dispatcher import plot_group

        plots = []
        for i, g in enumerate(self.groups.values()):
            plot = plot_group(g, self.registry, self.config)
            plots.append(plot)

            if self.config.save_dir is not None:
                file_path = self.config.save_dir / f"plot_{g.name}_{i}.png"
                plot.savefig(file_path, bbox_inches="tight")

        return plots

    @staticmethod
    def close_all_plots(plots: plt.figure.Figure) -> None:
        for p in plots:
            plt.close(p)
