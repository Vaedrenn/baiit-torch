from PyQt5.QtCore import Qt, QSize, QUrl, QRect
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListView, QStyledItemDelegate, QApplication, \
    QStyleOptionViewItem, QToolTip


class ImageGallery(QListView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        delegate = ThumbnailDelegate()
        self.setItemDelegate(delegate)
        self.setViewMode(QListWidget.IconMode)
        self.setAcceptDrops(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # ctrl and shift click selection
        self.setIconSize(QSize(180, 180))
        self.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize
        self.doubleClicked.connect(self.open_image)

    def open_image(self, index):
        """
        Display Open image in image explorer
        :param index: index in the model, item holds file path and tag info
        """
        file_path = self.model().data(index, Qt.DisplayRole)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustSpacing()

    def adjustSpacing(self):
        icon_size = self.iconSize()
        available_width = self.viewport().width()

        num_columns = max(1, available_width // icon_size.width())
        extra_space = available_width - (num_columns * icon_size.width())
        new_spacing = max(5, extra_space // (num_columns + 1))

        new_grid_size = QSize(icon_size.width() + new_spacing, 185)
        self.setGridSize(new_grid_size)


class ThumbnailDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying images, removes check box and names for better formatting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayRoleEnabled = False

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # remove checkbox and name area
        if not self.displayRoleEnabled:
            option.features &= ~option.HasDisplay
            option.features &= ~option.HasCheckIndicator
