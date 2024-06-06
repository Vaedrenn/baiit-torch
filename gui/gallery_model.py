from collections import defaultdict

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QImage


class ImageGalleryTableModel(QAbstractTableModel):
    icons_ready = pyqtSignal()

    def __init__(self, results, parent=None):
        super(ImageGalleryTableModel, self).__init__(parent)
        self.results = results
        self.filenames = list(results.keys())
        self.tags = create_filters(results)
        self.icons = {}

        self.icon_thread = IconCreationThread(results)
        self.icon_thread.icons_created.connect(self.on_icons_created)
        self.icon_thread.start()

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
            return self.icons.get(filename, QIcon())  # Return empty QIcon if not yet loaded
        elif role == Qt.UserRole:
            return self.results[filename]['caption']

        return QVariant()

    def get_tags(self, filename, category):
        return self.results[filename][category]

    def on_icons_created(self, icons):
        self.icons = icons
        self.icons_ready.emit()
        self.layoutChanged.emit()


def create_filters(results):
    """
    Creates a dictionary of all tags and the count of each tag: {'safe': 3, 'house': 4, 'cafe': 2 }
    :param results:
    :return: tags
    """
    tag_counts = defaultdict(int)

    for image_data in results.values():
        for category, tags in image_data.items():
            if category not in ['caption', 'taglist']:  # Exclude caption and taglist
                for tag in tags.keys():
                    tag_counts[tag] += 1

    return dict(tag_counts)


class IconCreationThread(QThread):
    icons_created = pyqtSignal(dict)

    def __init__(self, results):
        super().__init__()
        self.results = results

    def run(self):
        icons = create_icons(self.results)
        self.icons_created.emit(icons)


def create_icons(results):
    icons = {}
    for filename in results.keys():
        image = QImage(filename).scaledToHeight(200, Qt.FastTransformation)
        pixmap = QPixmap.fromImage(image)
        ico = QIcon(pixmap)
        icons[filename] = ico
    return icons
