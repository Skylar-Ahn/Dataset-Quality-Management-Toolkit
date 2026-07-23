from collections import Counter
from dataclasses import dataclass

from dq_toolkit.io.coco import CocoDataset


@dataclass
class CategoryIssue:
    check_name: str
    severity: str
    annotation_id: int | None
    image_id: int | None
    category_id: int | None
    message: str


def validate_categories(coco_dataset: CocoDataset) -> list[CategoryIssue]:
    """
    Validate category-related consistency in a COCO-format dataset.

    Main checks:
    - duplicate category ids
    - duplicate category names
    - missing category_id in annotations
    - annotations referencing unknown category ids
    """
    issues: list[CategoryIssue] = []

    category_ids = [category.get("id") for category in coco_dataset.categories]
    category_names = [category.get("name") for category in coco_dataset.categories]

    category_id_counts = Counter(category_ids)
    category_name_counts = Counter(category_names)

    valid_category_ids = {
        category["id"]
        for category in coco_dataset.categories
        if "id" in category
    }

    for category_id, count in category_id_counts.items():
        if category_id is None:
            issues.append(
                CategoryIssue(
                    check_name="category_id_missing",
                    severity="error",
                    annotation_id=None,
                    image_id=None,
                    category_id=None,
                    message="A category entry is missing the 'id' field.",
                )
            )
        elif count > 1:
            issues.append(
                CategoryIssue(
                    check_name="category_id_duplicate",
                    severity="error",
                    annotation_id=None,
                    image_id=None,
                    category_id=category_id,
                    message=f"Duplicate category id found: {category_id}",
                )
            )

    for category_name, count in category_name_counts.items():
        if category_name is None:
            issues.append(
                CategoryIssue(
                    check_name="category_name_missing",
                    severity="warning",
                    annotation_id=None,
                    image_id=None,
                    category_id=None,
                    message="A category entry is missing the 'name' field.",
                )
            )
        elif count > 1:
            issues.append(
                CategoryIssue(
                    check_name="category_name_duplicate",
                    severity="warning",
                    annotation_id=None,
                    image_id=None,
                    category_id=None,
                    message=f"Duplicate category name found: {category_name}",
                )
            )

    for annotation in coco_dataset.annotations:
        annotation_id = annotation.get("id")
        image_id = annotation.get("image_id")

        if "category_id" not in annotation:
            issues.append(
                CategoryIssue(
                    check_name="annotation_category_id_missing",
                    severity="error",
                    annotation_id=annotation_id,
                    image_id=image_id,
                    category_id=None,
                    message="Annotation is missing the 'category_id' field.",
                )
            )
            continue

        category_id = annotation["category_id"]

        if category_id not in valid_category_ids:
            issues.append(
                CategoryIssue(
                    check_name="annotation_unknown_category_id",
                    severity="error",
                    annotation_id=annotation_id,
                    image_id=image_id,
                    category_id=category_id,
                    message=(
                        f"Annotation references an unknown category_id: "
                        f"{category_id}"
                    ),
                )
            )

    return issues