import sys

from PyQt5.QtCore import QSortFilterProxyModel, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QListView, QStyleFactory, QGroupBox, QTabWidget, QMainWindow

from gui.dark_palette import create_dark_palette
from image_gallery import ImageGallery
from categories import TagDisplayWidget


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

        self.searchbar = QLineEdit()
        self.filter_completer = QCompleter()
        self.clear_btn = QPushButton()
        self.tag_filter = QListView()
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

        search_box = QWidget()
        search_box.setLayout(QHBoxLayout())
        search_box.layout().setContentsMargins(0, 0, 0, 0)

        self.searchbar.setPlaceholderText("  Filter Tags")
        self.searchbar.returnPressed.connect(lambda: self.filter_tags(self.searchbar.text()))
        self.clear_btn = QPushButton("Clear Filter")

        search_box.layout().addWidget(self.searchbar)
        search_box.layout().addWidget(self.clear_btn)

        self.caption.setReadOnly(True)
        self.caption.setMaximumHeight(200)

        filter_widget.layout().addWidget(search_box)
        filter_widget.layout().addWidget(self.tag_filter)
        filter_widget.layout().addWidget(self.caption)

        # Frame 2   image gallery
        # self.image_gallery

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

    def filter_tags(self, text):
        # Placeholder method for filtering tags
        print(f"Filtering tags with: {text}")

    def submit(self):
        # Placeholder method for submit action
        print("Submit action triggered")

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