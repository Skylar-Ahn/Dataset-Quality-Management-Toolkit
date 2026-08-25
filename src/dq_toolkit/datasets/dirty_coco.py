from copy import deepcopy
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass
class CorruptionRecord:
    """
    Dirty COCO 생성 과정에서 어떤 오류를 어디에 주입했는지 기록한다.
    """
    corruption_name: str
    expected_check_name: str
    target_type: str
    image_id: int | None
    annotation_id: int | None
    category_id: int | None
    details: dict[str, Any]


def _load_json(path: str | Path) -> dict[str, Any]:
    """
    [P1] clean COCO annotation JSON을 읽는다.
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(data: dict[str, Any] | list[dict[str, Any]], path: str | Path) -> None:
    """
    [P10] JSON 파일을 저장한다.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _require_minimum_items(
    images: list[dict[str, Any]],
    annotations: list[dict[str, Any]],
    categories: list[dict[str, Any]],
) -> None:
    """
    Dirty corruption을 만들 수 있을 만큼 데이터가 있는지 확인한다.
    """
    if len(images) < 2:
        raise ValueError("Dirty COCO generation requires at least 2 images.")

    if len(annotations) < 4:
        raise ValueError("Dirty COCO generation requires at least 4 annotations.")

    if len(categories) < 2:
        raise ValueError("Dirty COCO generation requires at least 2 categories.")


def _get_image_by_id(
    images: list[dict[str, Any]],
    image_id: int,
) -> dict[str, Any]:
    for image in images:
        if image.get("id") == image_id:
            return image

    raise ValueError(f"Image id not found: {image_id}")


def _select_annotation_indices(
    annotations: list[dict[str, Any]],
    excluded_image_id: int,
    required_count: int,
) -> list[int]:
    """
    [P4] corruption에 사용할 annotation index를 선택한다.

    image_without_annotations에 사용할 image의 annotation은 제외한다.
    """
    selected_indices: list[int] = []

    for index, annotation in enumerate(annotations):
        if annotation.get("image_id") == excluded_image_id:
            continue

        selected_indices.append(index)

        if len(selected_indices) == required_count:
            break

    if len(selected_indices) < required_count:
        raise ValueError(
            "Not enough annotations outside the selected empty image. "
            f"required={required_count}, found={len(selected_indices)}"
        )

    return selected_indices


def _get_max_int_value(items: list[dict[str, Any]], key: str) -> int:
    values = [
        item.get(key)
        for item in items
        if isinstance(item.get(key), int)
    ]

    if not values:
        return 0

    return max(values)


def generate_dirty_coco(
    input_annotation_path: str | Path,
    output_annotation_path: str | Path,
    output_manifest_path: str | Path,
) -> list[CorruptionRecord]:
    """
    Clean COCO annotation을 기반으로 schema-valid dirty COCO annotation을 생성한다.

    원본 annotation 파일은 수정하지 않는다.
    이미지 파일도 복사하거나 삭제하지 않는다.
    """
    # [P1] clean COCO annotation JSON을 읽고 deepcopy한다.
    clean_data = _load_json(input_annotation_path)
    dirty_data = deepcopy(clean_data)

    # [P2] images, annotations, categories를 가져온다.
    images = dirty_data.get("images", [])
    annotations = dirty_data.get("annotations", [])
    categories = dirty_data.get("categories", [])

    _require_minimum_items(images, annotations, categories)

    records: list[CorruptionRecord] = []

    max_image_id = _get_max_int_value(images, "id")
    max_category_id = _get_max_int_value(categories, "id")

    unknown_image_id = max_image_id + 1_000_000
    unknown_category_id = max_category_id + 1_000_000

    # [P3] image_without_annotations에 사용할 image를 선택한다.
    empty_image = images[-1]
    empty_image_id = empty_image.get("id")

    if not isinstance(empty_image_id, int):
        raise ValueError("Selected empty image has invalid id.")

    # [P4] corruption에 사용할 annotation들을 선택한다.
    (
        unknown_image_ann_index,
        bbox_out_ann_index,
        bbox_zero_ann_index,
        unknown_category_ann_index,
    ) = _select_annotation_indices(
        annotations=annotations,
        excluded_image_id=empty_image_id,
        required_count=4,
    )

    # ------------------------------------------------------------------
    # [P5] reference 오류 주입
    # ------------------------------------------------------------------

    # [P5-1] missing_image_file: 실제 존재하지 않는 file_name으로 변경한다.
    missing_file_image = images[0]
    original_file_name = missing_file_image.get("file_name")
    missing_file_image["file_name"] = "__dirty_missing_image_file__.jpg"

    records.append(
        CorruptionRecord(
            corruption_name="inject_missing_image_file",
            expected_check_name="missing_image_file",
            target_type="image",
            image_id=missing_file_image.get("id"),
            annotation_id=None,
            category_id=None,
            details={
                "original_file_name": original_file_name,
                "dirty_file_name": missing_file_image["file_name"],
            },
        )
    )

    # [P5-2] annotation_unknown_image_id: annotation image_id를 없는 id로 변경한다.
    unknown_image_annotation = annotations[unknown_image_ann_index]
    original_image_id = unknown_image_annotation.get("image_id")
    unknown_image_annotation["image_id"] = unknown_image_id

    records.append(
        CorruptionRecord(
            corruption_name="inject_unknown_image_id",
            expected_check_name="annotation_unknown_image_id",
            target_type="annotation",
            image_id=unknown_image_id,
            annotation_id=unknown_image_annotation.get("id"),
            category_id=unknown_image_annotation.get("category_id"),
            details={
                "original_image_id": original_image_id,
                "dirty_image_id": unknown_image_id,
            },
        )
    )

    # ------------------------------------------------------------------
    # [P6] bbox 오류 주입
    # ------------------------------------------------------------------

    # [P6-1] bbox_out_of_image: bbox가 이미지 경계를 벗어나도록 변경한다.
    bbox_out_annotation = annotations[bbox_out_ann_index]
    bbox_out_image_id = bbox_out_annotation.get("image_id")

    if not isinstance(bbox_out_image_id, int):
        raise ValueError("Selected bbox_out annotation has invalid image_id.")

    bbox_out_image = _get_image_by_id(images, bbox_out_image_id)
    image_width = bbox_out_image.get("width")
    image_height = bbox_out_image.get("height")

    if not isinstance(image_width, (int, float)) or not isinstance(image_height, (int, float)):
        raise ValueError("Selected image has invalid width/height.")

    original_bbox = bbox_out_annotation.get("bbox")
    dirty_bbox = [
        max(0, image_width - 5),
        max(0, image_height - 5),
        50,
        50,
    ]
    bbox_out_annotation["bbox"] = dirty_bbox

    records.append(
        CorruptionRecord(
            corruption_name="inject_bbox_out_of_image",
            expected_check_name="bbox_out_of_image",
            target_type="annotation",
            image_id=bbox_out_image_id,
            annotation_id=bbox_out_annotation.get("id"),
            category_id=bbox_out_annotation.get("category_id"),
            details={
                "original_bbox": original_bbox,
                "dirty_bbox": dirty_bbox,
                "image_width": image_width,
                "image_height": image_height,
            },
        )
    )

    # [P6-2] bbox_non_positive_size: bbox width를 0으로 변경한다.
    bbox_zero_annotation = annotations[bbox_zero_ann_index]
    original_bbox = bbox_zero_annotation.get("bbox")
    dirty_bbox = [10, 10, 0, 20]
    bbox_zero_annotation["bbox"] = dirty_bbox

    records.append(
        CorruptionRecord(
            corruption_name="inject_bbox_non_positive_size",
            expected_check_name="bbox_non_positive_size",
            target_type="annotation",
            image_id=bbox_zero_annotation.get("image_id"),
            annotation_id=bbox_zero_annotation.get("id"),
            category_id=bbox_zero_annotation.get("category_id"),
            details={
                "original_bbox": original_bbox,
                "dirty_bbox": dirty_bbox,
            },
        )
    )

    # ------------------------------------------------------------------
    # [P7] category 오류 주입
    # ------------------------------------------------------------------

    # [P7-1] annotation_unknown_category_id: 없는 category_id를 참조하도록 변경한다.
    unknown_category_annotation = annotations[unknown_category_ann_index]
    original_category_id = unknown_category_annotation.get("category_id")
    unknown_category_annotation["category_id"] = unknown_category_id

    records.append(
        CorruptionRecord(
            corruption_name="inject_unknown_category_id",
            expected_check_name="annotation_unknown_category_id",
            target_type="annotation",
            image_id=unknown_category_annotation.get("image_id"),
            annotation_id=unknown_category_annotation.get("id"),
            category_id=unknown_category_id,
            details={
                "original_category_id": original_category_id,
                "dirty_category_id": unknown_category_id,
            },
        )
    )

    # [P7-2] category_name_duplicate: 두 번째 category name을 첫 번째와 같게 만든다.
    first_category = categories[0]
    second_category = categories[1]
    original_second_category_name = second_category.get("name")
    second_category["name"] = first_category.get("name")

    records.append(
        CorruptionRecord(
            corruption_name="inject_duplicate_category_name",
            expected_check_name="category_name_duplicate",
            target_type="category",
            image_id=None,
            annotation_id=None,
            category_id=second_category.get("id"),
            details={
                "first_category_id": first_category.get("id"),
                "first_category_name": first_category.get("name"),
                "second_category_id": second_category.get("id"),
                "original_second_category_name": original_second_category_name,
                "dirty_second_category_name": second_category.get("name"),
            },
        )
    )

    # ------------------------------------------------------------------
    # [P8] image_without_annotations 오류 주입
    # ------------------------------------------------------------------

    removed_annotation_ids = [
        annotation.get("id")
        for annotation in annotations
        if annotation.get("image_id") == empty_image_id
    ]

    dirty_data["annotations"] = [
        annotation
        for annotation in annotations
        if annotation.get("image_id") != empty_image_id
    ]

    records.append(
        CorruptionRecord(
            corruption_name="inject_image_without_annotations",
            expected_check_name="image_without_annotations",
            target_type="image",
            image_id=empty_image_id,
            annotation_id=None,
            category_id=None,
            details={
                "removed_annotation_ids": removed_annotation_ids,
                "removed_annotation_count": len(removed_annotation_ids),
                "file_name": empty_image.get("file_name"),
            },
        )
    )

    # [P9] corruption manifest를 만든다.
    manifest = {
        "source_annotation_path": str(input_annotation_path),
        "output_annotation_path": str(output_annotation_path),
        "corruption_policy": "schema_valid_semantic_dirty_v1",
        "corruption_count": len(records),
        "corruptions": [
            asdict(record)
            for record in records
        ],
    }

    # [P10] dirty annotation JSON과 manifest를 저장한다.
    _save_json(dirty_data, output_annotation_path)
    _save_json(manifest, output_manifest_path)

    return records