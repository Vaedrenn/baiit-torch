import sys

from PyQt5.QtCore import QSortFilterProxyModel, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QStyleFactory, QMainWindow, QPushButton, QVBoxLayout, \
    QStatusBar, QInputDialog, QFileDialog, QLineEdit, QGridLayout, QDialog, QProgressBar

from categories import TagDisplayWidget
from gui.dark_palette import create_dark_palette
from image_gallery import ImageGallery
from predict import predict


def browse_directory(line_edit):
    """
        looks for the target directory where images are to be tagged
        :parameter line_edit: QLineEdit where text will be displayed
        :return directory_path: abs path of the directory
        """

    directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
    if directory_path:
        line_edit.setText(directory_path)
        return directory_path


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        category_dict = {"rating": 9, "characters": 4, "general": 0}
        thresh_dict = {"rating": 0.0, "characters": 0.7, "general": 0.35}
        self.threshold = thresh_dict
        self.categories = category_dict
        self.model = None
        self.model_folder = None
        self.proxy_model = QSortFilterProxyModel()

        self.image_gallery = ImageGallery()
        self.tag_display = TagDisplayWidget(categories=self.categories, thresholds=self.threshold)

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        self.setLayout(QHBoxLayout())
        self.tag_display.setMaximumWidth(350)
        self.tag_display.layout().setContentsMargins(0,0,0,0)

        frame1 = QWidget()
        frame1.setLayout(QVBoxLayout())
        frame1.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(frame1)
        self.layout().addWidget(self.tag_display)

        button_box = QWidget()
        button_box.setLayout(QHBoxLayout())
        button_box.layout().setContentsMargins(0, 0, 0, 0)

        submit_btn = QPushButton("Submit")
        filter_btn = QPushButton("Filter")
        tag_curr_btn = QPushButton("Tag Current")
        tag_all_btn = QPushButton("Tag All")

        submit_btn.clicked.connect(lambda: self.submit())
        # tag_curr_btn.clicked.connect(lambda: self.select_all_tags())
        # tag_all_btn.clicked.connect(lambda: self.clear_tags())

        button_box.layout().addWidget(submit_btn)
        button_box.layout().addWidget(filter_btn)
        button_box.layout().addWidget(tag_curr_btn)
        button_box.layout().addWidget(tag_all_btn)

        frame1.layout().addWidget(self.image_gallery)
        frame1.layout().addWidget(button_box)

    def submit(self):
        dialog = self.SubmitDialog(self)
        dialog.results.connect(lambda x: self.process_results(x))
        self.parent().model_folder = dialog.model_input
        dialog.exec_()

    def process_results(self, data: dict):
        # filename: data
        for filename in data.keys():
            tags = data[filename]
            for category in self.categories.keys():
                a = self.tag_display.tag_display.indexes[category]
                a.add_dict(tags=tags[category])

    class SubmitDialog(QDialog):
        results = pyqtSignal(object)

        def __init__(self, parent):
            super().__init__(parent)
            self.setLayout(QGridLayout())
            self.setWindowTitle("Predict Tags")
            self.model_input = QLineEdit()
            self.model_input.setPlaceholderText("Select model directory...")
            self.dir_input = QLineEdit()
            self.dir_input.setPlaceholderText("Select directory...")
            self.model_button = QPushButton("Browse")
            self.dir_button = QPushButton("Browse")
            self.confirm_btn = QPushButton("Submit")
            self.cancel_btn = QPushButton("Cancel")

            self.model_button.clicked.connect(lambda: browse_directory(self.model_input))
            self.dir_button.clicked.connect(lambda: browse_directory(self.dir_input))
            self.confirm_btn.clicked.connect(lambda: self.call_predict())
            self.cancel_btn.clicked.connect(lambda: self.reject())

            self.layout().addWidget(self.model_input, 0, 0)
            self.layout().addWidget(self.model_button, 0, 1)
            self.layout().addWidget(self.dir_input, 1, 0)
            self.layout().addWidget(self.dir_button, 1, 1)
            self.layout().addWidget(self.confirm_btn, 2, 0)
            self.layout().addWidget(self.cancel_btn, 2, 1)

            if self.parent().model_folder is not None:
                self.model_input.setText(self.parent().model_folder)


        def call_predict(self):
            if self.dir_input.text() == "" or None:
                return
            if self.model_input.text() == "" or None:
                return
            stuff = predict(thresholds=self.parent().threshold, categories=self.parent().categories,
                            image_dir=self.dir_input.text(), model_path=self.model_input.text())

            self.parent().model_folder = self.model_input.text()
            self.results.emit(stuff)
            self.done(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setPalette(create_dark_palette())
        self.center_widget = CentralWidget()
        self.setCentralWidget(self.center_widget)
        self.setStatusBar(QStatusBar())


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QMainWindow using QWidget as central widget
    window = MainWindow()
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec())
