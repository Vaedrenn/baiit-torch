import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication, QGridLayout, QLineEdit, \
    QPushButton, QHBoxLayout, QSpinBox, QFileDialog

from gui.custom_components.VerticalTabWidget import VerticalQTabWidget


class SettingsMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings Menu")
        self.setGeometry(100, 100, 600, 400)

        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create the tab widget
        self.tab_widget = VerticalQTabWidget()
        layout.addWidget(self.tab_widget)

        # Add tabs
        self.add_tabs()

    def add_tabs(self):
        # Configure Categories tab
        configure_categories_tab = EditCategoriesWidget()
        configure_categories_layout = QVBoxLayout()
        configure_categories_layout.addWidget(QLabel("Configure Categories Settings"))
        configure_categories_tab.setLayout(configure_categories_layout)
        self.tab_widget.addTab(configure_categories_tab, "Edit Categories")

        # Predict Options tab
        predict_options_tab = QWidget()
        predict_options_layout = QVBoxLayout()
        predict_options_layout.addWidget(QLabel("Predict Options Settings"))
        predict_options_tab.setLayout(predict_options_layout)
        self.tab_widget.addTab(predict_options_tab, "Predict")

        # Export Options tab
        export_options_tab = QWidget()
        export_options_layout = QVBoxLayout()
        export_options_layout.addWidget(QLabel("Export Options Settings"))
        export_options_tab.setLayout(export_options_layout)
        self.tab_widget.addTab(export_options_tab, "Export")

        # Move Options tab
        move_options_tab = QWidget()
        move_options_layout = QVBoxLayout()
        move_options_layout.addWidget(QLabel("Move Options Settings"))
        move_options_tab.setLayout(move_options_layout)
        self.tab_widget.addTab(move_options_tab, "Move")


class EditCategoriesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the main layout
        main_layout = QVBoxLayout()

        # Access the thresholds from the parent
        self.thresholds = {"rating": 0.5, "characters": 0.7, "general": 0.35}  # load from settings
        self.categories = {"rating": 9, "characters": 4, "general": 0, "user_tags": 9999}  # load from settings

        selection_grid = QGridLayout()

        label = QLabel("Use this to configure model category info as well as default thresholds")
        main_layout.addWidget(label)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Select model directory...")
        self.model_button = QPushButton("Browse")

        self.model_button.clicked.connect(lambda: self.browse_directory(self.model_input))

        selection_grid.addWidget(self.model_input, 0, 0)
        selection_grid.addWidget(self.model_button, 0, 1)
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

        main_layout.addStretch()

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

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)

    def submit(self):
        pass

    def reject(self):
        pass



class PredictOptions(QWidget):
    def __init__(self):
        super().__init__()


class ExportOptions(QWidget):
    def __init__(self):
        super().__init__()


class MoveOptions(QWidget):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsMenu()
    window.show()
    sys.exit(app.exec_())
