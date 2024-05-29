from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QSpinBox, QPushButton, QLabel, QLineEdit, QFileDialog
from PyQt5.QtCore import pyqtSignal
import sys

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
        confirm_button.clicked.connect(self.accept)
        confirm_button.clicked.connect(self.submit)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)

    def update_threshold(self, category, value):
        self.thresholds[category] = value / 100.0

    def submit(self):
        # defaults for testing
        if not self.model_input.text():
            self.model_input.setText("../wd-vit-tagger-v3")
        if not self.dir_input.text():
            self.dir_input.setText("../images")

        self.parent().model_folder = self.model_input.text()  # save model folder
        from predict import predict
        results = predict(model_path=self.model_input.text(),
                          image_dir=self.dir_input.text(),
                          categories=self.categories,
                          thresholds=self.thresholds)

        self.results.emit(results)

# class ParentWindow(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('Parent Window')
#         self.threshold = {"rating": 0.0, "characters": 0.7, "general": 0.35}  # load from settings
#         self.categories = {"rating": 9, "characters": 4, "general": 0}  # load from settings
#
#         open_dialog_button = QPushButton('Open Threshold Dialog')
#         open_dialog_button.clicked.connect(self.open_threshold_dialog)
#
#         layout = QVBoxLayout()
#         layout.addWidget(open_dialog_button)
#         self.setLayout(layout)
#
#     def open_threshold_dialog(self):
#         dialog = ThresholdDialog(self)
#         dialog.results.connect(self.update_thresholds)
#         if dialog.exec_():
#             # Retrieve the updated values from the spinboxes
#             for category, spinbox in dialog.spinboxes.items():
#                 self.threshold[category] = spinbox.value() / 100.0
#             print("Thresholds updated:", self.threshold)
#         else:
#             print("Thresholds update canceled.")
#
#     def update_thresholds(self, new_thresholds):
#         print("Thresholds received:", new_thresholds)
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_win = ParentWindow()
#     main_win.show()
#     sys.exit(app.exec_())
