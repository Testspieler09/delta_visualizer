import pandas as pd
from pathlib import Path
from typing import List
import uuid

from core_models import Dataset, DatasetType


TIME_COLUMNS = {"run_index", "duration_ns"}
MEMORY_MAX_COLUMNS = {"run_index", "physical_bytes", "virtual_bytes"}
MEMORY_TIMELINE_COLUMNS = {
    "run_index",
    "timestamp_ms",
    "physical_bytes",
    "virtual_bytes",
}


def detect_dataset_type(df: pd.DataFrame) -> DatasetType:
    cols = set(df.columns)

    if cols == TIME_COLUMNS:
        return "time"

    if cols == MEMORY_MAX_COLUMNS:
        return "memory_max"

    if cols == MEMORY_TIMELINE_COLUMNS:
        return "memory_timeline"

    raise ValueError("Invalid CSV schema.")


def discover_csv_files(root: Path) -> List[Path]:
    return list(root.rglob("*.csv"))


def load_dataset(path: Path) -> Dataset:
    df = pd.read_csv(path)

    dataset_type = detect_dataset_type(df)

    return Dataset(
        id=str(uuid.uuid4()),
        source_path=path,
        display_name=path.name,
        type=dataset_type,
        raw_df=df.copy(deep=True),
    )
