import sys
import time

import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QThread, pyqtSignal, QAbstractListModel, QRunnable, QThreadPool
from PyQt5.QtGui import QIcon, QPixmap, QImage


class ImageGalleryTableModel(QAbstractListModel):
    icons_ready = pyqtSignal()

    def __init__(self, results, parent=None):
        super(ImageGalleryTableModel, self).__init__(parent)
        self.filenames = list(results.keys())
        self.results = results  # pseudo cache of tags by categories
        self.tags = None  # df of tags and count
        self.state = None  # df of tag state
        self.filtered_filenames = self.filenames  # Use this instead of state to avoid extreme data population times
        self.filtered_state = self.state
        self.icons = {}

        self.state, self.tags = build_table(results)
        self.filtered_state = self.state
        self.icon_thread = IconCreationThread(results)
        self.icon_thread.icons_created.connect(self.on_icons_created)
        self.icon_thread.start()

    def rowCount(self, parent=QModelIndex()):
        return len(self.filtered_filenames)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row = index.row()
        filename = self.filtered_filenames[row]
        if role == Qt.DisplayRole:
            return filename
        elif role == Qt.DecorationRole:
            return self.icons.get(filename, QIcon())  # Return empty QIcon if not yet loaded
        elif role == Qt.UserRole:
            return self.results[filename]['training_caption']

        return QVariant()

    def get_tags(self, filename, category):
        try:
            return self.results[filename][category]
        except KeyError:
            if category == 'user_tags':
                return []
            else:
                print(f"KeyError: category: '{category}' not found for '{filename}'")
                return []

    def on_icons_created(self, icons):
        self.icons = icons
        self.icons_ready.emit()
        self.layoutChanged.emit()

    def filter(self, tags: list):

        """Filter for filenames results where tags are true"""
        if not tags:
            self.filtered_filenames = self.filenames
        else:
            try:
                mask = self.state[tags].all(axis=1)
                self.filtered_state = self.state[mask]
                self.filtered_filenames = self.filtered_state.loc[:, "filename"].tolist()
            except KeyError:
                self.filtered_filenames = []
        self.layoutChanged.emit()


def build_table(results):
    unique_tags = set()
    for attributes in results.values():
        tags = attributes['training_caption'].split(', ')
        unique_tags.update(tags)

    # Create the table
    table_data = []
    for filename, attributes in results.items():
        tags = set(attributes['training_caption'].split(', '))
        row = {'filename': filename}
        for tag in unique_tags:
            row[tag] = tag in tags
        table_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(table_data)

    tag_counts = df.drop(columns=['filename']).sum()
    tag_counts = tag_counts.sort_values(ascending=False)

    return df, tag_counts


class IconCreationThread(QThread):
    """
    Offload icon creation off of main thread. Creates a new runnable for each filename
    """
    icons_created = pyqtSignal(dict)

    def __init__(self, results):
        super().__init__()
        self.results = results
        self.icons = {}

    def run(self):
        pool = QThreadPool.globalInstance()
        max_threads = pool.maxThreadCount()
        if max_threads > 2:  # stop eating all my cpu
            max_threads -= 2
        pool.setMaxThreadCount(max_threads)

        for filename in self.results.keys():
            runnable = CreateIconRunnable(filename=filename, icons=self.icons)
            pool.start(runnable)

        pool.waitForDone()
        self.icons_created.emit(self.icons)


class CreateIconRunnable(QRunnable):
    def __init__(self, filename, icons):
        super().__init__()
        self.filename = filename
        self.icons = icons

    def run(self):
        image = QImage(self.filename).scaledToHeight(200, Qt.FastTransformation)
        pixmap = QPixmap.fromImage(image)
        ico = QIcon(pixmap)
        self.icons[self.filename] = ico
