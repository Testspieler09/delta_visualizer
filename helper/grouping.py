from typing import List
from core_models import DatasetRegistry, Group, DatasetType
import uuid


def create_group(
    registry: DatasetRegistry,
    name: str,
    dataset_ids: List[str],
) -> Group:
    if not dataset_ids:
        raise ValueError("Group must contain at least one dataset.")

    dataset_types: set[DatasetType] = {
        registry.get(ds_id).type for ds_id in dataset_ids
    }

    if len(dataset_types) != 1:
        raise ValueError("All datasets in a group must share the same type.")

    group_type = dataset_types.pop()

    return Group(
        id=str(uuid.uuid4()),
        name=name,
        dataset_ids=dataset_ids,
        type=group_type,
    )
