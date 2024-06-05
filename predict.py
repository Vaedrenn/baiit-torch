import gc
import os
from typing import Any, Dict, List

import numpy as np
import torch
from timm.data import create_transform, resolve_data_config

from load_actions import load_model, load_labels
from process_images import process_images_from_directory


def predict(model_path: str | os.PathLike,
            thresholds: dict,
            categories: dict,
            image_dir: str | os.PathLike,
            batch_size: int = 32
            ) -> dict[Any, dict[str | Any, dict[Any, Any] | str]] | None:
    """
    Predicts tags for images in directory
    :param model_path: path to model
    :param thresholds: dictionary of categories and thresholds, if threshold > probs then accept tag
    :param categories: dictionary of category and their number in selected_tags.csv
    :param image_dir: directory of images
    :param batch_size: number of images to process in a batch
    :return: dict[ filename: {category: {tag:probs}, category: {tag:probs}, 'taglist': str, 'caption': str }]

    Usage:
    category_dict = {"rating": 9, "general": 0, "characters": 4}
    thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
    results = predict(model_path='wd-vit-tagger-v3', categories=category_dict, thresholds=thresh_dict, image_dir=r"images")
    """

    # Load model and labels
    model = load_model(model_path=model_path)
    if model is None:
        return
    labels = load_labels(model_path=model_path, categories=categories)
    if labels is None or {}:
        return
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))

    processed_images = process_images_from_directory(model_path=model_path, directory=image_dir, transform=transform)

    # Determine device (GPU or CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    results = {}
    model = model.to(device)
    model.eval()

    def batch_generator(data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    for image_batch in batch_generator(processed_images, batch_size):
        filenames = [img[0] for img in image_batch]
        img_tensors = torch.stack([img[1] for img in image_batch])

        # Remove any singleton dimensions and move to device
        img_tensors = torch.squeeze(img_tensors, dim=1).to(device)

        # Ensure img_tensors have the shape (batch_size, channels, height, width)
        if len(img_tensors.shape) != 4:
            raise ValueError(f"Expected img_tensors to have 4 dimensions (batch_size, channels, height, width), but got {img_tensors.shape}")

        with torch.inference_mode():
            outputs = model.forward(img_tensors)
            # apply the final activation function (timm doesn't support doing this internally)
            outputs = torch.nn.functional.sigmoid(outputs)

            # move outputs back to cpu
            outputs = outputs.cpu()

        for idx, filename in enumerate(filenames):
            results_tags = process_results(probs=outputs[idx], labels=labels, thresholds=thresholds)
            results[filename] = results_tags

        # Move tensors to CPU and explicitly delete them to free GPU memory
        img_tensors.cpu()
        torch.cuda.empty_cache()

    model.cpu()
    torch.cuda.empty_cache()
    return results


def process_results(probs, labels, thresholds):
    if len(probs.shape) == 1:
        # If probs is a 1D array, convert it to a 2D array with one batch
        probs = probs[np.newaxis, :]
    elif len(probs.shape) != 2:
        raise ValueError(f"Expected probs to have 2 dimensions (batch_size, num_classes), but got {probs.shape}")

    tag_names = list(zip(labels["tags"], probs[0]))  # labels["tags"] is the list of all tags
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
