# AI Training Dataset Quality Management Toolkit

A lightweight pre-flight quality management toolkit for COCO-format object detection datasets.

This project validates dataset integrity, analyzes annotation distributions, enriches detected issues with an issue catalog, and converts them into a human-reviewable queue. It is designed as a small, reproducible CLI workflow for AI training data quality assurance.

[한국어 README](README.ko.md)

---

## Why this project exists

Object detection models learn from image–annotation pairs.

In COCO-format datasets:

- `bbox` is used as the localization target.
- `category_id` is used as the classification target.
- `image_id` and `file_name` connect images with their ground-truth annotations.

If annotation structure, image–annotation references, bbox coordinates, or category mappings are broken, the model may learn from invalid or misleading training targets.

This toolkit asks:

- Can the dataset be loaded reliably by a training pipeline?
- Are images and annotations correctly linked?
- Are bbox coordinates and sizes physically valid?
- Are category IDs consistent with the class ontology?
- Is the dataset distribution skewed by class or object size?
- Which samples should be reviewed first, and why?

---

## What it does

### Dataset inspection

- Loads COCO annotation JSON files.
- Summarizes image, annotation, and category counts.
- Checks missing image files.

### Validation

- **Schema validation**
  - Required top-level keys
  - Required fields
  - Duplicate IDs
- **Reference validation**
  - Unknown `image_id` references
  - Missing image files
  - Images without annotations
- **BBox validation**
  - Missing bbox values
  - Invalid bbox format
  - Non-numeric bbox values
  - Non-positive width or height
  - Negative coordinates
  - Bboxes outside image boundaries
- **Category validation**
  - Duplicate category IDs or names
  - Missing `category_id`
  - Unknown `category_id` references

### Distribution analysis

- Class distribution by instance count and image count
- BBox area and normalized area
- BBox aspect ratio
- Small / medium / large object distribution

### Quality report

Generates a JSON quality report that combines validation results and distribution analysis.

Each detected issue can be enriched with:

- issue description
- why it matters
- likely causes
- suggested actions
- recommended owner
- judgement level
- blocking level
- impact level

### Review queue

Converts validation issues into a CSV review queue.

The review queue is intended to help reviewers understand:

- what issue was detected
- which image or annotation is affected
- why the issue matters
- who should review it
- what action is recommended
- how urgent the issue is in a rule-based triage workflow

### Dirty COCO generator

Creates a schema-valid dirty COCO annotation file from a clean annotation file by injecting controlled errors.

Injected examples include:

- missing image file references
- unknown `image_id` references
- bboxes outside image boundaries
- bboxes with non-positive size
- unknown `category_id` references
- duplicated category names
- images without annotations

### Clean vs Dirty comparison

Compares clean and dirty quality reports and exports the result as Markdown and CSV.

This validates whether controlled corruptions are detected and routed into the review workflow.

---

## Pipeline

```text
COCO Annotation JSON
        ↓
COCO Dataset Loader
        ↓
Schema / Reference / BBox / Category Validation
        ↓
Class & BBox Distribution Analysis
        ↓
Quality Report JSON
        ↓
Issue Catalog Enrichment
        ↓
Review Queue CSV
        ↓
Clean vs Dirty Quality Comparison
```

---

## Requirements

- Python >= 3.10
- Tested with Python 3.11

The project currently uses mostly Python standard-library modules. Run commands with `PYTHONPATH=src`.

```bash
PYTHONPATH=src python -m dq_toolkit.cli --help
```

---

## Quick start

### Inspect a COCO dataset

```bash
PYTHONPATH=src python -m dq_toolkit.cli inspect-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images
```

### Validate a COCO dataset

```bash
PYTHONPATH=src python -m dq_toolkit.cli validate-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images
```

### Analyze class and bbox distributions

```bash
PYTHONPATH=src python -m dq_toolkit.cli analyze-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --output-csv reports/class_distribution.csv \
  --bbox-output-csv reports/bbox_distribution.csv
```

### Generate a quality report

```bash
PYTHONPATH=src python -m dq_toolkit.cli report-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images \
  --output reports/quality_report.json
```

### Generate a review queue

```bash
PYTHONPATH=src python -m dq_toolkit.cli review-queue \
  --report reports/quality_report.json \
  --output reports/review_queue.csv
```

### Generate a dirty COCO annotation file

```bash
PYTHONPATH=src python -m dq_toolkit.cli make-dirty-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --output-annotation data/sample/coco-mini-dirty/annotations/instances_coco_mini_dirty.json \
  --output-manifest data/sample/coco-mini-dirty/corruption_manifest.json
```

### Compare clean and dirty reports

```bash
PYTHONPATH=src python -m dq_toolkit.cli compare-reports \
  --clean-report reports/quality_report.json \
  --dirty-report reports/dirty_quality_report.json \
  --output-md reports/clean_vs_dirty_report.md \
  --output-csv reports/clean_vs_dirty_summary.csv
```

---

## Example result

Example validation summary after injecting controlled corruptions:

| Validation Section | Clean | Dirty | Delta |
| --- | ---: | ---: | ---: |
| schema | 0 | 0 | 0 |
| reference | 0 | 3 | +3 |
| bbox | 0 | 2 | +2 |
| category | 0 | 2 | +2 |

Example review queue summary:

| Priority Tier | Clean | Dirty | Delta |
| --- | ---: | ---: | ---: |
| P0 | 0 | 2 | +2 |
| P1 | 0 | 4 | +4 |
| P2 | 0 | 1 | +1 |
| P3 | 0 | 0 | 0 |

The exact numbers may vary depending on the COCO subset and injected corruption policy.

---

## Review priority tiers

`priority_tier` is not an objective data quality score. It is a rule-based triage label used to sort review work.

| Tier | Meaning | Example |
| --- | --- | --- |
| P0 | Blocks dataset loading or training-sample construction | missing image file, unknown `image_id` |
| P1 | Directly corrupts model training targets | invalid bbox, unknown `category_id` |
| P2 | Requires human review | image without annotations |
| P3 | Requires policy, ontology, or traceability review | duplicated category name |

Future versions can replace or augment this rule-based baseline with review-log-driven prioritization.

---

## Design principles

### Do not automatically fix every issue

This toolkit does not assume that every detected issue should be automatically modified.

Operations such as bbox clipping, category remapping, or annotation deletion depend on dataset purpose and labeling policy. Even when an automatic fix is technically possible, it should be applied through dry-run output or human approval.

### Separate automatic checks from human review

| Judgement Level | Meaning |
| --- | --- |
| `automatic` | Can be detected through deterministic rules |
| `human_review` | Requires a reviewer to inspect the sample |
| `policy_review` | Requires labeling policy or ontology review |
| `expert_review` | Requires domain expert judgement |

### Treat priority as triage, not truth

Priority tiers help route review work. They may change depending on dataset purpose, model use case, class risk, and reviewer capacity.

---

## Project structure

```text
src/dq_toolkit/
├── analysis/
│   ├── bbox_distribution.py
│   └── class_distribution.py
├── checks/
│   ├── bbox.py
│   ├── category.py
│   ├── reference.py
│   └── schema.py
├── datasets/
│   └── dirty_coco.py
├── io/
│   └── coco.py
├── report/
│   ├── compare_reports.py
│   └── report_builder.py
├── review/
│   ├── issue_catalog.py
│   └── review_queue.py
└── cli.py
```

---


## Future work

- Duplicate and near-duplicate image detection
- Train/validation/test leakage detection
- Image quality checks
  - corrupted image
  - low resolution
  - blur
  - blank image
- Missing-label suspicion using model predictions
- Label consistency checks for similar images or video frames
- Review result logging
- Worker/reviewer quality metrics
- Model-performance-based error analysis
- Streamlit dashboard
- CVAT / Label Studio export integration


---

## Portfolio positioning

This project demonstrates the ability to:

- understand the AI training data lifecycle
- inspect COCO-format object detection datasets
- design annotation-level validation checks
- connect dataset quality issues to model training targets
- distinguish automatic checks from human, policy, and expert review cases
- convert raw validation issues into explainable review tasks
- generate controlled dirty datasets for validation testing
- compare clean and dirty quality reports
- design a human-in-the-loop dataset quality management workflow

Core message:

> Training data quality management is not just about finding broken files. It is about identifying which data issues affect model learning, explaining why they matter, and routing them into the right review or improvement workflow.
