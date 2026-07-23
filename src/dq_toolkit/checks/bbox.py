from dataclasses import dataclass
from math import isfinite

from dq_toolkit.io.coco import CocoDataset


@dataclass
class BBoxIssue:
    check_name: str
    severity: str
    annotation_id: int | None
    image_id: int | None
    message: str


def validate_bboxes(coco_dataset: CocoDataset) -> list[BBoxIssue]:
    """
    Validate COCO bbox annotations.

    COCO bbox format:
        [x_min, y_min, width, height]
    """
    issues: list[BBoxIssue] = []

    image_id_to_image = coco_dataset.image_id_to_image

    for ann in coco_dataset.annotations:
        ann_id = ann.get("id")
        image_id = ann.get("image_id")

        if image_id not in image_id_to_image:
            issues.append(
                BBoxIssue(
                    check_name="bbox_image_reference",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message="Annotation references a missing image_id.",
                )
            )
            continue

        image = image_id_to_image[image_id]
        image_width = image.get("width")
        image_height = image.get("height")

        bbox = ann.get("bbox")

        if bbox is None:
            issues.append(
                BBoxIssue(
                    check_name="bbox_missing",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message="Annotation is missing bbox.",
                )
            )
            continue

        if not isinstance(bbox, list) or len(bbox) != 4:
            issues.append(
                BBoxIssue(
                    check_name="bbox_format",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message=f"bbox must be a list of 4 numbers. Got: {bbox}",
                )
            )
            continue

        x, y, w, h = bbox

        if not all(isinstance(v, (int, float)) and isfinite(v) for v in bbox):
            issues.append(
                BBoxIssue(
                    check_name="bbox_numeric",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message=f"bbox contains non-numeric or non-finite values. Got: {bbox}",
                )
            )
            continue

        if w <= 0 or h <= 0:
            issues.append(
                BBoxIssue(
                    check_name="bbox_non_positive_size",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message=f"bbox width and height must be positive. Got: {bbox}",
                )
            )

        if x < 0 or y < 0:
            issues.append(
                BBoxIssue(
                    check_name="bbox_negative_coordinate",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message=f"bbox x/y must be non-negative. Got: {bbox}",
                )
            )

        if image_width is None or image_height is None:
            issues.append(
                BBoxIssue(
                    check_name="image_size_missing",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message="Referenced image is missing width or height.",
                )
            )
            continue

        if x + w > image_width or y + h > image_height:
            issues.append(
                BBoxIssue(
                    check_name="bbox_out_of_image",
                    severity="error",
                    annotation_id=ann_id,
                    image_id=image_id,
                    message=(
                        f"bbox exceeds image boundary. "
                        f"bbox={bbox}, image_size=({image_width}, {image_height})"
                    ),
                )
            )

    return issues
