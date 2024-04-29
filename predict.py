import os
from typing import Any

import torch.nn
from timm.data import create_transform, resolve_data_config

from load_actions import load_model, load_labels
from process_images import process_images_from_directory


def predict(model_path: str | os.PathLike,
            thresholds: dict,
            categories: dict,
            image_dir: str | os.PathLike
            ) -> list[tuple[Any, dict[Any, list[list[Any] | Any]]]] | None:
    model = load_model(model_path=model_path)
    load_labels(model_path=model_path, categories=categories)
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))

    process_images = process_images_from_directory(model_path=model_path, directory=image_dir)
    return None


category_dict = {"rating": 9, "general": 0, "characters": 4}
thresh_dict = {"rating": 0.5, "general": 0.35, "characters": 7}
predict(model_path='wd-vit-tagger-v3', categories=category_dict, thresholds=thresh_dict, image_dir="images")
