import sys

from PyQt5.QtCore import QSize, QRegularExpression, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QStyleFactory, QMainWindow, QListWidget, \
    QListWidgetItem

from categories import TagDisplayWidget
from gui.dark_palette import create_dark_palette
from gui.gallery_model import ImageGalleryTableModel
from image_gallery import ImageGallery


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setPalette(create_dark_palette())
        self.center_widget = CentralWidget()
        self.setCentralWidget(self.center_widget)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.threshold = {"rating": 0.0, "characters": 0.7, "general": 0.35}  # load from settings
        self.categories = {"rating": 9, "characters": 4, "general": 0}  # load from settings
        self.model = None
        self.model_folder = None  # cache
        self.proxy_model = QSortFilterProxyModel()

        self.searchbar = QLineEdit()
        self.filter_completer = QCompleter()
        self.clear_btn = QPushButton()
        self.tag_list = QListWidget()
        self.caption = QTextEdit()

        self.image_gallery = ImageGallery()
        self.tag_display = TagDisplayWidget(categories=self.categories, thresholds=self.threshold)

        self.initUI()

    def initUI(self):
        self.setLayout(QHBoxLayout())
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setPalette(create_dark_palette())

        # Frame 1  tag search and filter, caption
        filter_widget = QWidget()
        filter_widget.setLayout(QVBoxLayout())
        filter_widget.layout().setContentsMargins(0, 0, 0, 0)
        filter_widget.setMaximumWidth(300)

        search_box = QHBoxLayout()
        self.searchbar.setPlaceholderText("  Filter Tags")
        self.searchbar.returnPressed.connect(lambda: self.filter_images(self.searchbar.text()))
        self.clear_btn = QPushButton("Clear Filter")
        self.clear_btn.clicked.connect(self.clear_filter)

        search_box.addWidget(self.searchbar)
        search_box.addWidget(self.clear_btn)

        self.tag_list.setSelectionMode(QListWidget.MultiSelection)  # Toggle style selection
        self.tag_list.itemClicked.connect(self.filter_images)  # on click filter

        self.caption.setReadOnly(True)
        self.caption.setMaximumHeight(200)

        filter_widget.layout().addLayout(search_box)
        filter_widget.layout().addWidget(self.tag_list)

        # Frame 2   image gallery

        # Frame 3   tag display, shows all tags related to image separated into their respective categories
        self.tag_display.setMaximumWidth(300)
        self.tag_display.layout().setContentsMargins(0, 0, 0, 0)

        # Navbar
        navbar = QWidget()
        navbar.setLayout(QVBoxLayout())
        navbar.setMaximumWidth(40)
        navbar.layout().setContentsMargins(0, 0, 0, 0)
        navbar.layout().setSpacing(5)
        self.add_buttons_to_navbar(navbar)

        # Wrapup
        self.layout().addWidget(navbar)
        self.layout().addWidget(filter_widget)
        self.layout().addWidget(self.image_gallery)
        self.layout().addWidget(self.tag_display)

    def add_buttons_to_navbar(self, navbar):
        buttons_info = [
            ("Predict tags for images", "ICONS/play.png", self.submit),
            ("Write tags to file", "ICONS/WRITE.png", self.write_tags),
            ("Export tags", "ICONS/EXPORT.png", self.export),
            ("Move images to folder", "ICONS/MOVE.png", self.move_images),
            ("", "ICONS/GALLERY.png", self.move_images),  # Connect when needed
            ("Settings", "ICONS/SETTINGS.png", self.settings)
        ]

        for tooltip, icon_path, callback in buttons_info:
            btn = QPushButton()
            btn.setIconSize(QSize(30, 30))
            btn.setIcon(QIcon(icon_path))
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            if tooltip == "Settings":
                navbar.layout().addStretch()
            navbar.layout().addWidget(btn)

    def submit(self):
        # dialog = self.SubmitDialog(self)
        # dialog.results.connect(lambda x: self.process_results(x))
        # self.parent().model_folder = dialog.model_input
        # dialog.exec_()
        print("submit clicked")
        results = {
            "../images/image1.jpg": {
                "rating": {"safe": 0.9},
                "characters": {"cat": 0.8},
                "general": {"cute": 0.95, "animal": 0.85},
                "caption": "safe, cat, cute, animal"
            },
            "../images/image2.jpg": {
                "rating": {"safe": 0.95},
                "characters": {"dog": 0.9},
                "general": {"cute": 0.75, "animal": 0.65},
                "caption": "safe, dog, cute, animal"
            },
            "../images/image3.jpg": {
                "rating": {"safe": 0.8},
                "characters": {"bird": 0.85},
                "general": {"cute": 0.55, "animal": 0.75},
                "caption": "safe, bird, cute, animal"
            }
        }
        self.process_results(results)

    def process_results(self, data: dict):
        # filename: data
        self.model = ImageGalleryTableModel(data)
        self.proxy_model.setSourceModel(self.model)
        self.image_gallery.setModel(self.proxy_model)
        self.tag_list.clear()
        for tag, count in sorted(self.model.tags.items(), key=lambda item: item[1], reverse=True):
            formatted_tag = f"{count:>4}  {tag}"
            self.tag_list.addItem(QListWidgetItem(formatted_tag))

    def filter_images(self):
        # Get all tags and remove (number)
        selected_tags = [
            item.text().split(maxsplit=1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]
        if not selected_tags:
            # Clear filter if no tags are selected
            self.proxy_model.setFilterRegularExpression(QRegularExpression())
            return

        regex_pattern = "(?=.*{})".format(")(?=.*".join(selected_tags))  # Regex for selecting things with all tags

        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(
            Qt.UserRole)  # Filter by UserRole, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def clear_filter(self):
        """
        clears filters
        """
        self.tag_list.clearSelection()
        # Create QRegularExpression object
        regex = QRegularExpression('', QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(
            Qt.UserRole)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def write_tags(self):
        # Placeholder method for writing tags to file
        print("Write tags action triggered")

    def export(self):
        print("Export tags action triggered")

    def move_images(self):
        # Placeholder method for moving images
        print("Move images action triggered")

    def settings(self):
        # Placeholder method for settings
        print("Settings action triggered")


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QMainWindow using QWidget as central widget
    window = CentralWidget()
    window.resize(1200, 800)
    window.show()

    # Execute application
    sys.exit(app.exec())
