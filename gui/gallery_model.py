from collections import defaultdict

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from PyQt5.QtGui import QIcon


class ImageGalleryTableModel(QAbstractTableModel):
    def __init__(self, results, parent=None):
        super(ImageGalleryTableModel, self).__init__(parent)
        self.results = results
        self.filenames = list(results.keys())
        self.tags = self.create_filters(results)

    def rowCount(self, parent=QModelIndex()):
        return len(self.filenames)

    def columnCount(self, parent=QModelIndex()):
        return 1  # Only filenames

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row = index.row()
        filename = self.filenames[row]

        if role == Qt.DisplayRole:
            return filename
        elif role == Qt.DecorationRole:
            return QIcon(filename)

        return QVariant()

    def get_tags(self, filename, category):
        return self.results[filename][category]

    def create_filters(self, results):
        """
        Creates a dictionary of all tags and the count of each tag: {'safe': 3, 'house': 4, 'cafe': 2 }
        :param results:
        :return: tags
        """
        tag_counts = defaultdict(int)

        for image_data in results.values():
            for category, tags in image_data.items():
                for tag in tags.keys():
                    tag_counts[tag] += 1

        return dict(tag_counts)
