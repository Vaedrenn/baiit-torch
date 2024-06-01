from PyQt5.QtCore import Qt, QSize, QUrl, QRect
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap
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
        self.setIconSize(QSize(800, 200))
        self.setSpacing(5)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(50)
        self.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize
        self.doubleClicked.connect(self.open_image)

    def open_image(self, index):
        """
        Display Open image in image explorer
        :param index: index in the model, item holds file path and tag info
        """
        file_path = self.model().data(index, Qt.DisplayRole)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))


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
