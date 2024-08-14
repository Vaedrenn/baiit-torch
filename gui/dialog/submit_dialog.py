from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QSpinBox, QPushButton, QLabel, \
    QLineEdit, QFileDialog, QProgressBar


from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QSpinBox, QPushButton, QLabel, \
    QLineEdit, QFileDialog, QProgressDialog

class ThresholdDialog(QDialog):
    results = pyqtSignal(object)  # Define the signal at the class level

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Thresholds')
        self.setMinimumSize(400, 200)

        # Create the main layout
        main_layout = QVBoxLayout()

        # Access the thresholds from the parent
        self.thresholds = self.parent().threshold
        self.categories = self.parent().categories
        selection_grid = QGridLayout()

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Select model directory...")
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory...")
        self.model_button = QPushButton("Browse")
        self.dir_button = QPushButton("Browse")

        if self.parent().model_folder:
            self.model_input.setText(self.parent().model_folder)

        self.model_button.clicked.connect(lambda: self.browse_directory(self.model_input))
        self.dir_button.clicked.connect(lambda: self.browse_directory(self.dir_input))

        selection_grid.addWidget(self.model_input, 0, 0)
        selection_grid.addWidget(self.model_button, 0, 1)
        selection_grid.addWidget(self.dir_input, 1, 0)
        selection_grid.addWidget(self.dir_button, 1, 1)
        main_layout.addLayout(selection_grid)

        # Add sliders and spinboxes for each threshold
        self.spinboxes = {}
        for category, value in self.thresholds.items():
            # Create a horizontal layout for the label and spinbox
            h_layout = QHBoxLayout()
            label = QLabel(f'{category} Threshold')
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(100)
            spinbox.setValue(int(value * 100))
            spinbox.setMaximumWidth(50)

            # Connect the spinbox value change signal to update the threshold
            spinbox.valueChanged.connect(lambda val, cat=category: self.update_threshold(cat, val))

            h_layout.addWidget(label)
            h_layout.addWidget(spinbox)

            self.spinboxes[category] = spinbox

            main_layout.addLayout(h_layout)

        # Add Confirm and Cancel buttons
        button_layout = QHBoxLayout()
        confirm_button = QPushButton('Confirm')
        confirm_button.clicked.connect(self.submit)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setPalette(self.parent().palette())

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)

    def update_threshold(self, category, value):
        self.thresholds[category] = value / 100.0

    def submit(self):
        # defaults for testing
        if not self.model_input.text():
            self.model_input.setText("wd-vit-tagger-v3")
        if not self.dir_input.text():
            self.dir_input.setText("images")

        self.parent().model_folder = self.model_input.text()  # save model folder

        # Spawn a new thread for the predict function
        self.thread = PredictThread(parent=self,
                                    model_path=self.model_input.text(),
                                    image_dir=self.dir_input.text(),
                                    categories=self.categories,
                                    thresholds=self.thresholds)
        self.thread.results.connect(self.handle_results)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        # Close the current dialog
        self.accept()

        # Open a new progress dialog
        self.progress_dialog = QProgressDialog("Loading Model...", "Cancel", 0, 100, self.parent())
        self.progress_dialog.setWindowTitle("Progress")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.canceled.connect(self.thread.terminate)
        self.progress_dialog.show()

    @pyqtSlot(object)
    def handle_results(self, results):
        self.results.emit(results)
        self.progress_dialog.close()

    @pyqtSlot(object)
    def update_progress(self, data):
        value, text = data
        self.progress_dialog.setLabelText(text)
        self.progress_dialog.setValue(value)


class PredictThread(QThread):
    results = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, parent, model_path, image_dir, categories, thresholds):
        super().__init__()
        self.model_path = model_path
        self.image_dir = image_dir
        self.categories = categories
        self.thresholds = thresholds
        self.parent = parent

    def run(self):
        from predict import predict
        results = predict(model_path=self.model_path,
                          image_dir=self.image_dir,
                          categories=self.categories,
                          thresholds=self.thresholds,
                          progress_callback=self.progress.emit)
        self.parent.results.emit(results)