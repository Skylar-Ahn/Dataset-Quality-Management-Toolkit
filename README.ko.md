# AI 학습데이터 품질관리 Toolkit

COCO-format object detection 데이터셋을 대상으로 하는 경량 pre-flight 품질관리 도구입니다.

이 프로젝트는 데이터셋의 구조적 무결성, image-annotation 참조 관계, bbox/category 유효성, 데이터 분포를 검사하고, 탐지된 이슈를 사람이 검수할 수 있는 Review Queue로 변환합니다. 단순 COCO validator가 아니라, 자동 검사 가능한 이슈와 사람/정책 검수가 필요한 이슈를 분리하는 Human-in-the-Loop 품질관리 workflow를 목표로 합니다.

[English README](README.md)

---

## 프로젝트 목적

Object detection 모델은 이미지와 annotation의 쌍을 바탕으로 객체의 위치와 class를 학습합니다.

COCO-format annotation에서:

- `bbox`는 localization target으로 사용됩니다.
- `category_id`는 classification target으로 사용됩니다.
- `image_id`와 `file_name`은 이미지와 정답 라벨을 연결합니다.

따라서 annotation 구조, image-annotation 참조 관계, bbox 좌표, category mapping에 오류가 있으면 단순한 파일 문제가 아니라 모델 학습의 정답 신호가 왜곡될 수 있습니다.

이 프로젝트는 다음 질문에 답하기 위해 만들어졌습니다.

- 데이터셋이 학습 파이프라인에서 안정적으로 읽힐 수 있는가?
- image와 annotation의 연결 관계가 올바른가?
- bbox 좌표와 크기가 물리적으로 유효한가?
- `category_id`와 class ontology가 일관적인가?
- class/object size 분포가 특정 방향으로 치우쳐 있지는 않은가?
- 사람이 검수해야 할 샘플은 무엇이고, 어떤 이유로 검수해야 하는가?

---

## 주요 기능

### Dataset inspection

- COCO annotation JSON을 로드합니다.
- image / annotation / category 개수를 요약합니다.
- missing image file 개수를 확인합니다.

### Validation

- **Schema validation**
  - top-level key 검사
  - 필수 필드 검사
  - id 중복 검사
- **Reference validation**
  - 존재하지 않는 `image_id` 참조 검사
  - 실제 이미지 파일 누락 검사
  - annotation이 없는 image 탐지
- **BBox validation**
  - bbox 누락
  - bbox format 오류
  - non-numeric bbox
  - width/height가 0 이하인 bbox
  - 음수 좌표
  - 이미지 경계를 벗어난 bbox
- **Category validation**
  - category id/name 중복
  - annotation의 `category_id` 누락
  - 존재하지 않는 `category_id` 참조

### Distribution analysis

- category별 instance count와 image count
- bbox area와 normalized area
- bbox aspect ratio
- small / medium / large object 비율

### Quality report

validation 결과와 distribution analysis 결과를 하나의 JSON report로 저장합니다.

각 issue에는 다음 정보를 붙일 수 있습니다.

- issue 설명
- 왜 중요한지
- 가능한 원인
- 권장 조치
- 추천 담당자
- 판단 수준
- blocking level
- impact level

### Review queue

Quality Report의 validation issue를 사람이 처리 가능한 CSV 작업 목록으로 변환합니다.

Review Queue는 검수자가 다음을 이해할 수 있도록 돕습니다.

- 어떤 issue가 탐지되었는지
- 어떤 image 또는 annotation이 영향을 받는지
- 왜 검수해야 하는지
- 누가 검토하는 것이 적절한지
- 어떤 조치가 권장되는지
- rule-based triage 기준에서 어느 정도 우선순위인지

### Dirty COCO generator

clean COCO annotation을 기반으로 schema-valid dirty annotation을 생성합니다.

주입되는 오류 예시는 다음과 같습니다.

- missing image file reference
- unknown `image_id` reference
- bbox out of image boundary
- bbox non-positive size
- unknown `category_id` reference
- duplicated category name
- image without annotations

### Clean vs Dirty comparison

clean quality report와 dirty quality report를 비교하여 Markdown/CSV 리포트를 생성합니다.

이를 통해 controlled corruption이 실제로 탐지되고 Review Queue로 연결되는지 확인할 수 있습니다.

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
- Python 3.11에서 테스트

현재 프로젝트는 대부분 Python 표준 라이브러리 중심으로 동작합니다. 실행 시에는 `PYTHONPATH=src`를 지정합니다.

```bash
PYTHONPATH=src python -m dq_toolkit.cli --help
```

---

## Quick start

### COCO dataset inspection

```bash
PYTHONPATH=src python -m dq_toolkit.cli inspect-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images
```

### COCO dataset validation

```bash
PYTHONPATH=src python -m dq_toolkit.cli validate-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images
```

### Class / bbox distribution analysis

```bash
PYTHONPATH=src python -m dq_toolkit.cli analyze-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --output-csv reports/class_distribution.csv \
  --bbox-output-csv reports/bbox_distribution.csv
```

### Quality report 생성

```bash
PYTHONPATH=src python -m dq_toolkit.cli report-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --image-dir data/sample/coco-mini/images \
  --output reports/quality_report.json
```

### Review queue 생성

```bash
PYTHONPATH=src python -m dq_toolkit.cli review-queue \
  --report reports/quality_report.json \
  --output reports/review_queue.csv
```

### Dirty COCO annotation 생성

```bash
PYTHONPATH=src python -m dq_toolkit.cli make-dirty-coco \
  --annotation data/sample/coco-mini/annotations/instances_coco_mini.json \
  --output-annotation data/sample/coco-mini-dirty/annotations/instances_coco_mini_dirty.json \
  --output-manifest data/sample/coco-mini-dirty/corruption_manifest.json
```

### Clean vs Dirty report 비교

```bash
PYTHONPATH=src python -m dq_toolkit.cli compare-reports \
  --clean-report reports/quality_report.json \
  --dirty-report reports/dirty_quality_report.json \
  --output-md reports/clean_vs_dirty_report.md \
  --output-csv reports/clean_vs_dirty_summary.csv
```

---

## 예시 결과

controlled corruption을 주입한 dirty dataset과 clean dataset을 비교한 예시입니다.

| Validation Section | Clean | Dirty | Delta |
| --- | ---: | ---: | ---: |
| schema | 0 | 0 | 0 |
| reference | 0 | 3 | +3 |
| bbox | 0 | 2 | +2 |
| category | 0 | 2 | +2 |

Review Queue 예시:

| Priority Tier | Clean | Dirty | Delta |
| --- | ---: | ---: | ---: |
| P0 | 0 | 2 | +2 |
| P1 | 0 | 4 | +4 |
| P2 | 0 | 1 | +1 |
| P3 | 0 | 0 | 0 |

실제 숫자는 사용한 COCO subset과 dirty corruption 정책에 따라 달라질 수 있습니다.

---

## Review priority tier

`priority_tier`는 절대적인 데이터 품질 점수가 아닙니다. 현재 MVP에서는 검수 작업을 정렬하기 위한 rule-based triage label로 사용합니다.

| Tier | Meaning | Example |
| --- | --- | --- |
| P0 | Dataset loading 또는 training sample 구성을 막는 문제 | missing image file, unknown `image_id` |
| P1 | 모델 학습 target을 직접 오염시키는 문제 | invalid bbox, unknown `category_id` |
| P2 | 사람 검수가 필요한 이슈 | image without annotations |
| P3 | 정책, ontology, traceability 검토가 필요한 이슈 | duplicated category name |

향후 실제 review log가 쌓이면 이 rule-based baseline을 review-log 기반 prioritization으로 확장할 수 있습니다.

---

## 설계 원칙

### 모든 이슈를 자동 수정하지 않는다

이 프로젝트는 탐지된 모든 품질 문제를 자동으로 수정하는 것을 목표로 하지 않습니다.

bbox clipping, category remapping, annotation deletion 같은 작업은 데이터셋 목적과 라벨링 정책에 따라 달라질 수 있습니다. 따라서 자동 수정이 가능한 경우에도 dry-run 결과 또는 human approval을 전제로 합니다.

### 자동 검사와 사람 검수를 분리한다

| Judgement Level | Meaning |
| --- | --- |
| `automatic` | 규칙 기반으로 자동 판단 가능한 이슈 |
| `human_review` | 사람이 샘플을 확인해야 하는 이슈 |
| `policy_review` | 라벨링 정책 또는 ontology 검토가 필요한 이슈 |
| `expert_review` | 도메인 전문가 판단이 필요한 이슈 |

### Priority는 truth가 아니라 triage다

Priority tier는 검수 작업을 정렬하기 위한 기준입니다. 이 값은 데이터셋의 목적, 모델 사용 맥락, class 위험도, reviewer 가용성에 따라 달라질 수 있습니다.

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

## Scope and limitations

현재 MVP 범위:

- COCO-format object detection annotation
- 2D bbox validation
- category id/name validation
- class distribution analysis
- bbox distribution analysis
- issue catalog enrichment
- rule-based review queue generation
- controlled dirty dataset generation

현재 한계:

- bbox가 실제 object를 tight하게 감싸는지는 자동 판단하지 않습니다.
- missing label 여부는 model prediction 또는 human review 없이 직접 판단하지 않습니다.
- train/validation/test leakage detection은 아직 구현하지 않았습니다.
- worker quality metrics는 실제 reviewer log 없이는 계산하지 않습니다.
- 모델 성능에 미친 영향은 아직 측정하지 않았습니다.
- robotics multimodal consistency check는 아직 다루지 않습니다.

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
- Robotics multimodal quality checks
  - video-sensor timestamp mismatch
  - joint signal range violation
  - frame drop
  - episode length anomaly
  - task/subtask label consistency

---

## Portfolio positioning

이 프로젝트는 다음 역량을 보여줍니다.

- AI training data lifecycle 이해
- COCO-format object detection dataset inspection
- annotation-level validation check 설계
- dataset quality issue와 model training target의 연결 이해
- automatic / human / policy / expert review case 구분
- raw validation issue를 설명 가능한 review task로 변환
- controlled dirty dataset을 활용한 validation test 설계
- clean and dirty quality report 비교
- Human-in-the-Loop dataset quality management workflow 설계

핵심 메시지:

> Training data quality management is not just about finding broken files. It is about identifying which data issues affect model learning, explaining why they matter, and routing them into the right review or improvement workflow.
