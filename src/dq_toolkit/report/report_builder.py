from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from dq_toolkit.analysis.bbox_distribution import (
    analyze_bbox_distribution,
    summarize_bbox_distribution,
)
from dq_toolkit.analysis.class_distribution import analyze_class_distribution
from dq_toolkit.checks.bbox import validate_bboxes
from dq_toolkit.checks.category import validate_categories
from dq_toolkit.checks.reference import validate_references
from dq_toolkit.checks.schema import validate_coco_schema
from dq_toolkit.io.coco import load_coco_annotation, summarize_coco_dataset
from dq_toolkit.review.issue_catalog import enrich_issue_dict

def _to_dict(item: Any) -> dict:
    if is_dataclass(item):
        return asdict(item)

    if isinstance(item, dict):
        return item

    raise TypeError(f"Unsupported report item type: {type(item)}")


def _to_dict_list(items: list[Any]) -> list[dict]:
    return [_to_dict(item) for item in items]


def _count_by_severity(issue_dicts: list[dict]) -> dict:
    return dict(Counter(issue["severity"] for issue in issue_dicts))


def _count_by_check_name(issue_dicts: list[dict]) -> dict:
    return dict(Counter(issue["check_name"] for issue in issue_dicts))


def _build_issue_section(issues: list[Any], language: str = 'ko') -> dict:
    issue_dicts = _to_dict_list(issues)

    enriched_issue_dicts = [
        enrich_issue_dict(issue_dict, language=language)
        for issue_dict in issue_dicts
    ]

    return {
        "count": len(enriched_issue_dicts),
        "by_severity": _count_by_severity(enriched_issue_dicts),
        "by_check_name": _count_by_check_name(enriched_issue_dicts),
        "issues": enriched_issue_dicts,
    }


def build_quality_report(
    annotation_path: str | Path,
    image_dir: str | Path | None = None,
) -> dict:
    
    annotation_path = Path(annotation_path)
    image_dir_path = Path(image_dir) if image_dir is not None else None

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "annotation_path": str(annotation_path),
        "image_dir": str(image_dir_path) if image_dir_path is not None else None,
        "report_version": "0.1.0",
    }

    schema_issues = validate_coco_schema(annotation_path)
    schema_section = _build_issue_section(schema_issues)

    if schema_issues:
        return {
            "metadata": metadata,
            "dataset": None,
            "validation": {
                "schema": schema_section,
                "reference": {
                    "skipped": True,
                    "reason": "Schema validation failed.",
                },
                "bbox": {
                    "skipped": True,
                    "reason": "Schema validation failed.",
                },
                "category": {
                    "skipped": True,
                    "reason": "Schema validation failed.",
                },
            },
            "analysis": {
                "skipped": True,
                "reason": "Schema validation failed.",
            },
        }

   
    coco_dataset = load_coco_annotation(annotation_path)

    dataset_summary = summarize_coco_dataset(coco_dataset, image_dir_path)

    reference_issues = validate_references(coco_dataset, image_dir_path)

    bbox_issues = validate_bboxes(coco_dataset)

    category_issues = validate_categories(coco_dataset)

    class_distribution = analyze_class_distribution(coco_dataset)

    bbox_distribution = analyze_bbox_distribution(coco_dataset)
    bbox_distribution_summary = summarize_bbox_distribution(bbox_distribution)

    report = {
        "metadata": metadata,
        "dataset": dataset_summary,
        "validation": {
            "schema": schema_section,
            "reference": _build_issue_section(reference_issues),
            "bbox": _build_issue_section(bbox_issues),
            "category": _build_issue_section(category_issues),
        },
        "analysis": {
            "class_distribution": _to_dict_list(class_distribution),
            "bbox_distribution": {
                "summary": bbox_distribution_summary,
                "rows": _to_dict_list(bbox_distribution),
            },
        },
    }

    return report


def save_quality_report_json(
    report: dict,
    output_path: str | Path,
) -> None:
    
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)