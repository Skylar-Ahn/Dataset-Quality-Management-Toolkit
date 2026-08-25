from collections import Counter
from dataclasses import asdict, dataclass
import csv
import json
from pathlib import Path
from typing import Any


VALIDATION_SECTIONS = ["schema", "reference", "bbox", "category"]

PRIORITY_TIER_ORDER = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
}

SEVERITY_ORDER = {
    "error": 0,
    "warning": 1,
    "info": 2,
}


@dataclass
class ReviewQueueRow:
    """
    [P1] 검수 작업 큐의 row 하나를 나타내는 데이터 구조.

    이 row는 issue 하나를 사람이 처리 가능한 작업 단위로 바꾼 결과다.
    """
    review_id: int
    priority_tier: str
    priority_reason: str
    review_scope: str
    image_id: int | None
    annotation_id: int | None
    file_name: str | None
    issue_section: str
    issue_type: str
    severity: str
    title: str
    description: str
    default_impact_level: str
    blocking_level: str
    judgement_level: str
    recommended_owner: str
    auto_fixable: str
    suggested_action: str
    all_suggested_actions: str
    issue_count_for_image: int
    message: str


def load_quality_report(report_path: str | Path) -> dict[str, Any]:
    """
    [P2] quality_report.json을 읽는다.
    """
    report_path = Path(report_path)

    with report_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_validation_issues(
    quality_report: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    [P3] quality report 안의 validation issue를 평탄화한다.

    반환되는 issue dict에는 issue_section 필드가 추가된다.
    """
    validation = quality_report.get("validation", {})
    flattened_issues: list[dict[str, Any]] = []

    for section_name in VALIDATION_SECTIONS:
        section = validation.get(section_name, {})

        # schema validation 실패 등으로 section이 skipped된 경우 건너뛴다.
        if section.get("skipped", False):
            continue

        issues = section.get("issues", [])

        for issue in issues:
            issue_with_section = dict(issue)
            issue_with_section["issue_section"] = section_name
            flattened_issues.append(issue_with_section)

    return flattened_issues


def _get_image_issue_counts(
    issues: list[dict[str, Any]],
) -> Counter:
    """
    [P4] image_id별 issue 개수를 계산한다.

    image_id가 없는 schema-level issue는 '__dataset__' key로 계산한다.
    """
    counter: Counter = Counter()

    for issue in issues:
        image_id = issue.get("image_id")

        if image_id is None:
            counter["__dataset__"] += 1
        else:
            counter[image_id] += 1

    return counter


def determine_review_scope(issue: dict[str, Any]) -> str:
    """
    issue가 dataset-level, image-level, annotation-level 중
    어디에 해당하는지 판단한다.
    """
    annotation_id = issue.get("annotation_id")
    image_id = issue.get("image_id")

    if annotation_id is not None:
        return "annotation"

    if image_id is not None:
        return "image"

    return "dataset"


def determine_priority_tier(
    issue: dict[str, Any],
) -> tuple[str, str]:
    """
    [P5] issue catalog 정보를 이용해 priority_tier를 결정한다.

    이 tier는 절대적인 품질 점수가 아니라,
    현재 MVP에서 검수 작업을 정렬하기 위한 rule-based triage 결과다.
    """
    severity = issue.get("severity", "info")
    catalog = issue.get("catalog", {})

    blocking_level = catalog.get("blocking_level", "unknown")
    judgement_level = catalog.get("judgement_level", "human_review")
    impact_level = catalog.get("default_impact_level", "unknown")

    # [P5-1] 데이터셋 로딩 또는 학습 샘플 구성을 막는 문제
    if blocking_level in {
        "blocks_dataset_loading",
        "blocks_training_sample",
    }:
        return (
            "P0",
            f"Blocking issue: {blocking_level}",
        )

    # [P5-2] 학습 target을 직접 오염시키는 문제
    if (
        severity == "error"
        and blocking_level in {
            "affects_annotation_quality",
            "affects_class_mapping",
            "affects_dataset_integrity",
        }
    ):
        return (
            "P1",
            f"Error affecting training target: {blocking_level}",
        )

    # [P5-3] impact가 high/critical인 error
    if severity == "error" and impact_level in {"critical", "high"}:
        return (
            "P1",
            f"High-impact error: {impact_level}",
        )

    # [P5-4] 사람 검수가 필요한 문제
    if judgement_level == "human_review" or blocking_level == "needs_human_check":
        return (
            "P2",
            f"Human review required: {judgement_level}",
        )

    # [P5-5] 정책 또는 ontology 검토가 필요한 문제
    if judgement_level == "policy_review" or blocking_level == "needs_policy_check":
        return (
            "P3",
            f"Policy review required: {blocking_level}",
        )

    # [P5-6] 추적성, 품질검사 제한, 기타 검토 항목
    return (
        "P3",
        f"Follow-up review: {blocking_level}",
    )


def _get_first_suggested_action(catalog: dict[str, Any]) -> str:
    suggested_actions = catalog.get("suggested_actions", [])

    if not suggested_actions:
        return ""

    return str(suggested_actions[0])


def _join_suggested_actions(catalog: dict[str, Any]) -> str:
    suggested_actions = catalog.get("suggested_actions", [])

    return " | ".join(str(action) for action in suggested_actions)


def convert_issue_to_review_row(
    issue: dict[str, Any],
    review_id: int,
    image_issue_counts: Counter,
) -> ReviewQueueRow:
    """
    [P6] issue 하나를 ReviewQueueRow로 변환한다.
    """
    catalog = issue.get("catalog", {})

    image_id = issue.get("image_id")
    annotation_id = issue.get("annotation_id")

    count_key = image_id if image_id is not None else "__dataset__"
    issue_count_for_image = image_issue_counts[count_key]

    priority_tier, priority_reason = determine_priority_tier(issue)

    return ReviewQueueRow(
        review_id=review_id,
        priority_tier=priority_tier,
        priority_reason=priority_reason,
        review_scope=determine_review_scope(issue),
        image_id=image_id,
        annotation_id=annotation_id,
        file_name=issue.get("file_name"),
        issue_section=issue.get("issue_section", ""),
        issue_type=issue.get("check_name", ""),
        severity=issue.get("severity", "info"),
        title=catalog.get("title", ""),
        description=catalog.get("description", ""),
        default_impact_level=catalog.get("default_impact_level", "unknown"),
        blocking_level=catalog.get("blocking_level", "unknown"),
        judgement_level=catalog.get("judgement_level", "human_review"),
        recommended_owner=catalog.get("recommended_owner", "data_curator"),
        auto_fixable=catalog.get("auto_fixable", "no"),
        suggested_action=_get_first_suggested_action(catalog),
        all_suggested_actions=_join_suggested_actions(catalog),
        issue_count_for_image=issue_count_for_image,
        message=issue.get("message", ""),
    )


def sort_review_queue_rows(
    rows: list[ReviewQueueRow],
) -> list[ReviewQueueRow]:
    """
    [P7] Review Queue row들을 정렬한다.

    정렬 기준:
    1. priority_tier: P0 → P1 → P2 → P3
    2. severity: error → warning → info
    3. issue_count_for_image: 많은 순
    4. image_id
    5. annotation_id
    """
    return sorted(
        rows,
        key=lambda row: (
            PRIORITY_TIER_ORDER.get(row.priority_tier, 99),
            SEVERITY_ORDER.get(row.severity, 99),
            -row.issue_count_for_image,
            row.image_id if row.image_id is not None else -1,
            row.annotation_id if row.annotation_id is not None else -1,
        ),
    )


def build_review_queue(
    quality_report: dict[str, Any],
) -> list[ReviewQueueRow]:
    """
    quality report dictionary에서 Review Queue row 목록을 만든다.
    """
    issues = flatten_validation_issues(quality_report)
    image_issue_counts = _get_image_issue_counts(issues)

    rows = [
        convert_issue_to_review_row(
            issue=issue,
            review_id=index + 1,
            image_issue_counts=image_issue_counts,
        )
        for index, issue in enumerate(issues)
    ]

    return sort_review_queue_rows(rows)


def save_review_queue_csv(
    rows: list[ReviewQueueRow],
    output_path: str | Path,
) -> None:
    """
    [P8] Review Queue CSV를 저장한다.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "review_id",
        "priority_tier",
        "priority_reason",
        "review_scope",
        "image_id",
        "annotation_id",
        "file_name",
        "issue_section",
        "issue_type",
        "severity",
        "title",
        "description",
        "default_impact_level",
        "blocking_level",
        "judgement_level",
        "recommended_owner",
        "auto_fixable",
        "suggested_action",
        "all_suggested_actions",
        "issue_count_for_image",
        "message",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(asdict(row))