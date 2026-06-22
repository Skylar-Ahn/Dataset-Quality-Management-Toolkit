import json
import random
import shutil
from pathlib import Path


SOURCE_ANN = Path("data/raw/coco/annotations/instances_val2017.json")
SOURCE_IMG_DIR = Path("data/raw/coco/val2017")

OUT_DIR = Path("data/sample/coco-mini")
OUT_IMG_DIR = OUT_DIR / "images"
OUT_ANN_DIR = OUT_DIR / "annotations"
OUT_ANN = OUT_ANN_DIR / "instances_coco_mini.json"

TARGET_CLASSES = {
    "person",
    "car",
    "bicycle",
    "motorcycle",
    "bus",
    "truck",
    "traffic light",
    "stop sign",
}

NUM_IMAGES = 150
RANDOM_SEED = 42


def main():
    random.seed(RANDOM_SEED)

    OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ANN_DIR.mkdir(parents=True, exist_ok=True)

    with SOURCE_ANN.open("r", encoding="utf-8") as f:
        coco = json.load(f)

    categories = coco["categories"]
    target_category_ids = {
        cat["id"]
        for cat in categories
        if cat["name"] in TARGET_CLASSES
    }

    image_id_to_annotations = {}
    for ann in coco["annotations"]:
        if ann["category_id"] in target_category_ids:
            image_id_to_annotations.setdefault(ann["image_id"], []).append(ann)

    candidate_image_ids = list(image_id_to_annotations.keys())
    selected_image_ids = set(random.sample(candidate_image_ids, min(NUM_IMAGES, len(candidate_image_ids))))

    selected_images = [
        img for img in coco["images"]
        if img["id"] in selected_image_ids
    ]

    selected_annotations = [
        ann for ann in coco["annotations"]
        if ann["image_id"] in selected_image_ids and ann["category_id"] in target_category_ids
    ]

    selected_categories = [
        cat for cat in categories
        if cat["id"] in target_category_ids
    ]

    for img in selected_images:
        src = SOURCE_IMG_DIR / img["file_name"]
        dst = OUT_IMG_DIR / img["file_name"]

        if src.exists():
            shutil.copy2(src, dst)
        else:
            print(f"[WARN] Missing image file: {src}")

    subset = {
        "info": coco.get("info", {}),
        "licenses": coco.get("licenses", []),
        "images": selected_images,
        "annotations": selected_annotations,
        "categories": selected_categories,
    }

    with OUT_ANN.open("w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False, indent=2)

    print(f"Created COCO mini subset")
    print(f"- images: {len(selected_images)}")
    print(f"- annotations: {len(selected_annotations)}")
    print(f"- categories: {len(selected_categories)}")
    print(f"- output: {OUT_DIR}")


if __name__ == "__main__":
    main()
