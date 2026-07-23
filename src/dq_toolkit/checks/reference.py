from dataclasses import dataclass
from pathlib import Path

from dq_toolkit.io.coco import CocoDataset


@dataclass
class ReferenceIssue:
    check_name: str
    severity: str
    image_id: int | None
    annotation_id: int | None
    file_name: str | None
    message: str


def validate_references(
    coco_dataset: CocoDataset,
    image_dir: str | Path | None = None,
) -> list[ReferenceIssue]:
    """
    Validate reference relationships in a COCO-format dataset.

    Main checks:
    - annotation.image_id must exist in images.id
    - image.file_name must exist in the image directory, if image_dir is provided
    - images without annotations are reported as warnings
    """
    issues: list[ReferenceIssue] = []

    image_id_to_image = coco_dataset.image_id_to_image
    valid_image_ids = set(image_id_to_image.keys())

    referenced_image_ids: set[int] = set()

    for annotation in coco_dataset.annotations:
        annotation_id = annotation.get("id")
        image_id = annotation.get("image_id")

        if image_id not in valid_image_ids:
            issues.append(
                ReferenceIssue(
                    check_name="annotation_unknown_image_id",
                    severity="error",
                    image_id=image_id,
                    annotation_id=annotation_id,
                    file_name=None,
                    message=(
                        f"Annotation references an unknown image_id: "
                        f"{image_id}"
                    ),
                )
            )
            continue

        referenced_image_ids.add(image_id)

    if image_dir is not None:
        image_dir = Path(image_dir)

        for image in coco_dataset.images:
            image_id = image.get("id")
            file_name = image.get("file_name")

            if not isinstance(file_name, str) or not file_name:
                issues.append(
                    ReferenceIssue(
                        check_name="image_file_name_invalid",
                        severity="error",
                        image_id=image_id,
                        annotation_id=None,
                        file_name=None,
                        message=(
                            f"Image has invalid file_name. "
                            f"image_id={image_id}, file_name={file_name}"
                        ),
                    )
                )
                continue

            image_path = image_dir / file_name

            if not image_path.exists():
                issues.append(
                    ReferenceIssue(
                        check_name="missing_image_file",
                        severity="error",
                        image_id=image_id,
                        annotation_id=None,
                        file_name=file_name,
                        message=f"Image file does not exist: {image_path}",
                    )
                )

    for image in coco_dataset.images:
        image_id = image.get("id")
        file_name = image.get("file_name")

        if image_id not in referenced_image_ids:
            issues.append(
                ReferenceIssue(
                    check_name="image_without_annotations",
                    severity="warning",
                    image_id=image_id,
                    annotation_id=None,
                    file_name=file_name,
                    message=(
                        "Image has no annotations. "
                        "This may be valid for negative images, "
                        "but should be reviewed."
                    ),
                )
            )

    return issues