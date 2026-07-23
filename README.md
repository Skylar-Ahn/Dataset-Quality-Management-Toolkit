# Dataset-Quality-Management-Toolkit

```markdown
This project aim to separates automatically detectable issues from human-review and expert-review cases, and provides structured reports for downstream review workflows.

## Features

- COCO annotation inspection
- Schema validation
- Reference validation
- BBox validation
- Category validation
- Class distribution analysis
- BBox distribution analysis
- Quality report JSON generation

## Quick Start

```bash
PYTHONPATH=src python -m dq_toolkit.cli inspect-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images
```

```shell
PYTHONPATH=src python -m dq_toolkit.cli analyze-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --output-csv reports/class_distribution.csv \
  --bbox-output-csv reports/bbox_distribution.csv
```

```shell
PYTHONPATH=src python -m dq_toolkit.cli report-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images \
  --output reports/quality_report.json
```