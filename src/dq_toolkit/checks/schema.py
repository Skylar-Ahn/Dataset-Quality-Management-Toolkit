from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class SchemaIssue:
    check_name: str
    severity: str
    location: str
    message: str


def _is_int(value: object) -> bool:
    """
    bool is a subclass of int in Python.
    So we explicitly exclude bool.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def _is_positive_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _find_duplicate_int_values(values: list[object]) -> list[int]:
    valid_int_values = [value for value in values if _is_int(value)]
    counts = Counter(valid_int_values)
    return [value for value, count in counts.items() if count > 1]


def validate_coco_schema(annotation_path: str | Path) -> list[SchemaIssue]:
    """
    Validate the basic schema of a COCO-format annotation JSON.

    This function checks whether the JSON has the minimum structure required
    to be handled as a COCO object detection dataset.
    """
    annotation_path = Path(annotation_path)
    issues: list[SchemaIssue] = []

    if not annotation_path.exists():
        return [
            SchemaIssue(
                check_name="annotation_file_missing",
                severity="error",
                location=str(annotation_path),
                message="Annotation JSON file does not exist.",
            )
        ]

    try:
        with annotation_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as error:
        return [
            SchemaIssue(
                check_name="json_decode_error",
                severity="error",
                location=str(annotation_path),
                message=f"Failed to parse JSON file: {error}",
            )
        ]

    if not isinstance(data, dict):
        return [
            SchemaIssue(
                check_name="top_level_type",
                severity="error",
                location="root",
                message="COCO annotation must be a JSON object.",
            )
        ]

    required_top_level_keys = ["images", "annotations", "categories"]

    for key in required_top_level_keys:
        if key not in data:
            issues.append(
                SchemaIssue(
                    check_name="top_level_key_missing",
                    severity="error",
                    location="root",
                    message=f"Missing top-level key: {key}",
                )
            )

    for key in required_top_level_keys:
        if key in data and not isinstance(data[key], list):
            issues.append(
                SchemaIssue(
                    check_name="top_level_key_type",
                    severity="error",
                    location=f"root.{key}",
                    message=f"Top-level key '{key}' must be a list.",
                )
            )

    images = data.get("images", [])
    annotations = data.get("annotations", [])
    categories = data.get("categories", [])

    if isinstance(images, list):
        issues.extend(_validate_images_schema(images))

    if isinstance(annotations, list):
        issues.extend(_validate_annotations_schema(annotations))

    if isinstance(categories, list):
        issues.extend(_validate_categories_schema(categories))

    return issues


def _validate_images_schema(images: list[object]) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []
    image_ids: list[object] = []

    for index, image in enumerate(images):
        location = f"images[{index}]"

        if not isinstance(image, dict):
            issues.append(
                SchemaIssue(
                    check_name="image_item_type",
                    severity="error",
                    location=location,
                    message="Each image entry must be a JSON object.",
                )
            )
            continue

        image_id = image.get("id")
        image_ids.append(image_id)

        if "id" not in image:
            issues.append(
                SchemaIssue(
                    check_name="image_id_missing",
                    severity="error",
                    location=location,
                    message="Image entry is missing 'id'.",
                )
            )
        elif not _is_int(image_id):
            issues.append(
                SchemaIssue(
                    check_name="image_id_type",
                    severity="error",
                    location=f"{location}.id",
                    message=f"Image id must be an integer. Got: {image_id}",
                )
            )

        file_name = image.get("file_name")

        if "file_name" not in image:
            issues.append(
                SchemaIssue(
                    check_name="image_file_name_missing",
                    severity="error",
                    location=location,
                    message="Image entry is missing 'file_name'.",
                )
            )
        elif not isinstance(file_name, str) or not file_name:
            issues.append(
                SchemaIssue(
                    check_name="image_file_name_type",
                    severity="error",
                    location=f"{location}.file_name",
                    message=f"Image file_name must be a non-empty string. Got: {file_name}",
                )
            )

        width = image.get("width")
        height = image.get("height")

        if "width" not in image:
            issues.append(
                SchemaIssue(
                    check_name="image_width_missing",
                    severity="error",
                    location=location,
                    message="Image entry is missing 'width'.",
                )
            )
        elif not _is_positive_number(width):
            issues.append(
                SchemaIssue(
                    check_name="image_width_value",
                    severity="error",
                    location=f"{location}.width",
                    message=f"Image width must be a positive number. Got: {width}",
                )
            )

        if "height" not in image:
            issues.append(
                SchemaIssue(
                    check_name="image_height_missing",
                    severity="error",
                    location=location,
                    message="Image entry is missing 'height'.",
                )
            )
        elif not _is_positive_number(height):
            issues.append(
                SchemaIssue(
                    check_name="image_height_value",
                    severity="error",
                    location=f"{location}.height",
                    message=f"Image height must be a positive number. Got: {height}",
                )
            )

    duplicate_image_ids = _find_duplicate_int_values(image_ids)

    for image_id in duplicate_image_ids:
        issues.append(
            SchemaIssue(
                check_name="image_id_duplicate",
                severity="error",
                location="images",
                message=f"Duplicate image id found: {image_id}",
            )
        )

    return issues


def _validate_annotations_schema(annotations: list[object]) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []
    annotation_ids: list[object] = []

    for index, annotation in enumerate(annotations):
        location = f"annotations[{index}]"

        if not isinstance(annotation, dict):
            issues.append(
                SchemaIssue(
                    check_name="annotation_item_type",
                    severity="error",
                    location=location,
                    message="Each annotation entry must be a JSON object.",
                )
            )
            continue

        annotation_id = annotation.get("id")
        annotation_ids.append(annotation_id)

        if "id" not in annotation:
            issues.append(
                SchemaIssue(
                    check_name="annotation_id_missing",
                    severity="error",
                    location=location,
                    message="Annotation entry is missing 'id'.",
                )
            )
        elif not _is_int(annotation_id):
            issues.append(
                SchemaIssue(
                    check_name="annotation_id_type",
                    severity="error",
                    location=f"{location}.id",
                    message=f"Annotation id must be an integer. Got: {annotation_id}",
                )
            )

        image_id = annotation.get("image_id")

        if "image_id" not in annotation:
            issues.append(
                SchemaIssue(
                    check_name="annotation_image_id_missing",
                    severity="error",
                    location=location,
                    message="Annotation entry is missing 'image_id'.",
                )
            )
        elif not _is_int(image_id):
            issues.append(
                SchemaIssue(
                    check_name="annotation_image_id_type",
                    severity="error",
                    location=f"{location}.image_id",
                    message=f"Annotation image_id must be an integer. Got: {image_id}",
                )
            )

        category_id = annotation.get("category_id")

        if "category_id" not in annotation:
            issues.append(
                SchemaIssue(
                    check_name="annotation_category_id_missing",
                    severity="error",
                    location=location,
                    message="Annotation entry is missing 'category_id'.",
                )
            )
        elif not _is_int(category_id):
            issues.append(
                SchemaIssue(
                    check_name="annotation_category_id_type",
                    severity="error",
                    location=f"{location}.category_id",
                    message=f"Annotation category_id must be an integer. Got: {category_id}",
                )
            )

        if "bbox" not in annotation:
            issues.append(
                SchemaIssue(
                    check_name="annotation_bbox_missing",
                    severity="error",
                    location=location,
                    message="Annotation entry is missing 'bbox'.",
                )
            )

    duplicate_annotation_ids = _find_duplicate_int_values(annotation_ids)

    for annotation_id in duplicate_annotation_ids:
        issues.append(
            SchemaIssue(
                check_name="annotation_id_duplicate",
                severity="error",
                location="annotations",
                message=f"Duplicate annotation id found: {annotation_id}",
            )
        )

    return issues


def _validate_categories_schema(categories: list[object]) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []

    for index, category in enumerate(categories):
        location = f"categories[{index}]"

        if not isinstance(category, dict):
            issues.append(
                SchemaIssue(
                    check_name="category_item_type",
                    severity="error",
                    location=location,
                    message="Each category entry must be a JSON object.",
                )
            )
            continue

        category_id = category.get("id")

        if "id" not in category:
            issues.append(
                SchemaIssue(
                    check_name="category_id_missing",
                    severity="error",
                    location=location,
                    message="Category entry is missing 'id'.",
                )
            )
        elif not _is_int(category_id):
            issues.append(
                SchemaIssue(
                    check_name="category_id_type",
                    severity="error",
                    location=f"{location}.id",
                    message=f"Category id must be an integer. Got: {category_id}",
                )
            )

        category_name = category.get("name")

        if "name" not in category:
            issues.append(
                SchemaIssue(
                    check_name="category_name_missing",
                    severity="error",
                    location=location,
                    message="Category entry is missing 'name'.",
                )
            )
        elif not isinstance(category_name, str) or not category_name:
            issues.append(
                SchemaIssue(
                    check_name="category_name_type",
                    severity="error",
                    location=f"{location}.name",
                    message=f"Category name must be a non-empty string. Got: {category_name}",
                )
            )

    return issues