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

    process_images = process_images_from_directory(model_path=model_path, directory=image_dir, transform=transform)

    print("Running inference...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    img = process_images[0][1]
    with torch.inference_mode():
        # move model to GPU, if available
        if device.type != "cpu":
            model = model.to(device)
            img = img.to(device)
        # run the model
        outputs = model.forward(img)
        # apply the final activation function (timm doesn't support doing this internally)
        outputs = torch.nn.functional.sigmoid(outputs)
        # move inputs, outputs, and model back to cpu if we were on GPU
        if device.type != "cpu":
            img = img.to("cpu")
            outputs = outputs.to("cpu")
            model = model.to("cpu")

    print("Processing results...")


    return None


category_dict = {"rating": 9, "general": 0, "characters": 4}
thresh_dict = {"rating": 0.5, "general": 0.35, "characters": 7}
predict(model_path='wd-vit-tagger-v3', categories=category_dict, thresholds=thresh_dict, image_dir="images")
