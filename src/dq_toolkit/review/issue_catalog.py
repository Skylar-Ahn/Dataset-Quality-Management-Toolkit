from dataclasses import asdict, dataclass
from typing import Any, Literal


Language = Literal["ko", "en"]
SUPPORTED_LANGUAGES = {"ko", "en"}


@dataclass(frozen=True)
class IssueDefinition:
    """
    [P1] A structured definition for one dataset quality issue.

    The catalog does not directly decide review_priority_score.
    Instead, it provides explainable fields that the Review Queue can use
    for triage, ownership, and suggested actions.
    """
    check_name: str
    title: str
    description: str
    why_it_matters: str
    likely_causes: list[str]
    suggested_actions: list[str]
    recommended_owner: str
    judgement_level: str
    auto_fixable: str
    default_impact_level: str
    blocking_level: str
    review_urgency_hint: str
    priority_policy_note: str


# [P2] Language-independent operational metadata.
# Text fields are separated into ISSUE_TEXTS so Korean/English output can be switched.
ISSUE_METADATA: dict[str, dict[str, str]] = {
    "annotation_file_missing": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "critical",
        "blocking_level": "blocks_dataset_loading",
        "review_urgency_hint": "high",
    },
    "json_decode_error": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "critical",
        "blocking_level": "blocks_dataset_loading",
        "review_urgency_hint": "high",
    },
    "top_level_key_missing": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "critical",
        "blocking_level": "blocks_dataset_loading",
        "review_urgency_hint": "high",
    },
    "top_level_key_type": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "critical",
        "blocking_level": "blocks_dataset_loading",
        "review_urgency_hint": "high",
    },
    "image_id_duplicate": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "high",
        "blocking_level": "affects_dataset_integrity",
        "review_urgency_hint": "high",
    },
    "annotation_id_duplicate": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "medium",
        "blocking_level": "affects_traceability",
        "review_urgency_hint": "medium",
    },
    "annotation_unknown_image_id": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "critical",
        "blocking_level": "blocks_training_sample",
        "review_urgency_hint": "high",
    },
    "missing_image_file": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "critical",
        "blocking_level": "blocks_training_sample",
        "review_urgency_hint": "high",
    },
    "image_without_annotations": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "no",
        "default_impact_level": "medium",
        "blocking_level": "needs_human_check",
        "review_urgency_hint": "medium",
    },
    "image_file_name_invalid": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "high",
        "blocking_level": "blocks_training_sample",
        "review_urgency_hint": "high",
    },
    "bbox_missing": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "no",
        "default_impact_level": "high",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "high",
    },
    "bbox_format": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "no",
        "default_impact_level": "high",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "high",
    },
    "bbox_non_numeric": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "high",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "high",
    },
    "bbox_non_positive_size": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "no",
        "default_impact_level": "high",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "high",
    },
    "bbox_negative_coordinate": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "dry_run_only",
        "default_impact_level": "medium",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "medium",
    },
    "bbox_out_of_image": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "dry_run_only",
        "default_impact_level": "high",
        "blocking_level": "affects_annotation_quality",
        "review_urgency_hint": "high",
    },
    "image_size_missing": {
        "recommended_owner": "data_engineer",
        "judgement_level": "automatic",
        "auto_fixable": "with_approval",
        "default_impact_level": "medium",
        "blocking_level": "limits_quality_check",
        "review_urgency_hint": "medium",
    },
    "category_id_duplicate": {
        "recommended_owner": "labeling_policy_manager",
        "judgement_level": "human_review",
        "auto_fixable": "with_approval",
        "default_impact_level": "high",
        "blocking_level": "affects_class_mapping",
        "review_urgency_hint": "high",
    },
    "category_name_duplicate": {
        "recommended_owner": "labeling_policy_manager",
        "judgement_level": "policy_review",
        "auto_fixable": "no",
        "default_impact_level": "medium",
        "blocking_level": "needs_policy_check",
        "review_urgency_hint": "medium",
    },
    "annotation_category_id_missing": {
        "recommended_owner": "labeling_reviewer",
        "judgement_level": "human_review",
        "auto_fixable": "no",
        "default_impact_level": "high",
        "blocking_level": "affects_class_mapping",
        "review_urgency_hint": "high",
    },
    "annotation_unknown_category_id": {
        "recommended_owner": "labeling_policy_manager",
        "judgement_level": "human_review",
        "auto_fixable": "with_approval",
        "default_impact_level": "high",
        "blocking_level": "affects_class_mapping",
        "review_urgency_hint": "high",
    },
}


# [P3] Localized text for each issue.
# The output language is selected by get_issue_definition(..., language="ko" | "en").
ISSUE_TEXTS: dict[str, dict[str, dict[str, Any]]] = {
    "ko": {
        "annotation_file_missing": {
            "title": "Annotation file is missing",
            "description": "COCO annotation JSON 파일을 찾을 수 없는 경우입니다.",
            "why_it_matters": (
                "annotation 파일이 없으면 이미지와 정답 라벨을 연결할 수 없어 "
                "dataset loading과 후속 품질검사를 진행할 수 없습니다."
            ),
            "likely_causes": [
                "annotation 파일 경로가 잘못 지정됨",
                "파일 다운로드 또는 복사 과정에서 누락됨",
                "데이터셋 디렉토리 구조가 예상과 다름",
            ],
            "suggested_actions": [
                "annotation JSON 파일 경로를 확인합니다.",
                "원본 데이터셋에서 annotation 파일을 복구합니다.",
                "데이터셋 디렉토리 구조를 README 또는 config와 맞춥니다.",
            ],
            "priority_policy_note": (
                "annotation file이 없으면 dataset 자체를 검사하거나 학습할 수 없으므로 "
                "학습 가능한 데이터 패키지를 만들기 전에 먼저 해결해야 합니다."
            ),
        },
        "json_decode_error": {
            "title": "Annotation JSON cannot be parsed",
            "description": "annotation 파일이 올바른 JSON 형식이 아닌 경우입니다.",
            "why_it_matters": (
                "JSON parsing이 실패하면 COCO loader가 annotation을 읽을 수 없고, "
                "schema/reference/bbox/category validation을 수행할 수 없습니다."
            ),
            "likely_causes": [
                "JSON 파일이 중간에 잘림",
                "수동 편집 중 문법 오류 발생",
                "잘못된 export 파일 사용",
            ],
            "suggested_actions": [
                "JSON validator로 파일 문법을 확인합니다.",
                "라벨링 툴에서 annotation을 다시 export합니다.",
                "파일이 완전히 다운로드되었는지 확인합니다.",
            ],
            "priority_policy_note": "JSON parsing 오류는 모든 후속 검사를 막기 때문에 P0 수준으로 먼저 처리합니다.",
        },
        "top_level_key_missing": {
            "title": "Required COCO top-level key is missing",
            "description": "COCO JSON에 images, annotations, categories 같은 필수 key가 없는 경우입니다.",
            "why_it_matters": (
                "COCO-format object detection dataset은 images, annotations, categories 구조를 기준으로 "
                "이미지와 bbox/category target을 연결합니다. 필수 구조가 없으면 학습 파이프라인이 "
                "정답 라벨을 안정적으로 읽을 수 없습니다."
            ),
            "likely_causes": [
                "COCO가 아닌 다른 format의 annotation을 사용함",
                "format 변환 스크립트 오류",
                "subset 생성 과정에서 일부 key가 누락됨",
            ],
            "suggested_actions": [
                "annotation 파일이 COCO-format인지 확인합니다.",
                "format 변환 스크립트를 점검합니다.",
                "원본 COCO annotation에서 subset을 다시 생성합니다.",
            ],
            "priority_policy_note": "COCO 필수 구조가 없으면 downstream validation이 신뢰할 수 없으므로 먼저 해결합니다.",
        },
        "top_level_key_type": {
            "title": "Top-level COCO key has invalid type",
            "description": "images, annotations, categories 값이 list가 아닌 경우입니다.",
            "why_it_matters": (
                "COCO loader는 images, annotations, categories를 list로 순회한다고 가정합니다. "
                "타입이 맞지 않으면 validation과 학습 데이터 로딩이 실패할 수 있습니다."
            ),
            "likely_causes": [
                "annotation 변환 과정의 serialization 오류",
                "수동 편집 오류",
                "잘못된 annotation schema 사용",
            ],
            "suggested_actions": [
                "COCO schema에 맞게 images, annotations, categories를 list로 수정합니다.",
                "annotation export 또는 변환 스크립트를 재실행합니다.",
            ],
            "priority_policy_note": "top-level 구조 타입 오류는 dataset parser 실패로 이어질 수 있어 먼저 처리합니다.",
        },
        "image_id_duplicate": {
            "title": "Duplicated image id",
            "description": "images 목록 안에서 같은 image id가 중복된 경우입니다.",
            "why_it_matters": (
                "image_id는 annotation이 어떤 이미지에 속하는지 연결하는 key입니다. "
                "중복 image_id가 있으면 annotation-image matching이 모호해집니다."
            ),
            "likely_causes": [
                "여러 dataset을 병합하면서 id 재할당을 하지 않음",
                "subset 생성 스크립트 오류",
            ],
            "suggested_actions": [
                "image id를 dataset 전체에서 unique하게 재할당합니다.",
                "annotation의 image_id도 함께 갱신합니다.",
                "수정 전후 id mapping을 기록합니다.",
            ],
            "priority_policy_note": "image_id 중복은 annotation 매칭을 모호하게 만들기 때문에 reference validation 이슈와 함께 우선 검토합니다.",
        },
        "annotation_id_duplicate": {
            "title": "Duplicated annotation id",
            "description": "annotations 목록 안에서 같은 annotation id가 중복된 경우입니다.",
            "why_it_matters": "annotation id가 중복되면 오류 추적, review queue 생성, 수정 이력 관리가 어려워집니다.",
            "likely_causes": [
                "여러 annotation 파일을 병합하면서 id 재할당을 하지 않음",
                "subset 생성 스크립트 오류",
            ],
            "suggested_actions": [
                "annotation id를 unique하게 재할당합니다.",
                "수정 전후 id mapping을 기록합니다.",
            ],
            "priority_policy_note": "학습 자체를 즉시 막지 않을 수 있지만, 검수 이력과 수정 추적을 어렵게 만들기 때문에 정리 대상입니다.",
        },
        "annotation_unknown_image_id": {
            "title": "Annotation references unknown image",
            "description": "annotation의 image_id가 images 목록에 존재하지 않는 경우입니다.",
            "why_it_matters": (
                "object detection 학습은 image와 GT annotation의 쌍으로 이루어집니다. "
                "annotation이 존재하지 않는 image_id를 참조하면 정답 라벨이 어떤 이미지에 속하는지 알 수 없습니다."
            ),
            "likely_causes": [
                "이미지 subset 생성 후 annotation filtering이 제대로 되지 않음",
                "여러 annotation 파일을 병합하면서 image_id mapping이 깨짐",
                "일부 image metadata가 누락됨",
            ],
            "suggested_actions": [
                "annotation의 image_id가 images 목록에 존재하는지 확인합니다.",
                "해당 annotation을 제거하거나 올바른 image_id로 수정합니다.",
                "subset 생성 스크립트의 image filtering 로직을 점검합니다.",
            ],
            "priority_policy_note": "image와 annotation의 연결이 깨진 샘플은 학습 target으로 사용할 수 없으므로 우선 정리합니다.",
        },
        "missing_image_file": {
            "title": "Image file is missing",
            "description": "COCO JSON의 images에는 등록되어 있지만 실제 이미지 파일이 없는 경우입니다.",
            "why_it_matters": (
                "이미지 파일이 없으면 DataLoader가 샘플을 읽을 수 없고, "
                "해당 image에 연결된 annotation도 학습에 사용할 수 없습니다."
            ),
            "likely_causes": [
                "이미지 파일 복사 또는 다운로드 누락",
                "file_name 경로 오류",
                "이미지 디렉토리와 annotation JSON이 서로 다른 버전임",
            ],
            "suggested_actions": [
                "누락된 이미지 파일을 원본 데이터셋에서 복구합니다.",
                "file_name과 실제 파일 경로가 일치하는지 확인합니다.",
                "복구가 불가능하면 해당 image와 연결 annotation을 제외할지 검토합니다.",
            ],
            "priority_policy_note": "missing image file은 개별 샘플 로딩을 막으므로 trainable dataset 구성 단계에서 우선 처리합니다.",
        },
        "image_without_annotations": {
            "title": "Image has no annotations",
            "description": "images 목록에는 있지만 연결된 annotation이 하나도 없는 경우입니다.",
            "why_it_matters": (
                "object detection에서는 객체가 없는 negative image일 수도 있지만, "
                "라벨 누락일 수도 있습니다. 자동으로 오류라고 단정하면 안 되고 검수 기준이 필요합니다."
            ),
            "likely_causes": [
                "정상적인 negative sample",
                "객체 라벨 누락",
                "subset 생성 과정에서 annotation만 제거됨",
            ],
            "suggested_actions": [
                "해당 이미지가 negative sample로 의도된 것인지 확인합니다.",
                "객체가 보이는데 annotation이 없다면 재라벨링 대상으로 보냅니다.",
                "negative image를 허용하는 데이터셋 정책인지 확인합니다.",
            ],
            "priority_policy_note": "negative sample일 수도 있으므로 error처럼 즉시 수정하지 않고, 정책 확인 또는 샘플 검수 대상으로 분류합니다.",
        },
        "image_file_name_invalid": {
            "title": "Image file name is invalid",
            "description": "image metadata의 file_name이 비어 있거나 문자열이 아닌 경우입니다.",
            "why_it_matters": "file_name이 유효하지 않으면 image metadata와 실제 이미지 파일을 연결할 수 없습니다.",
            "likely_causes": [
                "metadata 생성 오류",
                "annotation 변환 스크립트 오류",
                "수동 편집 오류",
            ],
            "suggested_actions": [
                "file_name 값을 실제 이미지 파일명으로 수정합니다.",
                "metadata 생성 스크립트를 점검합니다.",
            ],
            "priority_policy_note": "file_name이 유효하지 않으면 실제 이미지 파일과 연결할 수 없으므로 missing image file과 유사하게 처리합니다.",
        },
        "bbox_missing": {
            "title": "BBox is missing",
            "description": "annotation에 bbox 값이 없는 경우입니다.",
            "why_it_matters": (
                "bbox는 object detection 모델의 localization target입니다. "
                "bbox가 없으면 해당 객체는 위치 학습에 사용할 수 없습니다."
            ),
            "likely_causes": [
                "라벨링 작업 누락",
                "annotation export 오류",
                "task format 변환 오류",
            ],
            "suggested_actions": [
                "annotation tool에서 bbox를 다시 확인합니다.",
                "필요하면 해당 객체를 재라벨링합니다.",
            ],
            "priority_policy_note": "bbox가 없는 object annotation은 detection 학습 target으로 불완전하므로 우선 검수 대상입니다.",
        },
        "bbox_format": {
            "title": "BBox format is invalid",
            "description": "bbox가 COCO 형식 [x, y, width, height]를 따르지 않는 경우입니다.",
            "why_it_matters": "bbox 형식이 잘못되면 model training 과정에서 localization target이 잘못 해석됩니다.",
            "likely_causes": [
                "YOLO/KITTI format을 COCO로 변환하는 과정의 오류",
                "bbox 좌표계를 잘못 사용함",
                "bbox list 길이가 잘못됨",
            ],
            "suggested_actions": [
                "bbox format이 [x, y, width, height]인지 확인합니다.",
                "format 변환 스크립트를 점검합니다.",
            ],
            "priority_policy_note": "bbox format 오류는 좌표 해석 전체를 깨뜨릴 수 있으므로 bbox 관련 오류 중 우선 검토합니다.",
        },
        "bbox_non_numeric": {
            "title": "BBox contains non-numeric value",
            "description": "bbox 안에 숫자가 아닌 값이 들어 있는 경우입니다.",
            "why_it_matters": (
                "bbox 값은 IoU 계산, bbox regression target, augmentation 좌표 변환에 사용되므로 "
                "숫자형 값이어야 합니다."
            ),
            "likely_causes": [
                "JSON serialization 오류",
                "수동 편집 오류",
                "결측값이 문자열로 저장됨",
            ],
            "suggested_actions": [
                "bbox 값을 숫자형으로 변환할 수 있는지 확인합니다.",
                "변환할 수 없는 경우 해당 annotation을 재검수합니다.",
            ],
            "priority_policy_note": "숫자형이 아닌 bbox는 학습 파이프라인에서 오류를 만들 수 있어 우선 정리합니다.",
        },
        "bbox_non_positive_size": {
            "title": "BBox has non-positive width or height",
            "description": "bbox width 또는 height가 0 이하인 경우입니다.",
            "why_it_matters": (
                "면적이 없거나 음수인 bbox는 실제 객체 영역을 나타낼 수 없고, "
                "IoU 계산과 bbox regression target을 불안정하게 만듭니다."
            ),
            "likely_causes": [
                "라벨링 중 bbox가 잘못 생성됨",
                "좌표 변환 과정에서 width/height 계산 오류",
                "잘못된 format 변환",
            ],
            "suggested_actions": [
                "annotation tool에서 bbox를 다시 확인합니다.",
                "좌표 변환 로직을 점검합니다.",
                "실제 객체가 없다면 annotation 제거를 검토합니다.",
            ],
            "priority_policy_note": "면적이 없는 bbox는 object localization target으로 사용할 수 없으므로 검수 우선순위가 높습니다.",
        },
        "bbox_negative_coordinate": {
            "title": "BBox has negative coordinate",
            "description": "bbox의 x 또는 y 좌표가 음수인 경우입니다.",
            "why_it_matters": (
                "음수 좌표는 bbox가 이미지 좌상단 밖에서 시작한다는 뜻이며, "
                "이미지 좌표계와 annotation 좌표계가 맞지 않을 가능성이 있습니다."
            ),
            "likely_causes": [
                "crop 또는 resize 후 좌표 보정 누락",
                "라벨링 툴 export 오류",
                "좌표계 변환 오류",
            ],
            "suggested_actions": [
                "이미지 전처리와 annotation 좌표 변환이 일치하는지 확인합니다.",
                "bbox가 실제 객체를 올바르게 감싸는지 검수합니다.",
                "자동 clipping은 dry-run 후보로만 표시하고 실제 반영은 검수 후 결정합니다.",
            ],
            "priority_policy_note": "음수 좌표는 좌표계 변환 오류일 수 있으므로 bbox_out_of_image와 함께 검토합니다.",
        },
        "bbox_out_of_image": {
            "title": "BBox exceeds image boundary",
            "description": "bbox가 이미지 width/height 경계를 벗어난 경우입니다.",
            "why_it_matters": (
                "모델이 실제 이미지에 존재하지 않는 영역까지 객체로 학습할 수 있고, "
                "augmentation이나 IoU 계산 과정에서 오류를 유발할 수 있습니다."
            ),
            "likely_causes": [
                "bbox를 이미지 밖까지 드래그함",
                "resize/crop 후 annotation 좌표가 갱신되지 않음",
                "이미지와 annotation이 서로 다른 버전임",
            ],
            "suggested_actions": [
                "annotation tool에서 bbox 경계를 확인합니다.",
                "이미지 크기와 annotation 좌표계가 일치하는지 확인합니다.",
                "필요 시 bbox를 이미지 경계 안으로 수정하되, 자동 clipping은 검수 후 적용합니다.",
            ],
            "priority_policy_note": "bbox가 이미지 밖으로 나간 경우 위치 정답이 왜곡될 수 있어 우선 검수 대상으로 분류합니다.",
        },
        "image_size_missing": {
            "title": "Image size metadata is missing",
            "description": "bbox boundary 검사를 위해 필요한 image width/height 정보가 없는 경우입니다.",
            "why_it_matters": "image size가 없으면 bbox가 이미지 경계 안에 있는지 판단할 수 없습니다.",
            "likely_causes": [
                "image metadata 생성 누락",
                "COCO subset 생성 오류",
                "annotation 변환 과정에서 width/height 제거",
            ],
            "suggested_actions": [
                "실제 이미지 파일에서 width/height를 다시 읽어 metadata를 보완합니다.",
                "metadata 생성 스크립트를 점검합니다.",
            ],
            "priority_policy_note": "학습 자체보다 품질검사 정확도를 제한하는 이슈이므로 bbox 오류와 함께 검토합니다.",
        },
        "category_id_duplicate": {
            "title": "Duplicated category id",
            "description": "categories 목록 안에서 category id가 중복된 경우입니다.",
            "why_it_matters": (
                "category_id는 classification target mapping에 사용됩니다. "
                "중복 id가 있으면 class ontology가 모호해집니다."
            ),
            "likely_causes": [
                "여러 category taxonomy를 병합하면서 id 충돌 발생",
                "class mapping table 관리 오류",
            ],
            "suggested_actions": [
                "category id를 unique하게 재정의합니다.",
                "annotation의 category_id mapping도 함께 갱신합니다.",
                "class ontology 변경 이력을 남깁니다.",
            ],
            "priority_policy_note": "class id mapping 문제는 모델의 classification target을 왜곡할 수 있어 정책 검토가 필요합니다.",
        },
        "category_name_duplicate": {
            "title": "Duplicated category name",
            "description": "categories 목록 안에서 같은 category name이 중복된 경우입니다.",
            "why_it_matters": "같은 class 이름이 여러 id에 매핑되면 모델 학습과 평가에서 class mapping이 혼란스러워집니다.",
            "likely_causes": [
                "taxonomy 병합 오류",
                "대소문자/띄어쓰기 차이를 별도 class로 처리함",
                "class ontology 관리 미흡",
            ],
            "suggested_actions": [
                "category name과 id mapping table을 정리합니다.",
                "동일한 의미의 class를 병합할지 정책적으로 결정합니다.",
            ],
            "priority_policy_note": "category name 중복은 자동 수정하기보다 ontology 정책 검토 대상으로 분류합니다.",
        },
        "annotation_category_id_missing": {
            "title": "Annotation category id is missing",
            "description": "annotation에 category_id가 없는 경우입니다.",
            "why_it_matters": (
                "category_id는 object detection 모델의 classification target입니다. "
                "category_id가 없으면 해당 객체의 class를 학습할 수 없습니다."
            ),
            "likely_causes": [
                "라벨링 누락",
                "annotation export 오류",
                "format 변환 오류",
            ],
            "suggested_actions": [
                "annotation tool에서 class label을 다시 확인합니다.",
                "category_id mapping이 유지되도록 export 설정을 확인합니다.",
            ],
            "priority_policy_note": "class label이 없는 object annotation은 classification target으로 불완전하므로 우선 검수합니다.",
        },
        "annotation_unknown_category_id": {
            "title": "Annotation references unknown category",
            "description": "annotation의 category_id가 categories 목록에 없는 경우입니다.",
            "why_it_matters": (
                "정의되지 않은 category_id는 class target으로 사용할 수 없으며, "
                "학습 파이프라인의 class index mapping을 깨뜨릴 수 있습니다."
            ),
            "likely_causes": [
                "category subset filtering 후 annotation filtering 누락",
                "class mapping table 오류",
                "여러 dataset 병합 과정에서 category id 충돌",
            ],
            "suggested_actions": [
                "category_id가 categories 목록에 존재하는지 확인합니다.",
                "잘못된 category_id를 올바른 class로 remap합니다.",
                "remap이 불가능하면 해당 annotation을 재검수합니다.",
            ],
            "priority_policy_note": "unknown category는 class target mapping을 깨뜨리므로 우선 검수 또는 remap 대상입니다.",
        },
    },
    "en": {
        "annotation_file_missing": {
            "title": "Annotation file is missing",
            "description": "The COCO annotation JSON file cannot be found.",
            "why_it_matters": (
                "Without the annotation file, images cannot be linked to ground-truth labels, "
                "so dataset loading and downstream quality checks cannot proceed."
            ),
            "likely_causes": [
                "The annotation file path was specified incorrectly",
                "The file was missing during download or copy",
                "The dataset directory structure does not match the expected layout",
            ],
            "suggested_actions": [
                "Check the annotation JSON file path.",
                "Restore the annotation file from the original dataset.",
                "Align the dataset directory structure with the README or configuration.",
            ],
            "priority_policy_note": (
                "If the annotation file is missing, the dataset cannot be inspected or trained on. "
                "Resolve this before preparing a trainable data package."
            ),
        },
        "json_decode_error": {
            "title": "Annotation JSON cannot be parsed",
            "description": "The annotation file is not valid JSON.",
            "why_it_matters": (
                "If JSON parsing fails, the COCO loader cannot read annotations, and "
                "schema/reference/bbox/category validation cannot be performed."
            ),
            "likely_causes": [
                "The JSON file was truncated",
                "A syntax error was introduced during manual editing",
                "An incorrect export file was used",
            ],
            "suggested_actions": [
                "Validate the file with a JSON validator.",
                "Re-export the annotation file from the labeling tool.",
                "Check whether the file was completely downloaded.",
            ],
            "priority_policy_note": "JSON parsing errors block all downstream checks and should be treated as P0-level issues.",
        },
        "top_level_key_missing": {
            "title": "Required COCO top-level key is missing",
            "description": "A required COCO top-level key such as images, annotations, or categories is missing.",
            "why_it_matters": (
                "COCO-format object detection datasets rely on images, annotations, and categories "
                "to connect images with bbox/category targets. Without the required structure, "
                "the training pipeline cannot reliably read ground-truth labels."
            ),
            "likely_causes": [
                "A non-COCO annotation format was used",
                "The format conversion script failed",
                "A key was removed during subset generation",
            ],
            "suggested_actions": [
                "Confirm that the annotation file follows COCO format.",
                "Inspect the format conversion script.",
                "Regenerate the subset from the original COCO annotation file.",
            ],
            "priority_policy_note": "Missing required COCO structure makes downstream validation unreliable and should be fixed first.",
        },
        "top_level_key_type": {
            "title": "Top-level COCO key has invalid type",
            "description": "The value of images, annotations, or categories is not a list.",
            "why_it_matters": (
                "The COCO loader assumes that images, annotations, and categories are iterable lists. "
                "If the type is invalid, validation and training data loading may fail."
            ),
            "likely_causes": [
                "Serialization error during annotation conversion",
                "Manual editing error",
                "Incorrect annotation schema",
            ],
            "suggested_actions": [
                "Update images, annotations, and categories to match the COCO list structure.",
                "Re-run the annotation export or conversion script.",
            ],
            "priority_policy_note": "Invalid top-level structure can break the dataset parser and should be handled first.",
        },
        "image_id_duplicate": {
            "title": "Duplicated image id",
            "description": "The images list contains duplicated image ids.",
            "why_it_matters": (
                "image_id is the key that links annotations to images. Duplicated image ids make "
                "annotation-image matching ambiguous."
            ),
            "likely_causes": [
                "Multiple datasets were merged without reassigning ids",
                "The subset generation script produced duplicate ids",
            ],
            "suggested_actions": [
                "Reassign image ids so they are unique across the dataset.",
                "Update annotation.image_id values accordingly.",
                "Record the before/after id mapping.",
            ],
            "priority_policy_note": "Duplicated image ids make annotation matching ambiguous and should be reviewed with reference validation issues.",
        },
        "annotation_id_duplicate": {
            "title": "Duplicated annotation id",
            "description": "The annotations list contains duplicated annotation ids.",
            "why_it_matters": "Duplicated annotation ids make issue tracking, review queue generation, and correction history management difficult.",
            "likely_causes": [
                "Multiple annotation files were merged without reassigning ids",
                "The subset generation script produced duplicate ids",
            ],
            "suggested_actions": [
                "Reassign annotation ids so they are unique.",
                "Record the before/after id mapping.",
            ],
            "priority_policy_note": "This may not immediately block training, but it weakens review traceability and should be cleaned up.",
        },
        "annotation_unknown_image_id": {
            "title": "Annotation references unknown image",
            "description": "An annotation references an image_id that does not exist in the images list.",
            "why_it_matters": (
                "Object detection training uses image and ground-truth annotation pairs. "
                "If an annotation references an unknown image_id, the target label cannot be linked to an image."
            ),
            "likely_causes": [
                "Annotations were not filtered correctly after image subset generation",
                "image_id mapping was broken while merging annotation files",
                "Some image metadata was removed or missing",
            ],
            "suggested_actions": [
                "Check whether the annotation.image_id exists in the images list.",
                "Remove the annotation or correct it to the proper image_id.",
                "Inspect the image filtering logic in the subset generation script.",
            ],
            "priority_policy_note": "Samples with broken image-annotation links cannot be used as training targets and should be cleaned first.",
        },
        "missing_image_file": {
            "title": "Image file is missing",
            "description": "The image is listed in the COCO JSON, but the actual image file is missing.",
            "why_it_matters": (
                "If the image file is missing, the DataLoader cannot read the sample, and annotations "
                "linked to that image cannot be used for training."
            ),
            "likely_causes": [
                "Image file was not copied or downloaded",
                "file_name path is incorrect",
                "The image directory and annotation JSON come from different dataset versions",
            ],
            "suggested_actions": [
                "Restore the missing image file from the original dataset.",
                "Check whether file_name matches the actual file path.",
                "If recovery is impossible, decide whether to exclude the image and linked annotations.",
            ],
            "priority_policy_note": "Missing image files block sample loading and should be addressed before constructing a trainable dataset.",
        },
        "image_without_annotations": {
            "title": "Image has no annotations",
            "description": "The image exists in the images list but has no linked annotations.",
            "why_it_matters": (
                "In object detection, this may be a valid negative image or a missing-label case. "
                "It should not be automatically treated as an error without checking the dataset policy."
            ),
            "likely_causes": [
                "The image is an intended negative sample",
                "Object labels were missed",
                "Annotations were removed during subset generation",
            ],
            "suggested_actions": [
                "Check whether this image is intended to be a negative sample.",
                "If visible objects are unlabeled, send the image for relabeling.",
                "Confirm whether the dataset policy allows negative images.",
            ],
            "priority_policy_note": "Because this may be a valid negative sample, route it to policy check or human review instead of auto-fixing it as an error.",
        },
        "image_file_name_invalid": {
            "title": "Image file name is invalid",
            "description": "The image metadata has an empty or non-string file_name value.",
            "why_it_matters": "If file_name is invalid, image metadata cannot be linked to the actual image file.",
            "likely_causes": [
                "Metadata generation error",
                "Annotation conversion script error",
                "Manual editing error",
            ],
            "suggested_actions": [
                "Update file_name to the actual image file name.",
                "Inspect the metadata generation script.",
            ],
            "priority_policy_note": "Invalid file_name prevents linking to the image file and should be handled like a missing-image issue.",
        },
        "bbox_missing": {
            "title": "BBox is missing",
            "description": "The annotation does not contain a bbox value.",
            "why_it_matters": (
                "bbox is the localization target for object detection models. Without a bbox, "
                "the object cannot be used for location learning."
            ),
            "likely_causes": [
                "Labeling task was incomplete",
                "Annotation export failed",
                "Task format conversion failed",
            ],
            "suggested_actions": [
                "Review the bbox in the annotation tool.",
                "Relabel the object if necessary.",
            ],
            "priority_policy_note": "Object annotations without bboxes are incomplete detection targets and should be prioritized for review.",
        },
        "bbox_format": {
            "title": "BBox format is invalid",
            "description": "The bbox does not follow the COCO format [x, y, width, height].",
            "why_it_matters": "If the bbox format is invalid, the localization target may be misinterpreted during model training.",
            "likely_causes": [
                "Error while converting YOLO/KITTI format to COCO",
                "Wrong bbox coordinate convention was used",
                "The bbox list has an invalid length",
            ],
            "suggested_actions": [
                "Check whether the bbox follows [x, y, width, height].",
                "Inspect the format conversion script.",
            ],
            "priority_policy_note": "BBox format errors can break coordinate interpretation and should be reviewed early among bbox-related issues.",
        },
        "bbox_non_numeric": {
            "title": "BBox contains non-numeric value",
            "description": "The bbox contains at least one non-numeric value.",
            "why_it_matters": (
                "bbox values are used in IoU calculation, bbox regression targets, and augmentation coordinate transforms. "
                "They must be numeric."
            ),
            "likely_causes": [
                "JSON serialization error",
                "Manual editing error",
                "Missing values were stored as strings",
            ],
            "suggested_actions": [
                "Check whether bbox values can be converted to numeric values.",
                "If conversion is not possible, send the annotation for review.",
            ],
            "priority_policy_note": "Non-numeric bbox values can break training pipelines and should be cleaned early.",
        },
        "bbox_non_positive_size": {
            "title": "BBox has non-positive width or height",
            "description": "The bbox width or height is less than or equal to zero.",
            "why_it_matters": (
                "A zero-area or negative-size bbox cannot represent a real object region, and it can make "
                "IoU calculations and bbox regression targets unstable."
            ),
            "likely_causes": [
                "BBox was incorrectly created during labeling",
                "Width/height was computed incorrectly during coordinate conversion",
                "Format conversion was incorrect",
            ],
            "suggested_actions": [
                "Review the bbox in the annotation tool.",
                "Inspect the coordinate conversion logic.",
                "If no real object exists, consider removing the annotation.",
            ],
            "priority_policy_note": "Zero-area bboxes cannot be used as localization targets and should receive high review priority.",
        },
        "bbox_negative_coordinate": {
            "title": "BBox has negative coordinate",
            "description": "The bbox x or y coordinate is negative.",
            "why_it_matters": (
                "A negative coordinate means the bbox starts outside the top-left image boundary, "
                "which may indicate a mismatch between the image coordinate system and annotation coordinates."
            ),
            "likely_causes": [
                "Coordinates were not updated after crop or resize",
                "Labeling tool export error",
                "Coordinate system conversion error",
            ],
            "suggested_actions": [
                "Check whether image preprocessing and annotation coordinate conversion are aligned.",
                "Review whether the bbox correctly covers the object.",
                "Mark auto-clipping as a dry-run candidate only and apply it after human review.",
            ],
            "priority_policy_note": "Negative coordinates may indicate coordinate conversion problems and should be reviewed with out-of-image bboxes.",
        },
        "bbox_out_of_image": {
            "title": "BBox exceeds image boundary",
            "description": "The bbox extends beyond the image width or height boundary.",
            "why_it_matters": (
                "The model may learn object regions that do not exist in the actual image, and this can cause "
                "errors during augmentation or IoU calculation."
            ),
            "likely_causes": [
                "The bbox was dragged outside the image",
                "Annotation coordinates were not updated after resize or crop",
                "The image and annotation come from different versions",
            ],
            "suggested_actions": [
                "Review the bbox boundary in the annotation tool.",
                "Check whether image size and annotation coordinates use the same coordinate system.",
                "If needed, adjust the bbox inside the image boundary after human review; do not blindly auto-clip.",
            ],
            "priority_policy_note": "Out-of-image bboxes can distort location targets and should be routed to early human review.",
        },
        "image_size_missing": {
            "title": "Image size metadata is missing",
            "description": "Image width/height metadata required for bbox boundary checks is missing.",
            "why_it_matters": "Without image size metadata, the system cannot determine whether bboxes are inside the image boundary.",
            "likely_causes": [
                "Image metadata was not generated",
                "COCO subset generation failed",
                "width/height was removed during annotation conversion",
            ],
            "suggested_actions": [
                "Read width/height from the actual image files and restore the metadata.",
                "Inspect the metadata generation script.",
            ],
            "priority_policy_note": "This mainly limits quality-check accuracy, so review it together with bbox validation issues.",
        },
        "category_id_duplicate": {
            "title": "Duplicated category id",
            "description": "The categories list contains duplicated category ids.",
            "why_it_matters": (
                "category_id is used for classification target mapping. Duplicated ids make the class ontology ambiguous."
            ),
            "likely_causes": [
                "Category taxonomies were merged and id collisions occurred",
                "The class mapping table was not managed correctly",
            ],
            "suggested_actions": [
                "Redefine category ids so they are unique.",
                "Update annotation.category_id mappings accordingly.",
                "Record class ontology change history.",
            ],
            "priority_policy_note": "Class id mapping issues can distort classification targets and require policy review.",
        },
        "category_name_duplicate": {
            "title": "Duplicated category name",
            "description": "The categories list contains duplicated category names.",
            "why_it_matters": "If the same class name maps to multiple ids, class mapping becomes confusing during training and evaluation.",
            "likely_causes": [
                "Taxonomy merge error",
                "Case or spacing variants were treated as separate classes",
                "Class ontology was not managed consistently",
            ],
            "suggested_actions": [
                "Clean up the category name and id mapping table.",
                "Decide whether semantically identical classes should be merged.",
            ],
            "priority_policy_note": "Duplicated category names should be routed to ontology policy review instead of automatic correction.",
        },
        "annotation_category_id_missing": {
            "title": "Annotation category id is missing",
            "description": "The annotation does not contain category_id.",
            "why_it_matters": (
                "category_id is the classification target for object detection models. Without it, "
                "the model cannot learn the object's class."
            ),
            "likely_causes": [
                "Labeling was incomplete",
                "Annotation export failed",
                "Format conversion failed",
            ],
            "suggested_actions": [
                "Review the class label in the annotation tool.",
                "Check export settings to ensure category_id mapping is preserved.",
            ],
            "priority_policy_note": "Object annotations without class labels are incomplete classification targets and should be reviewed early.",
        },
        "annotation_unknown_category_id": {
            "title": "Annotation references unknown category",
            "description": "The annotation.category_id does not exist in the categories list.",
            "why_it_matters": (
                "An undefined category_id cannot be used as a class target and can break class-index mapping "
                "in the training pipeline."
            ),
            "likely_causes": [
                "Annotations were not filtered after category subset filtering",
                "Class mapping table error",
                "Category id collision during dataset merge",
            ],
            "suggested_actions": [
                "Check whether category_id exists in the categories list.",
                "Remap the incorrect category_id to the correct class.",
                "If remapping is impossible, send the annotation for review.",
            ],
            "priority_policy_note": "Unknown categories break class-target mapping and should be prioritized for review or remapping.",
        },
    },
}


DEFAULT_METADATA = {
    "recommended_owner": "data_curator",
    "judgement_level": "human_review",
    "auto_fixable": "no",
    "default_impact_level": "unknown",
    "blocking_level": "unknown",
    "review_urgency_hint": "medium",
}


DEFAULT_TEXTS: dict[str, dict[str, Any]] = {
    "ko": {
        "title": "Unregistered quality issue",
        "description": "Issue catalog에 아직 등록되지 않은 품질 이슈입니다.",
        "why_it_matters": (
            "validation logic에서 issue가 생성되었지만 catalog 설명이 없으면 "
            "검수자에게 의미와 조치 방법을 충분히 전달하기 어렵습니다."
        ),
        "likely_causes": [
            "새 validation check가 추가되었지만 catalog가 업데이트되지 않음",
            "check_name 오타 또는 naming convention 불일치",
        ],
        "suggested_actions": [
            "issue_catalog.py에 해당 check_name의 정의를 추가합니다.",
            "check_name naming convention을 확인합니다.",
        ],
        "priority_policy_note": (
            "catalog에 등록되지 않은 issue는 우선 review 대상에 포함하되, "
            "정확한 priority tier 계산 전에 catalog 정의를 보완합니다."
        ),
    },
    "en": {
        "title": "Unregistered quality issue",
        "description": "This quality issue is not registered in the issue catalog yet.",
        "why_it_matters": (
            "The validation logic produced an issue, but without a catalog definition, "
            "reviewers do not get enough context about its meaning or recommended action."
        ),
        "likely_causes": [
            "A new validation check was added but the catalog was not updated",
            "check_name typo or naming convention mismatch",
        ],
        "suggested_actions": [
            "Add a definition for this check_name to issue_catalog.py.",
            "Check the check_name naming convention.",
        ],
        "priority_policy_note": (
            "Unregistered issues should be included in the review queue, but the catalog definition "
            "should be completed before final priority tier interpretation."
        ),
    },
}


def normalize_language(language: str | None) -> Language:
    """
    [P4] Normalize user-facing catalog language.

    Default is Korean to preserve backward compatibility with the original project.
    """
    if language is None:
        return "ko"

    normalized = language.lower().strip()

    if normalized not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {sorted(SUPPORTED_LANGUAGES)}"
        )

    return normalized  # type: ignore[return-value]


def _build_issue_definition(
    check_name: str,
    language: str | None = "ko",
) -> IssueDefinition:
    """
    [P5] Build an IssueDefinition by combining metadata and localized text.
    """
    selected_language = normalize_language(language)

    metadata = ISSUE_METADATA.get(check_name, DEFAULT_METADATA)
    text = ISSUE_TEXTS[selected_language].get(check_name, DEFAULT_TEXTS[selected_language])

    return IssueDefinition(
        check_name=check_name,
        title=text["title"],
        description=text["description"],
        why_it_matters=text["why_it_matters"],
        likely_causes=list(text["likely_causes"]),
        suggested_actions=list(text["suggested_actions"]),
        recommended_owner=metadata["recommended_owner"],
        judgement_level=metadata["judgement_level"],
        auto_fixable=metadata["auto_fixable"],
        default_impact_level=metadata["default_impact_level"],
        blocking_level=metadata["blocking_level"],
        review_urgency_hint=metadata["review_urgency_hint"],
        priority_policy_note=text["priority_policy_note"],
    )


def get_issue_definition(
    check_name: str | None,
    language: str | None = "ko",
) -> IssueDefinition:
    """
    [P6] Look up an issue definition by check_name.

    If check_name is registered, return the localized definition.
    If check_name is missing or unregistered, return a localized fallback definition.
    """
    if check_name is None:
        return _build_issue_definition("unknown_issue", language=language)

    return _build_issue_definition(check_name, language=language)


def enrich_issue_dict(
    issue_dict: dict[str, Any],
    language: str | None = "ko",
) -> dict[str, Any]:
    """
    [P7] Attach localized catalog information to a raw issue dict.

    Example:
        enrich_issue_dict(issue, language="ko")  # Korean catalog text
        enrich_issue_dict(issue, language="en")  # English catalog text
    """
    enriched_issue = dict(issue_dict)

    check_name = enriched_issue.get("check_name")
    issue_definition = get_issue_definition(check_name, language=language)

    catalog_dict = asdict(issue_definition)

    # Preserve the actual check_name even when fallback text is used.
    if check_name is not None:
        catalog_dict["check_name"] = check_name

    enriched_issue["catalog"] = catalog_dict

    return enriched_issue
