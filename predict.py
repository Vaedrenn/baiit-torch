import os
from typing import Any, Dict, List

import torch.nn
from timm.data import create_transform, resolve_data_config

from load_actions import load_model, load_labels
from process_images import process_images_from_directory


def predict(model_path: str | os.PathLike,
            thresholds: dict,
            categories: dict,
            image_dir: str | os.PathLike
            ) -> dict[Any, dict[str | Any, dict[Any, Any] | str]] | None:
    """
    Predicts tags for images in directory
    :param model_path: path to model
    :param thresholds: dictionary of categories and thresholds, if threshold > probs then accept tag
    :param categories: dictionary of category and their number in selected_tags.csv
    :param image_dir: directory of images
    :return: dict[ filename: {category: {tag:probs}, category: {tag:probs}, 'taglist': str, 'caption': str }]

    Usage:
    category_dict = {"rating": 9, "general": 0, "characters": 4}
    thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
    results = predict(model_path='wd-vit-tagger-v3', categories=category_dict, thresholds=thresh_dict, image_dir=r"images")
    """

    # print("Loading model and labels")
    model = load_model(model_path=model_path)
    if model is None:
        return
    labels = load_labels(model_path=model_path, categories=categories)
    if labels is None or {}:
        return
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))

    processed_images = process_images_from_directory(model_path=model_path, directory=image_dir, transform=transform)

    # print("Running inference...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    results = {}
    for img in processed_images:
        filename = img[0]
        img_tensor = img[1]
        with torch.inference_mode():
            # move model to GPU, if available
            if device.type != "cpu":
                model = model.to(device)
                img_tensor = img_tensor.to(device)
            # run the model
            outputs = model.forward(img_tensor)
            # apply the final activation function (timm doesn't support doing this internally)
            outputs = torch.nn.functional.sigmoid(outputs)
            # move inputs, outputs, and model back to cpu if we were on GPU
            if device.type != "cpu":
                img_tensor = img_tensor.to("cpu")
                outputs = outputs.to("cpu")
                model = model.to("cpu")

        # convert numpy to access results
        outputs = outputs.numpy()
        results_tags = process_results(probs=outputs, labels=labels, thresholds=thresholds)
        results[filename] = results_tags

    # for k, v in results.items():
    #     print(k)
    #     print(v['caption'])
    return results


def process_results(probs, labels, thresholds):
    tag_names = list(zip(labels["tags"], probs[0]))  # labels[tags] is the list of all tags
    processed = {}

    for category, indexes in labels.items():
        # Get all names from indexes if it is in index
        if category != 'tags':
            tag_probs = dict([tag_names[i] for i in indexes if tag_names[i][1] > thresholds[category]])
            processed[category] = dict(sorted(tag_probs.items(), key=lambda item: item[1], reverse=True))

    combined_names = []
    for category, tags in processed.items():
        combined_names.extend([t for t in tags])

    # Convert to a string suitable for use as a training caption
    caption = ", ".join(combined_names)
    tag_list = caption.replace("_", " ").replace("(", "\(").replace(")", "\)")

    processed['caption'] = caption
    processed['taglist'] = tag_list

    return processed

