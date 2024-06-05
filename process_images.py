import json
import os

import numpy as np
from PIL import Image
from PyQt5.QtCore import QThreadPool, QRunnable


class Runnable(QRunnable):
    """
    Preprocesses images from directory using qt's multiprocessing model
    :param image_path: file name
    :param size: dimensions to resize to
    :param preprocessed_images: return array
    """

    def __init__(self, image_path, size, preprocessed_images, transform):

        super().__init__()
        self.image_path = image_path
        self.size = size
        self.preprocessed_images = preprocessed_images
        self.transform = transform

    def run(self):
        try:
            # Model only supports 3 channels
            with Image.open(self.image_path).convert('RGB') as image:

                # Pad image to square
                w, h = image.size
                px = max(image.size)
                # pad to square with white background
                canvas = Image.new("RGB", (px, px), (255, 255, 255))
                canvas.paste(image, ((px - w) // 2, (px - h) // 2))

                image_array = self.transform(canvas).unsqueeze(0)
                image_array = image_array[:, [2, 1, 0]]

                self.preprocessed_images.append((self.image_path, image_array))

        except Exception as e:
            print(f"Runnable Error processing {self.image_path}: {e}")


def process_images_from_directory(model_path: str, directory: str, transform) -> list[(str, np.ndarray)]:
    """
    Processes all images in a directory, does not go into subdirectories.
    Images need to be shaped before predict can be called on it.
    :param transform:     inputs: Tensor = transform(img_input).unsqueeze(0)
    :param model_path: load config file for input shapes
    :param directory: directory of images to be precessed
    :return: [(filename, ndarray)] returns a list of file names and processed images
    """
    preprocessed_images = []
    image_filenames = os.listdir(directory)
    pool = QThreadPool.globalInstance()

    # get dimensions from model
    with open(os.path.join(model_path, "config.json")) as config_file:
        configs = json.load(config_file)

    _, height, width = configs['pretrained_cfg']['input_size']

    size = (height, width)
    for filename in image_filenames:
        image_path = os.path.join(directory, filename)
        runnable = Runnable(image_path, size, preprocessed_images, transform)
        pool.start(runnable)

    pool.waitForDone()
    return preprocessed_images



