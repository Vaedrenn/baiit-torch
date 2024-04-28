from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
import timm


def load_model(model_path: str | os.path, filename="model.safetensors"):
    """
    Loads models model_path, should be called before using predict
    :param model_path: file name
    :param filename: optional filename
    :return: returns the loaded model
    """
    config_file = open(os.path.join(model_path, "config.json"))

    configs = json.load(config_file)
    arch = configs['architecture']
    file_path = os.path.join(model_path, filename)
    model = timm.create_model(
        model_name=arch,
        pretrained_cfg_overlay=dict(file=file_path)
    )

    return model


def load_labels(model_path: str | os.path, filename: str, categories: dict) -> dict:
    """
    Loads labels from  txt file
    :param filename:name of label file
    :param categories: cat name : cat number
    :param model_path: file name
    :return: list of tags(labels) labels[category_name] = index
    """
    tag_path = os.path.join(model_path, filename)

    if not os.path.exists(tag_path):
        # Default path name
        tag_path = os.path.join(model_path, "selected_tags.csv")

    labels = {}
    try:
        tags_df = pd.read_csv(tag_path)
        tags = tags_df["name"]
        all_tags = tags.tolist()
        labels['tags'] = all_tags

        for category_name, category_number in categories.items():
            index = list(np.where(tags_df["category"] == category_number)[0])
            labels[category_name] = index

    except (FileNotFoundError, IOError, OSError, PermissionError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return {}
    return labels


if __name__ == '__main__':
    path = r"wd-vit-tagger-v3"
    r = load_model(path)
    print(r)
