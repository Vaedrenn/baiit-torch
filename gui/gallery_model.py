from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from PyQt5.QtGui import QIcon


class ImageGalleryTableModel(QAbstractTableModel):
    def __init__(self, results, parent=None):
        super(ImageGalleryTableModel, self).__init__(parent)
        self.results = results
        self.filenames = list(results.keys())

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
        elif role == Qt.UserRole:
            return self.results[filename]

        return QVariant()

    def get_tags(self, filename, category):
        return self.results[filename][category]
