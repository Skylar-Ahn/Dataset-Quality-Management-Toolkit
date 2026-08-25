import argparse
from pathlib import Path

from dq_toolkit.checks.bbox import validate_bboxes
from dq_toolkit.checks.category import validate_categories
from dq_toolkit.checks.reference import validate_references
from dq_toolkit.checks.schema import validate_coco_schema
from dq_toolkit.io.coco import load_coco_annotation, summarize_coco_dataset
from dq_toolkit.analysis.bbox_distribution import (
    analyze_bbox_distribution,
    save_bbox_distribution_csv,
    summarize_bbox_distribution,
)
from dq_toolkit.analysis.class_distribution import (
    analyze_class_distribution,
    save_class_distribution_csv,
)
from dq_toolkit.report.report_builder import (
    build_quality_report,
    save_quality_report_json,
)
from dq_toolkit.review.review_queue import (
    build_review_queue,
    load_quality_report,
    save_review_queue_csv,
)
from dq_toolkit.datasets.dirty_coco import generate_dirty_coco
from dq_toolkit.report.compare_reports import compare_quality_reports


def inspect_coco(args: argparse.Namespace) -> None:
    coco_dataset = load_coco_annotation(args.annotation)
    summary = summarize_coco_dataset(coco_dataset, args.image_dir)

    print("COCO Dataset Summary")
    print("====================")
    print(f"Images      : {summary['num_images']}")
    print(f"Annotations : {summary['num_annotations']}")
    print(f"Categories  : {summary['num_categories']}")

    if "num_missing_images" in summary:
        print(f"Missing image files: {summary['num_missing_images']}")

        if summary["num_missing_images"] > 0:
            print("\nMissing image examples:")
            for file_name in summary["missing_images"][:10]:
                print(f"- {file_name}")


def validate_coco(args: argparse.Namespace) -> None:
    schema_issues = validate_coco_schema(args.annotation)

    print("COCO Validation Result")
    print("======================")
    print(f"Schema issues   : {len(schema_issues)}")

    if schema_issues:
        print("\nSchema issue examples:")
        for issue in schema_issues[:10]:
            print(
                f"- [{issue.severity}] {issue.check_name} | "
                f"location={issue.location} | "
                f"{issue.message}"
            )

        print("\nSchema validation failed. Skipping reference and semantic checks.")
        return

    coco_dataset = load_coco_annotation(args.annotation)

    reference_issues = validate_references(coco_dataset, args.image_dir)
    bbox_issues = validate_bboxes(coco_dataset)
    category_issues = validate_categories(coco_dataset)

    print(f"Reference issues : {len(reference_issues)}")
    print(f"BBox issues: {len(bbox_issues)}")
    print(f"Category issues : {len(category_issues)}")

    if reference_issues:
        print("\nReference issue examples:")
        for issue in reference_issues[:10]:
            print(
                f"- [{issue.severity}] {issue.check_name} | "
                f"image_id={issue.image_id}, "
                f"annotation_id={issue.annotation_id}, "
                f"file_name={issue.file_name} | "
                f"{issue.message}"
            )

    if bbox_issues:
        print("\nBBox issue examples:")
        for issue in bbox_issues[:10]:
            print(
                f"- [{issue.severity}] {issue.check_name} | "
                f"image_id={issue.image_id}, annotation_id={issue.annotation_id} | "
                f"{issue.message}"
            )

    if category_issues:
        print("\nCategory issue examples:")
        for issue in category_issues[:10]:
            print(
                f"- [{issue.severity}] {issue.check_name} | "
                f"image_id={issue.image_id}, "
                f"annotation_id={issue.annotation_id}, "
                f"category_id={issue.category_id} | "
                f"{issue.message}"
            )


def analyze_coco(args: argparse.Namespace) -> None:
    coco_dataset = load_coco_annotation(args.annotation)

    class_distribution = analyze_class_distribution(coco_dataset)
    bbox_distribution = analyze_bbox_distribution(coco_dataset)
    bbox_summary = summarize_bbox_distribution(bbox_distribution)

    print("COCO Class Distribution")
    print("=======================")
    print(
        f"{'category_id':>11}  "
        f"{'category_name':<20}  "
        f"{'instances':>10}  "
        f"{'images':>8}  "
        f"{'inst_ratio':>10}  "
        f"{'img_ratio':>10}"
    )

    for row in class_distribution:
        print(
            f"{row.category_id:>11}  "
            f"{row.category_name:<20}  "
            f"{row.instance_count:>10}  "
            f"{row.image_count:>8}  "
            f"{row.instance_ratio:>10.2%}  "
            f"{row.image_ratio:>10.2%}"
        )

    print("\nCOCO BBox Distribution")
    print("======================")
    print(f"Total valid bboxes: {bbox_summary['total_bboxes']}")

    size_counts = bbox_summary["size_counts"]
    total_bboxes = bbox_summary["total_bboxes"]

    for size_bin in ["small", "medium", "large"]:
        count = size_counts.get(size_bin, 0)
        ratio = count / total_bboxes if total_bboxes > 0 else 0.0
        print(f"{size_bin:<6}: {count:>6} ({ratio:>6.2%})")

    if total_bboxes > 0:
        area = bbox_summary["area"]
        aspect_ratio = bbox_summary["aspect_ratio"]

        print("\nBBox area")
        print(f"- min    : {area['min']:.2f}")
        print(f"- max    : {area['max']:.2f}")
        print(f"- mean   : {area['mean']:.2f}")
        print(f"- median : {area['median']:.2f}")

        print("\nAspect ratio")
        print(f"- min    : {aspect_ratio['min']:.4f}")
        print(f"- max    : {aspect_ratio['max']:.4f}")
        print(f"- mean   : {aspect_ratio['mean']:.4f}")
        print(f"- median : {aspect_ratio['median']:.4f}")

        normalized_area = bbox_summary["normalized_area"]

        if normalized_area:
            print("\nNormalized area")
            print(f"- min    : {normalized_area['min']:.8f}")
            print(f"- max    : {normalized_area['max']:.8f}")
            print(f"- mean   : {normalized_area['mean']:.8f}")
            print(f"- median : {normalized_area['median']:.8f}")


    if args.output_csv is not None:
        save_class_distribution_csv(class_distribution, args.output_csv)
        print(f"\nSaved class distribution CSV: {args.output_csv}")

    if args.bbox_output_csv is not None:
        save_bbox_distribution_csv(bbox_distribution, args.bbox_output_csv)
        print(f"Saved bbox distribution CSV: {args.bbox_output_csv}")


def report_coco(args: argparse.Namespace) -> None:
    report = build_quality_report(
        annotation_path=args.annotation,
        image_dir=args.image_dir,
    )

    save_quality_report_json(report, args.output)

    print("COCO Quality Report")
    print("===================")
    print(f"Saved report: {args.output}")

    validation = report["validation"]

    print("\nValidation summary")
    print(f"- Schema issues    : {validation['schema'].get('count', 'skipped')}")
    print(f"- Reference issues : {validation['reference'].get('count', 'skipped')}")
    print(f"- BBox issues      : {validation['bbox'].get('count', 'skipped')}")
    print(f"- Category issues  : {validation['category'].get('count', 'skipped')}")

    analysis = report["analysis"]

    if isinstance(analysis, dict) and not analysis.get("skipped", False):
        bbox_summary = analysis["bbox_distribution"]["summary"]
        print("\nAnalysis summary")
        print(f"- Class rows       : {len(analysis['class_distribution'])}")
        print(f"- Valid bboxes     : {bbox_summary['total_bboxes']}")


def review_queue(args: argparse.Namespace) -> None:
    quality_report = load_quality_report(args.report)
    rows = build_review_queue(quality_report)

    save_review_queue_csv(rows, args.output)

    print("Review Queue")
    print("============")
    print(f"Input report : {args.report}")
    print(f"Saved CSV    : {args.output}")
    print(f"Queue rows   : {len(rows)}")

    tier_counts = {}

    for row in rows:
        tier_counts[row.priority_tier] = tier_counts.get(row.priority_tier, 0) + 1

    if tier_counts:
        print("\nPriority tier summary")
        for tier in ["P0", "P1", "P2", "P3"]:
            print(f"- {tier}: {tier_counts.get(tier, 0)}")

def make_dirty_coco(args: argparse.Namespace) -> None:
    records = generate_dirty_coco(
        input_annotation_path=args.annotation,
        output_annotation_path=args.output_annotation,
        output_manifest_path=args.output_manifest,
    )

    print("Dirty COCO Generator")
    print("====================")
    print(f"Input annotation : {args.annotation}")
    print(f"Output annotation: {args.output_annotation}")
    print(f"Output manifest  : {args.output_manifest}")
    print(f"Corruptions      : {len(records)}")

    print("\nInjected corruptions")
    for record in records:
        print(
            f"- {record.corruption_name} "
            f"→ expected={record.expected_check_name}, "
            f"target={record.target_type}, "
            f"image_id={record.image_id}, "
            f"annotation_id={record.annotation_id}, "
            f"category_id={record.category_id}"
        )

def compare_reports(args: argparse.Namespace) -> None:
    result = compare_quality_reports(
        clean_report_path=args.clean_report,
        dirty_report_path=args.dirty_report,
        output_markdown_path=args.output_md,
        output_csv_path=args.output_csv,
    )

    print("Clean vs Dirty Report")
    print("=====================")
    print(f"Clean report : {args.clean_report}")
    print(f"Dirty report : {args.dirty_report}")
    print(f"Saved MD     : {result['markdown_path']}")
    print(f"Saved CSV    : {result['csv_path']}")

    print("\nSummary rows")
    for row in result["summary_rows"]:
        print(
            f"- {row['section']} | {row['metric']}: "
            f"clean={row['clean']}, dirty={row['dirty']}, delta={row['delta']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dataset quality management toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # inspect parser
    inspect_parser = subparsers.add_parser(
        "inspect-coco",
        help="Inspect a COCO-format dataset",
    )
    inspect_parser.add_argument(
        "--annotation",
        required=True,
        type=Path,
        help="Path to COCO annotation JSON",
    )
    inspect_parser.add_argument(
        "--image-dir",
        required=False,
        type=Path,
        help="Path to image directory",
    )
    inspect_parser.set_defaults(func=inspect_coco)


    # validate parser
    validate_parser = subparsers.add_parser(
        "validate-coco",
        help="Validate a COCO-format dataset",
    )
    validate_parser.add_argument(
        "--annotation",
        required=True,
        type=Path,
        help="Path to COCO annotation JSON",
    )
    validate_parser.add_argument(
        "--image-dir",
        required=False,
        type=Path,
        help="Path to image directory",
    )
    validate_parser.set_defaults(func=validate_coco)


    # analyze parser
    analyze_parser = subparsers.add_parser(
        "analyze-coco",
        help="Analyze a COCO-format dataset",
    )
    analyze_parser.add_argument(
        "--annotation",
        required=True,
        type=Path,
        help="Path to COCO annotation JSON",
    )
    analyze_parser.add_argument(
        "--output-csv",
        required=False,
        type=Path,
        help="Path to save class distribution CSV",
    )
    analyze_parser.add_argument(
        "--bbox-output-csv",
        required=False,
        type=Path,
        help="Path to save bbox distribution CSV",
    )
    analyze_parser.set_defaults(func=analyze_coco)


    # report parser
    report_parser = subparsers.add_parser(
        "report-coco",
        help="Generate a JSON quality report for a COCO-format dataset",
    )
    report_parser.add_argument(
        "--language",
        required=False,
        choices=["ko", "en"],
        default="ko",
        help="Catalog output language",
    )
    report_parser.add_argument(
        "--annotation",
        required=True,
        type=Path,
        help="Path to COCO annotation JSON",
    )
    report_parser.add_argument(
        "--image-dir",
        required=False,
        type=Path,
        help="Path to image directory",
    )
    report_parser.add_argument(
        "--output",
        required=False,
        type=Path,
        default=Path("reports/quality_report.json"),
        help="Path to save quality report JSON",
    )
    report_parser.set_defaults(func=report_coco)


    # review queue parser
    review_queue_parser = subparsers.add_parser(
        "review-queue",
        help="Generate a review queue CSV from a quality report JSON",
    )
    review_queue_parser.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Path to quality report JSON",
    )
    review_queue_parser.add_argument(
        "--output",
        required=False,
        type=Path,
        default=Path("reports/review_queue.csv"),
        help="Path to save review queue CSV",
    )
    review_queue_parser.set_defaults(func=review_queue)


    # dirty parser
    dirty_parser = subparsers.add_parser(
        "make-dirty-coco",
        help="Generate a dirty COCO annotation JSON from a clean COCO annotation",
    )
    dirty_parser.add_argument(
        "--annotation",
        required=True,
        type=Path,
        help="Path to clean COCO annotation JSON",
    )
    dirty_parser.add_argument(
        "--output-annotation",
        required=False,
        type=Path,
        default=Path(
            "data/sample/coco-mini-dirty/annotations/instances_coco_mini_dirty.json"
        ),
        help="Path to save dirty COCO annotation JSON",
    )
    dirty_parser.add_argument(
        "--output-manifest",
        required=False,
        type=Path,
        default=Path("data/sample/coco-mini-dirty/corruption_manifest.json"),
        help="Path to save corruption manifest JSON",
    )
    dirty_parser.set_defaults(func=make_dirty_coco)


    # compare parser
    compare_parser = subparsers.add_parser(
        "compare-reports",
        help="Compare clean and dirty COCO quality reports",
    )
    compare_parser.add_argument(
        "--clean-report",
        required=True,
        type=Path,
        help="Path to clean quality report JSON",
    )
    compare_parser.add_argument(
        "--dirty-report",
        required=True,
        type=Path,
        help="Path to dirty quality report JSON",
    )
    compare_parser.add_argument(
        "--output-md",
        required=False,
        type=Path,
        default=Path("reports/clean_vs_dirty_report.md"),
        help="Path to save comparison Markdown report",
    )
    compare_parser.add_argument(
        "--output-csv",
        required=False,
        type=Path,
        default=Path("reports/clean_vs_dirty_summary.csv"),
        help="Path to save comparison CSV summary",
    )
    compare_parser.set_defaults(func=compare_reports)


    args = parser.parse_args()
    args.func(args)
    

if __name__ == "__main__":
    main()
