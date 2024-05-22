import sys

from PyQt5.QtCore import QSortFilterProxyModel, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QListView, QStyleFactory, QGroupBox

from gui.dark_palette import create_dark_palette
from image_gallery import ImageGallery
from categories import TagDisplayWidget


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

        start_btn = QPushButton()
        start_ico = QIcon(r"ICONS/play.png")
        start_btn.setIcon(start_ico)
        start_btn.setIconSize(QSize(30, 30))
        start_btn.setToolTip("Predict tags for images")
        start_btn.clicked.connect(self.submit)

        write_btn = QPushButton()
        write_ico = QIcon(r"ICONS/WRITE.png")
        write_btn.setIcon(write_ico)
        write_btn.setIconSize(QSize(30, 30))
        write_btn.setToolTip("Write tags to file")
        write_btn.clicked.connect(self.write_tags)

        move_btn = QPushButton()
        move_ico = QIcon(r"ICONS/MOVE.png")
        move_btn.setIcon(move_ico)
        move_btn.setIconSize(QSize(30, 30))
        move_btn.setToolTip("Move images to folder")
        move_btn.clicked.connect(self.move_images)

        gallery_btn = QPushButton()
        gallery_ico = QIcon(r"ICONS/GALLERY.png")
        gallery_btn.setIcon(gallery_ico)
        gallery_btn.setIconSize(QSize(30, 30))
        # gallery_btn.clicked.connect()  # Uncomment and define the method when needed

        settings_btn = QPushButton()
        setting_ico = QIcon(r"ICONS/SETTINGS.png")
        settings_btn.setIcon(setting_ico)
        settings_btn.setIconSize(QSize(30, 30))
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.settings)

        navbar.layout().addWidget(start_btn)
        navbar.layout().addWidget(write_btn)
        navbar.layout().addWidget(move_btn)
        navbar.layout().addWidget(gallery_btn)
        navbar.layout().addStretch(10)
        navbar.layout().setSpacing(10)
        navbar.layout().addWidget(settings_btn)

        # Wrapup
        self.layout().addWidget(navbar)
        self.layout().addWidget(filter_widget)
        self.layout().addWidget(self.image_gallery)
        self.layout().addWidget(self.tag_display)

    def filter_tags(self, text):
        # Placeholder method for filtering tags
        print(f"Filtering tags with: {text}")

    def submit(self):
        # Placeholder method for submit action
        print("Submit action triggered")

    def write_tags(self):
        # Placeholder method for writing tags to file
        print("Write tags action triggered")

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