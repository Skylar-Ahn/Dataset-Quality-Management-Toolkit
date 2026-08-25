from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any

from dq_toolkit.review.review_queue import build_review_queue


VALIDATION_SECTIONS = ["schema", "reference", "bbox", "category"]
PRIORITY_TIERS = ["P0", "P1", "P2", "P3"]


def load_report(report_path: str | Path) -> dict[str, Any]:
    """
    [P1] quality report JSON을 읽는다.
    """
    report_path = Path(report_path)

    with report_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_dataset_summary(report: dict[str, Any]) -> dict[str, Any]:
    """
    [P2] dataset summary를 추출한다.

    schema validation이 실패한 report는 dataset이 None일 수 있으므로
    기본값을 안전하게 반환한다.
    """
    dataset = report.get("dataset")

    if not isinstance(dataset, dict):
        return {
            "images": None,
            "annotations": None,
            "categories": None,
            "missing_image_files": None,
        }

    return {
        "images": dataset.get("num_images"),
        "annotations": dataset.get("num_annotations"),
        "categories": dataset.get("num_categories"),
        "missing_image_files": dataset.get("num_missing_image_files"),
    }


def extract_validation_counts(report: dict[str, Any]) -> dict[str, int | str]:
    """
    [P3] validation section별 issue count를 추출한다.
    """
    validation = report.get("validation", {})
    counts: dict[str, int | str] = {}

    for section_name in VALIDATION_SECTIONS:
        section = validation.get(section_name, {})

        if section.get("skipped", False):
            counts[section_name] = "skipped"
        else:
            counts[section_name] = int(section.get("count", 0))

    return counts


def extract_issue_type_counts(report: dict[str, Any]) -> Counter:
    """
    [P4] issue type별 count를 추출한다.
    """
    validation = report.get("validation", {})
    issue_type_counts: Counter = Counter()

    for section_name in VALIDATION_SECTIONS:
        section = validation.get(section_name, {})

        if section.get("skipped", False):
            continue

        by_check_name = section.get("by_check_name", {})

        for check_name, count in by_check_name.items():
            issue_type_counts[check_name] += count

    return issue_type_counts


def extract_review_tier_counts(report: dict[str, Any]) -> dict[str, int]:
    """
    [P5] review queue priority tier별 count를 계산한다.
    """
    rows = build_review_queue(report)
    tier_counts = Counter(row.priority_tier for row in rows)

    return {
        tier: tier_counts.get(tier, 0)
        for tier in PRIORITY_TIERS
    }


def build_comparison_summary_rows(
    clean_report: dict[str, Any],
    dirty_report: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    [P6] 비교 summary row를 만든다.

    CSV로 저장하기 쉬운 long-format row를 만든다.
    """
    rows: list[dict[str, Any]] = []

    clean_dataset = extract_dataset_summary(clean_report)
    dirty_dataset = extract_dataset_summary(dirty_report)

    for metric_name in ["images", "annotations", "categories", "missing_image_files"]:
        rows.append(
            {
                "section": "dataset",
                "metric": metric_name,
                "clean": clean_dataset.get(metric_name),
                "dirty": dirty_dataset.get(metric_name),
                "delta": _safe_delta(
                    clean_dataset.get(metric_name),
                    dirty_dataset.get(metric_name),
                ),
            }
        )

    clean_validation = extract_validation_counts(clean_report)
    dirty_validation = extract_validation_counts(dirty_report)

    for section_name in VALIDATION_SECTIONS:
        rows.append(
            {
                "section": "validation",
                "metric": f"{section_name}_issues",
                "clean": clean_validation.get(section_name),
                "dirty": dirty_validation.get(section_name),
                "delta": _safe_delta(
                    clean_validation.get(section_name),
                    dirty_validation.get(section_name),
                ),
            }
        )

    clean_tiers = extract_review_tier_counts(clean_report)
    dirty_tiers = extract_review_tier_counts(dirty_report)

    for tier in PRIORITY_TIERS:
        rows.append(
            {
                "section": "review_queue",
                "metric": f"{tier}_rows",
                "clean": clean_tiers.get(tier, 0),
                "dirty": dirty_tiers.get(tier, 0),
                "delta": _safe_delta(
                    clean_tiers.get(tier, 0),
                    dirty_tiers.get(tier, 0),
                ),
            }
        )

    return rows


def _safe_delta(clean_value: Any, dirty_value: Any) -> int | float | None:
    """
    clean과 dirty 값의 차이를 계산한다.

    숫자가 아닌 값이 들어오면 None을 반환한다.
    """
    if isinstance(clean_value, (int, float)) and isinstance(dirty_value, (int, float)):
        return dirty_value - clean_value

    return None


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """
    Markdown 표 문자열을 만든다.
    """
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"

    row_lines = [
        "| " + " | ".join(_format_markdown_value(value) for value in row) + " |"
        for row in rows
    ]

    return "\n".join([header_line, separator_line, *row_lines])


def _format_markdown_value(value: Any) -> str:
    if value is None:
        return "-"

    return str(value)


def generate_comparison_markdown(
    clean_report: dict[str, Any],
    dirty_report: dict[str, Any],
) -> str:
    """
    [P7] Markdown report를 생성한다.
    """
    clean_dataset = extract_dataset_summary(clean_report)
    dirty_dataset = extract_dataset_summary(dirty_report)

    clean_validation = extract_validation_counts(clean_report)
    dirty_validation = extract_validation_counts(dirty_report)

    clean_tiers = extract_review_tier_counts(clean_report)
    dirty_tiers = extract_review_tier_counts(dirty_report)

    clean_issue_counts = extract_issue_type_counts(clean_report)
    dirty_issue_counts = extract_issue_type_counts(dirty_report)

    all_issue_types = sorted(
        set(clean_issue_counts.keys()) | set(dirty_issue_counts.keys())
    )

    issue_breakdown_rows = []

    for issue_type in all_issue_types:
        clean_count = clean_issue_counts.get(issue_type, 0)
        dirty_count = dirty_issue_counts.get(issue_type, 0)
        delta = dirty_count - clean_count

        if clean_count == 0 and dirty_count == 0:
            continue

        issue_breakdown_rows.append(
            [
                issue_type,
                clean_count,
                dirty_count,
                delta,
            ]
        )

    markdown_lines = [
        "# Clean vs Dirty COCO Quality Comparison",
        "",
        "## 1. Purpose",
        "",
        (
            "This report compares a clean COCO mini dataset with a dirty COCO dataset "
            "generated through controlled corruption. The goal is to verify whether "
            "the quality checks detect intentionally injected dataset issues and "
            "whether those issues are converted into review queue items."
        ),
        "",
        "## 2. Dataset Summary",
        "",
        _markdown_table(
            headers=["Metric", "Clean", "Dirty", "Delta"],
            rows=[
                [
                    "Images",
                    clean_dataset["images"],
                    dirty_dataset["images"],
                    _safe_delta(clean_dataset["images"], dirty_dataset["images"]),
                ],
                [
                    "Annotations",
                    clean_dataset["annotations"],
                    dirty_dataset["annotations"],
                    _safe_delta(
                        clean_dataset["annotations"],
                        dirty_dataset["annotations"],
                    ),
                ],
                [
                    "Categories",
                    clean_dataset["categories"],
                    dirty_dataset["categories"],
                    _safe_delta(
                        clean_dataset["categories"],
                        dirty_dataset["categories"],
                    ),
                ],
                [
                    "Missing image files",
                    clean_dataset["missing_image_files"],
                    dirty_dataset["missing_image_files"],
                    _safe_delta(
                        clean_dataset["missing_image_files"],
                        dirty_dataset["missing_image_files"],
                    ),
                ],
            ],
        ),
        "",
        "## 3. Validation Issue Summary",
        "",
        _markdown_table(
            headers=["Validation Section", "Clean", "Dirty", "Delta"],
            rows=[
                [
                    section_name,
                    clean_validation.get(section_name),
                    dirty_validation.get(section_name),
                    _safe_delta(
                        clean_validation.get(section_name),
                        dirty_validation.get(section_name),
                    ),
                ]
                for section_name in VALIDATION_SECTIONS
            ],
        ),
        "",
        "## 4. Review Queue Summary",
        "",
        _markdown_table(
            headers=["Priority Tier", "Clean", "Dirty", "Delta"],
            rows=[
                [
                    tier,
                    clean_tiers.get(tier, 0),
                    dirty_tiers.get(tier, 0),
                    _safe_delta(clean_tiers.get(tier, 0), dirty_tiers.get(tier, 0)),
                ]
                for tier in PRIORITY_TIERS
            ],
        ),
        "",
        "## 5. Issue Type Breakdown",
        "",
    ]

    if issue_breakdown_rows:
        markdown_lines.append(
            _markdown_table(
                headers=["Issue Type", "Clean", "Dirty", "Delta"],
                rows=issue_breakdown_rows,
            )
        )
    else:
        markdown_lines.append("No validation issues were found in either report.")

    markdown_lines.extend(
        [
            "",
            "## 6. Interpretation",
            "",
            (
                "- The clean dataset is expected to have few or no validation issues, "
                "because it is based on a well-curated COCO subset."
            ),
            (
                "- The dirty dataset is expected to show increased reference, bbox, "
                "and category issues, because controlled corruptions were injected "
                "into the annotation JSON."
            ),
            (
                "- If the dirty report shows the expected issue types and the review "
                "queue contains corresponding P0/P1/P2/P3 items, the validation and "
                "review workflow is working as intended."
            ),
            "",
            "## 7. Note",
            "",
            (
                "Priority tiers are rule-based triage labels. They are not objective "
                "data quality scores. They are intended to help reviewers sort and "
                "inspect detected issues in a transparent way."
            ),
        ]
    )

    return "\n".join(markdown_lines)


def save_comparison_csv(
    rows: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    """
    [P8] CSV summary를 저장한다.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["section", "metric", "clean", "dirty", "delta"]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_comparison_markdown(
    markdown_text: str,
    output_path: str | Path,
) -> None:
    """
    [P9] Markdown report를 저장한다.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(markdown_text)


def compare_quality_reports(
    clean_report_path: str | Path,
    dirty_report_path: str | Path,
    output_markdown_path: str | Path,
    output_csv_path: str | Path,
) -> dict[str, Any]:
    """
    Clean report와 Dirty report를 비교하고 Markdown/CSV 리포트를 저장한다.
    """
    # [P1] quality report JSON을 읽는다.
    clean_report = load_report(clean_report_path)
    dirty_report = load_report(dirty_report_path)

    # [P6] 비교 summary row를 만든다.
    summary_rows = build_comparison_summary_rows(
        clean_report=clean_report,
        dirty_report=dirty_report,
    )

    # [P7] Markdown report를 생성한다.
    markdown_text = generate_comparison_markdown(
        clean_report=clean_report,
        dirty_report=dirty_report,
    )

    # [P8] CSV summary를 저장한다.
    save_comparison_csv(summary_rows, output_csv_path)

    # [P9] Markdown report를 저장한다.
    save_comparison_markdown(markdown_text, output_markdown_path)

    return {
        "summary_rows": summary_rows,
        "markdown_path": str(output_markdown_path),
        "csv_path": str(output_csv_path),
    }