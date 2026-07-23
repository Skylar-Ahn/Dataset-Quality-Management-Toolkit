from collections import Counter, defaultdict
from dataclasses import dataclass
import csv
from pathlib import Path

from dq_toolkit.io.coco import CocoDataset


@dataclass
class ClassDistributionRow:
    category_id: int
    category_name: str
    instance_count: int
    image_count: int
    instance_ratio: float
    image_ratio: float


def analyze_class_distribution(
    coco_dataset: CocoDataset,
) -> list[ClassDistributionRow]:
    """
    Analyze class distribution in a COCO-format dataset.

    This function counts:
    - how many object instances exist per category
    - how many images contain each category
    - the ratio of each category over total instances/images
    """
    category_id_to_name = {
        category["id"]: category["name"]
        for category in coco_dataset.categories
        if "id" in category and "name" in category
    }

    instance_counts: Counter[int] = Counter()
    category_to_image_ids: dict[int, set[int]] = defaultdict(set)

    for annotation in coco_dataset.annotations:
        category_id = annotation.get("category_id")
        image_id = annotation.get("image_id")

        if category_id not in category_id_to_name:
            continue

        instance_counts[category_id] += 1

        if isinstance(image_id, int):
            category_to_image_ids[category_id].add(image_id)

    total_instances = sum(instance_counts.values())
    total_images = len(coco_dataset.images)

    rows: list[ClassDistributionRow] = []

    for category_id, category_name in category_id_to_name.items():
        instance_count = instance_counts[category_id]
        image_count = len(category_to_image_ids[category_id])

        instance_ratio = (
            instance_count / total_instances
            if total_instances > 0
            else 0.0
        )
        image_ratio = (
            image_count / total_images
            if total_images > 0
            else 0.0
        )

        rows.append(
            ClassDistributionRow(
                category_id=category_id,
                category_name=category_name,
                instance_count=instance_count,
                image_count=image_count,
                instance_ratio=instance_ratio,
                image_ratio=image_ratio,
            )
        )

    rows.sort(key=lambda row: row.instance_count, reverse=True)

    return rows


def save_class_distribution_csv(
    rows: list[ClassDistributionRow],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category_id",
                "category_name",
                "instance_count",
                "image_count",
                "instance_ratio",
                "image_ratio",
            ],
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "instance_count": row.instance_count,
                    "image_count": row.image_count,
                    "instance_ratio": round(row.instance_ratio, 6),
                    "image_ratio": round(row.image_ratio, 6),
                }
            )