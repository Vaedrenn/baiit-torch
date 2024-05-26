import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QSlider, QSpinBox, QPushButton, QHBoxLayout, QLabel, \
    QLineEdit, QGridLayout
from PyQt5.QtCore import Qt


class ThresholdDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Thresholds')
        self.setMinimumSize(400, 200)

        # Create the main layout
        main_layout = QVBoxLayout()

        # Access the thresholds from the parent
        self.thresholds = self.parent().threshold.items()
        selection_grid = QGridLayout()

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Select model directory...")
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory...")
        self.model_button = QPushButton("Browse")
        self.dir_button = QPushButton("Browse")

        selection_grid.addWidget(self.model_input, 0, 0)
        selection_grid.addWidget(self.model_button, 0, 1)
        selection_grid.addWidget(self.dir_input, 1, 0)
        selection_grid.addWidget(self.dir_button, 1, 1)
        main_layout.addLayout(selection_grid)

        # Add sliders and spinboxes for each threshold
        self.sliders = {}
        self.spinboxes = {}
        for category, value in self.thresholds:
            # Create a horizontal layout for the label and spinbox
            h_layout = QHBoxLayout()
            label = QLabel(f'{category} Threshold')
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(100)
            spinbox.setValue(value)
            spinbox.setMaximumWidth(50)

            h_layout.addWidget(label)
            h_layout.addWidget(spinbox)

            # Create and configure the slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(1)
            slider.setMaximum(100)
            slider.setTickInterval(1)
            slider.setValue(value)

            # Connect slider and spinbox signals
            slider.valueChanged.connect(lambda val, spn=spinbox: spn.setValue(val))
            spinbox.valueChanged.connect(lambda val, sld=slider: sld.setValue(val))

            # Add to layout and store references
            self.sliders[category] = slider
            self.spinboxes[category] = spinbox

            main_layout.addLayout(h_layout)
            main_layout.addWidget(slider)

        # Add Confirm and Cancel buttons
        button_layout = QHBoxLayout()
        confirm_button = QPushButton('Confirm')
        confirm_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


class ParentWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Parent Window')
        self.threshold = {
            'General Tags': 50,
            'Character Tags': 85,
            'Example Category': 70
        }

        open_dialog_button = QPushButton('Open Threshold Dialog')
        open_dialog_button.clicked.connect(self.open_threshold_dialog)

        layout = QVBoxLayout()
        layout.addWidget(open_dialog_button)
        self.setLayout(layout)

    def open_threshold_dialog(self):
        dialog = ThresholdDialog(self)
        if dialog.exec_():
            # Retrieve the updated values from the sliders
            for category in dialog.sliders:
                self.threshold[category] = dialog.sliders[category].value()
            print("Thresholds updated:", self.threshold)
        else:
            print("Thresholds update canceled.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = ParentWindow()
    main_win.show()
    sys.exit(app.exec_())
