from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

from gui.custom_components.multicompleter import MultiCompleter


class AddTagDialog(QDialog):
    new_tags = pyqtSignal(str)

    def __init__(self, message, parent=None,):
        super().__init__(parent)
        self.model = parent.model

        self.setWindowTitle("Add Tags")

        main_layout = QVBoxLayout()

        self.text = QLabel(message)

        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText("  Separate each tag with a comma")
        button = QPushButton("Add Tag")

        self.completer = MultiCompleter(self.parent().model.tags.keys())
        self.lineedit.setCompleter(self.completer)

        # self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))  # adds twice
        button.clicked.connect(lambda: self.add_tag(self.lineedit.text()))

        tag_box = QHBoxLayout()
        tag_box.addWidget(self.lineedit)
        tag_box.addWidget(button)
        tag_box.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.text)

        main_layout.addLayout(tag_box)
        self.setLayout(main_layout)

    def add_tag(self, text):
        self.new_tags.emit(text)
        self.accept()
