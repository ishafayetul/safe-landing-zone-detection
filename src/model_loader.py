import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import torch
from transformers import AutoImageProcessor, SegformerForSemanticSegmentation

from .risk_config import MODEL_CLASS_NAMES


REQUIRED_MODEL_FILES = (
    "model.safetensors",
    "config.json",
    "preprocessor_config.json",
    "label2id.json",
    "id2label.json",
)


@dataclass
class ModelBundle:
    processor: AutoImageProcessor
    model: SegformerForSemanticSegmentation
    id2label: Dict[int, str]
    label2id: Dict[str, int]
    device: torch.device


def _load_label_maps(model_dir: Path):
    with (model_dir / "id2label.json").open(encoding="utf-8") as handle:
        id2label = {int(key): str(value) for key, value in json.load(handle).items()}
    with (model_dir / "label2id.json").open(encoding="utf-8") as handle:
        label2id = {str(key): int(value) for key, value in json.load(handle).items()}

    expected_inverse = {label: class_id for class_id, label in id2label.items()}
    if expected_inverse != label2id:
        raise ValueError("id2label.json and label2id.json are inconsistent")
    expected_ids = set(range(len(MODEL_CLASS_NAMES)))
    if set(id2label) != expected_ids:
        raise ValueError("model class IDs must be contiguous from 0 through 23")
    actual_names = tuple(id2label[class_id] for class_id in sorted(id2label))
    if actual_names != MODEL_CLASS_NAMES:
        raise ValueError(
            "model labels or ordering do not match the configured 24-class palette"
        )
    return id2label, label2id


def _select_device(requested: str) -> torch.device:
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but no CUDA device is available")
    return torch.device(requested)


def load_model_bundle(model_dir="model", device="auto") -> ModelBundle:
    model_path = Path(model_dir)
    if not model_path.is_dir():
        raise FileNotFoundError(f"model directory not found: {model_path}")

    missing = [name for name in REQUIRED_MODEL_FILES if not (model_path / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "model directory is missing required files: " + ", ".join(missing)
        )

    id2label, label2id = _load_label_maps(model_path)
    selected_device = _select_device(device)
    processor = AutoImageProcessor.from_pretrained(model_path, local_files_only=True)
    model = SegformerForSemanticSegmentation.from_pretrained(
        model_path, local_files_only=True
    )
    if model.config.num_labels != len(id2label):
        raise ValueError(
            f"model has {model.config.num_labels} output labels but mappings contain "
            f"{len(id2label)}"
        )
    model.config.id2label = id2label
    model.config.label2id = label2id
    model.to(selected_device)
    model.eval()
    return ModelBundle(processor, model, id2label, label2id, selected_device)
