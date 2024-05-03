import os
import shutil
import sys

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStyleFactory, QPushButton, QLineEdit, \
    QCompleter, QListWidget, QAbstractItemView, QListView, QStyledItemDelegate, QTextEdit, QGridLayout, QFileDialog, \
    QGroupBox

from gui.dark_palette import create_dark_palette
from categories import TagDisplayWidget

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        category_dict = {"rating": '9', "characters": '4', "general": '9'}
        thresh_dict = {"rating": 0.0, "characters": 0.7, "general": 0.35}
        self.threshold = thresh_dict
        self.categories = category_dict
        self.proxy_model = QSortFilterProxyModel()

        self.image_gallery = QListView()
        self.tag_display = None

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        self.setLayout(QHBoxLayout())

        # image gallery
        delegate = ThumbnailDelegate()
        self.image_gallery.setItemDelegate(delegate)
        self.image_gallery.setModel(self.proxy_model)  # set proxy model for filtering
        self.image_gallery.setViewMode(QListWidget.IconMode)
        self.image_gallery.setAcceptDrops(False)
        self.image_gallery.setSelectionMode(QAbstractItemView.ExtendedSelection)  # ctrl and shift click selection
        self.image_gallery.setIconSize(QSize(400, 200))
        self.image_gallery.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize
        self.image_gallery.clicked.connect(self.display_info)
        self.image_gallery.doubleClicked.connect(self.open_image)

        self.tag_display = TagDisplayWidget(self.categories, self.threshold)
        self.tag_display.setMaximumWidth(400)

        self.layout().addWidget(self.image_gallery)
        self.layout().addWidget(self.tag_display)

    def search_tags(self, text: str):
        """
        Alternative to clicking tags, Searches for tags based on text.
        Filtering is based on the text output section of the tagger.
        This is accessed by the TEXT user role ie: item.data(TEXT)
        :parameter text: string of tags to filter by
        """

        if text == "":
            return
        tags = [tag.strip() for tag in text.split(',')]
        regex_pattern = "(?=.*{})".format(")(?=.*".join(tags))  # Regex for selecting things with all tags
        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def filter_images(self):
        """
        Display images with the following tags.
        Filtering is based on the text output section of the tagger.
        This is accessed by the TEXT user role ie: item.data(TEXT)
        """

        # get all tags and remove (number)
        selected_tags = [
            item.text().split("   ", 1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]
        regex_pattern = "(?=.*{})".format(")(?=.*".join(selected_tags))  # Regex for selecting things with all tags

        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def clear_filter(self):
        """
        clears filters
        """
        self.tag_list.clearSelection()
        # Create QRegularExpression object
        regex = QRegularExpression('', QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def display_info(self, item):
        """
        Display file information in action box
        :param item: item in the model, item holds file path and tag info
        """
        self.file_name.setText(item.data(FILE_PATH))
        self.file_tags.setText(item.data(TEXT))

    def open_image(self, item):
        """
        Display Open image in image explorer
        :param item: item in the model, item holds file path and tag info
        """
        try:
            file_path = item.data(FILE_PATH)
            if file_path:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

        except Exception as e:
            print(e)


class MultiCompleter(QCompleter):
    """ Multi Tag completer, allows for comma separated tag searching"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setMaxVisibleItems(5)

    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)

        lst = str(self.widget().text()).split(', ')
        if len(lst) > 1:
            path = ', '.join(lst[:-1]) + ', ' + path

        return path

    def splitPath(self, path):
        return [path.split(',')[-1].strip()]


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


class TagListItemDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying larger item with larger text"""

    def sizeHint(self, option, index):
        # Customize the size of items
        return QSize(100, 25)  # Adjust the width and height as needed

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Customize the font size of the item text
        option.font.setPointSize(12)  # Adjust the font size as needed


if __name__ == '__main__':
    category_dict = {"rating": '9', "characters": '4', "general": '9'}
    thresh_dict = {"rating": 0.0, "characters": 0.7, "general": 0.35}

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
