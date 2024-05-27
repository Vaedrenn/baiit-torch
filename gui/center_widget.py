import sys

from PyQt5.QtCore import QSortFilterProxyModel, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QListView, QStyleFactory, QGroupBox, QTabWidget, QMainWindow

from gui.dark_palette import create_dark_palette
from gui.gallery_model import ImageGalleryTableModel
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

        search_box = QHBoxLayout()
        self.searchbar.setPlaceholderText("  Filter Tags")
        self.searchbar.returnPressed.connect(lambda: self.filter_tags(self.searchbar.text()))
        self.clear_btn = QPushButton("Clear Filter")

        search_box.addWidget(self.searchbar)
        search_box.addWidget(self.clear_btn)

        self.caption.setReadOnly(True)
        self.caption.setMaximumHeight(200)

        filter_widget.layout().addLayout(search_box)
        filter_widget.layout().addWidget(self.tag_filter)

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
                "general": {"cute": 0.95, "animal": 0.85}
            },
            "../images/image2.jpg": {
                "rating": {"explicit": 0.95},
                "characters": {"dog": 0.9},
                "general": {"cute": 0.75, "animal": 0.65}
            },
            "../images/image3.jpg": {
                "rating": {"questionable": 0.8},
                "characters": {"bird": 0.85},
                "general": {"cute": 0.55, "animal": 0.75}
            }
        }
        self.process_results(results)

    def process_results(self, data: dict):
        # filename: data
        self.model = ImageGalleryTableModel(data)
        self.image_gallery.setModel(self.model)

    def filter_tags(self, text):
        # Placeholder method for filtering tags
        print(f"Filtering tags with: {text}")

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