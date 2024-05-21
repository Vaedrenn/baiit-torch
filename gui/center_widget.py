import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QListView


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.searchbar = QLineEdit()
        self.filter_completer = QCompleter()
        self.clear_btn = QPushButton()
        self.tag_filter = QListView()
        self.caption = QTextEdit()

        self.image_gallery = None
        self.tag_display = None

        self.initUI()

    def initUI(self):
        self.setLayout(QHBoxLayout())

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

        # Frame 2

        # Frame 3

        # Wrapup
        self.layout().addWidget(filter_widget)
        self.layout().addWidget(self.image_gallery)
        self.layout().addWidget(self.tag_display)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QMainWindow using QWidget as central widget
    window = CentralWidget()
    window.resize(1200, 800)
    window.show()

    # Execute application
    sys.exit(app.exec())