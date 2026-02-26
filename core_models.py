from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal
import pandas as pd


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

    timeline_alignment: Literal["truncate", "interpolate", "per_run"] = "truncate"

    palette: Dict[str, str] = field(default_factory=dict)
    label_map: Dict[str, str] = field(default_factory=dict)


@dataclass
class AppState:
    registry: DatasetRegistry = field(default_factory=DatasetRegistry)
    groups: Dict[str, Group] = field(default_factory=dict)
    config: PlotConfig = field(default_factory=PlotConfig)
