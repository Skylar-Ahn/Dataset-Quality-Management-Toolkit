import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CocoDataset:
    images: list[dict]
    annotations: list[dict]
    categories: list[dict]

    @property
    def image_id_to_image(self) -> dict[int, dict]:
        return {image["id"]: image for image in self.images}

    @property
    def category_id_to_category(self) -> dict[int, dict]:
        return {category["id"]: category for category in self.categories}


def load_coco_annotation(annotation_path: str | Path) -> CocoDataset:
    annotation_path = Path(annotation_path)

    if not annotation_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotation_path}")

    with annotation_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = ["images", "annotations", "categories"]
    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        raise ValueError(f"Missing required COCO keys: {missing_keys}")

    return CocoDataset(
        images=data["images"],
        annotations=data["annotations"],
        categories=data["categories"],
    )


def summarize_coco_dataset(
    coco_dataset: CocoDataset,
    image_dir: str | Path | None = None,
) -> dict:
    summary = {
        "num_images": len(coco_dataset.images),
        "num_annotations": len(coco_dataset.annotations),
        "num_categories": len(coco_dataset.categories),
    }

    if image_dir is not None:
        image_dir = Path(image_dir)

        missing_images = []
        for image in coco_dataset.images:
            image_path = image_dir / image["file_name"]
            if not image_path.exists():
                missing_images.append(image["file_name"])

        summary["num_missing_images"] = len(missing_images)
        summary["missing_images"] = missing_images

    return summary
