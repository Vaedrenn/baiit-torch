from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
import timm
from torch import nn


def load_model(model_path: str | os.PathLike, filename="model.safetensors"):
    """
    Loads models model_path, should be called before using predict
    :param model_path: file name
    :param filename: optional filename
    :return: returns the loaded model
    """
    config_file_path = os.path.join(model_path, "config.json")

    if not os.path.exists(config_file_path):
        return

    with open(config_file_path, 'r') as config_file:
        configs = json.load(config_file)

    file_path = os.path.join(model_path, filename)

    # load kwargs from create_model
    model_name = configs["architecture"]
    pretrained_cfg = configs.get('pretrained_cfg', {})
    if 'num_classes' in configs:
        pretrained_cfg['num_classes'] = configs['num_classes']
    model_args = configs.get('model_args', {})

    model: nn.Module = timm.create_model(
        model_name=model_name,
        pretrained_cfg_overlay=pretrained_cfg,
        checkpoint_path=file_path,
        **model_args
    ).eval()

    return model


def load_labels(model_path: str | os.PathLike, categories: dict, filename="selected_tags.csv") -> dict:
    """
    Loads labels from a CSV file
    :param filename: name of label file
    :param categories: cat name : cat number
    :param model_path: file path
    :return: list of tags(labels) labels[category_name] = index
    """
    tag_path = os.path.join(model_path, filename)

    if not os.path.exists(tag_path):
        # Default path name
        tag_path = os.path.join(model_path, "selected_tags.csv")

    labels = {}
    try:
        with open(tag_path, 'r') as tag_file:
            tags_df = pd.read_csv(tag_file)
            tags = tags_df["name"].str.replace("_", " ")

            all_tags = tags.tolist()
            labels['tags'] = all_tags

            for category_name, category_number in categories.items():
                index = list(np.where(tags_df["category"] == category_number)[0])
                labels[category_name] = index

    except (FileNotFoundError, IOError, OSError, PermissionError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return {}

    return labels


def test_load():
    path = r"tests/wd-vit-tagger-v3"
    test_dict = {"rating": 9, "general": 0, "characters": 4}
    model = load_model(path)
    labels = load_labels(path, filename="selected_tags.csv", categories=test_dict)

    repo_id = "SmilingWolf/wd-vit-tagger-v3"
    hf_model: nn.Module = timm.create_model("hf-hub:" + repo_id).eval()
    state_dict = timm.models.load_state_dict_from_hf(repo_id)
    hf_model.load_state_dict(state_dict)
    hf_model.eval()

    assert str(hf_model) == str(model)
