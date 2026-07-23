from collections import Counter
from dataclasses import dataclass
import csv
from math import isfinite
from pathlib import Path
from statistics import mean, median

from dq_toolkit.io.coco import CocoDataset


SMALL_AREA_THRESHOLD = 32 * 32
MEDIUM_AREA_THRESHOLD = 96 * 96


@dataclass
class BBoxDistributionRow:
    annotation_id: int | None
    image_id: int | None
    category_id: int | None
    category_name: str | None
    bbox_width: float
    bbox_height: float
    bbox_area: float
    normalized_area: float | None
    aspect_ratio: float
    size_bin: str


def classify_bbox_size(bbox_area: float) -> str:
    """
    Classify bbox size into small / medium / large.

    The thresholds are commonly used in object detection analysis:
    - small: area < 32^2
    - medium: 32^2 <= area < 96^2
    - large: area >= 96^2
    """
    if bbox_area < SMALL_AREA_THRESHOLD:
        return "small"

    if bbox_area < MEDIUM_AREA_THRESHOLD:
        return "medium"

    return "large"


def _is_valid_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _is_valid_bbox(bbox: object) -> bool:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False

    if not all(_is_valid_number(value) for value in bbox):
        return False

    _, _, width, height = bbox

    return width > 0 and height > 0


def analyze_bbox_distribution(
    coco_dataset: CocoDataset,
) -> list[BBoxDistributionRow]:
    """
    Analyze bbox size and aspect ratio distribution in a COCO-format dataset.

    This function assumes COCO bbox format:
        [x_min, y_min, width, height]
    """
    category_id_to_name = {
        category["id"]: category["name"]
        for category in coco_dataset.categories
        if "id" in category and "name" in category
    }

    image_id_to_image = coco_dataset.image_id_to_image

    rows: list[BBoxDistributionRow] = []

    for annotation in coco_dataset.annotations:
        bbox = annotation.get("bbox")

        if not _is_valid_bbox(bbox):
            continue

        _, _, bbox_width, bbox_height = bbox

        bbox_area = bbox_width * bbox_height
        aspect_ratio = bbox_width / bbox_height
        size_bin = classify_bbox_size(bbox_area)

        image_id = annotation.get("image_id")
        image = image_id_to_image.get(image_id)

        normalized_area: float | None = None

        if image is not None:
            image_width = image.get("width")
            image_height = image.get("height")

            if _is_valid_number(image_width) and _is_valid_number(image_height):
                image_area = image_width * image_height

                if image_area > 0:
                    normalized_area = bbox_area / image_area

        category_id = annotation.get("category_id")
        category_name = category_id_to_name.get(category_id)

        rows.append(
            BBoxDistributionRow(
                annotation_id=annotation.get("id"),
                image_id=image_id,
                category_id=category_id,
                category_name=category_name,
                bbox_width=bbox_width,
                bbox_height=bbox_height,
                bbox_area=bbox_area,
                normalized_area=normalized_area,
                aspect_ratio=aspect_ratio,
                size_bin=size_bin,
            )
        )

    return rows


def summarize_bbox_distribution(
    rows: list[BBoxDistributionRow],
) -> dict:
    """
    Summarize bbox distribution rows into aggregate statistics.
    """
    if not rows:
        return {
            "total_bboxes": 0,
            "size_counts": {},
            "area": {},
            "normalized_area": {},
            "aspect_ratio": {},
        }

    bbox_areas = [row.bbox_area for row in rows]
    aspect_ratios = [row.aspect_ratio for row in rows]
    normalized_areas = [
        row.normalized_area
        for row in rows
        if row.normalized_area is not None
    ]

    size_counts = Counter(row.size_bin for row in rows)

    summary = {
        "total_bboxes": len(rows),
        "size_counts": dict(size_counts),
        "area": {
            "min": min(bbox_areas),
            "max": max(bbox_areas),
            "mean": mean(bbox_areas),
            "median": median(bbox_areas),
        },
        "aspect_ratio": {
            "min": min(aspect_ratios),
            "max": max(aspect_ratios),
            "mean": mean(aspect_ratios),
            "median": median(aspect_ratios),
        },
        "normalized_area": {},
    }

    if normalized_areas:
        summary["normalized_area"] = {
            "min": min(normalized_areas),
            "max": max(normalized_areas),
            "mean": mean(normalized_areas),
            "median": median(normalized_areas),
        }

    return summary


def save_bbox_distribution_csv(
    rows: list[BBoxDistributionRow],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "annotation_id",
                "image_id",
                "category_id",
                "category_name",
                "bbox_width",
                "bbox_height",
                "bbox_area",
                "normalized_area",
                "aspect_ratio",
                "size_bin",
            ],
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "annotation_id": row.annotation_id,
                    "image_id": row.image_id,
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "bbox_width": round(row.bbox_width, 6),
                    "bbox_height": round(row.bbox_height, 6),
                    "bbox_area": round(row.bbox_area, 6),
                    "normalized_area": (
                        round(row.normalized_area, 8)
                        if row.normalized_area is not None
                        else None
                    ),
                    "aspect_ratio": round(row.aspect_ratio, 6),
                    "size_bin": row.size_bin,
                }
            )