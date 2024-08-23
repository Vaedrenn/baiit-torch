import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication

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
        configure_categories_tab = QWidget()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsMenu()
    window.show()
    sys.exit(app.exec_())
