from __future__ import annotations

import os
from collections import OrderedDict
from typing import Type

import safetensors
from safetensors.torch import load_file
import torch
import pandas as pd
import numpy as np


def load_model(model_path: str | os.path, filename="model.safetensors"):
    """
    Loads models model_path, should be called before using predict
    :param model_path: file name
    :param filename: optional filename
    :return: returns the loaded model
    """
    torch_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    file = os.path.join(model_path, filename)
    model = safetensors.torch.load_file(file, str(torch_device))


def load_labels(model_path: str | os.path, filename: str, categories: dict) -> dict:
    """
    Loads labels from  txt file
    :param filename:name of label file
    :param categories: cat name : cat number
    :param model_path: file name
    :return: list of tags(labels)
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
    path = r"C:\Users\khei\PycharmProjects\models\wd-vit-tagger-v3"
    r = load_model(path)
    print(r)
    test_dict = {"rating": 9, "general": 0, "characters": 4}
    t = load_labels(path, "selected_tags.csv", test_dict)
    print(t)
