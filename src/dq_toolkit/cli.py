import argparse
from pathlib import Path

from dq_toolkit.checks.bbox import validate_bboxes
from dq_toolkit.checks.category import validate_categories
from dq_toolkit.checks.reference import validate_references
from dq_toolkit.checks.schema import validate_coco_schema
from dq_toolkit.io.coco import load_coco_annotation, summarize_coco_dataset


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dataset quality management toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
