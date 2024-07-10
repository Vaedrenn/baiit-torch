import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QSplitter, \
    QSpinBox, QPushButton, QHBoxLayout, QCompleter, QLineEdit, QApplication, QListWidget

from gui.tuplelistwidget import TupleCheckListWidget


class TagDisplayWidget(QWidget):
    def __init__(self, model):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.checklist = QListWidget()
        self.lineedit = QLineEdit()
        self.completer = QCompleter()
        self.add_btn = QPushButton("Add Tag")
        self.labels = []

        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.checklist)

        control_box = QHBoxLayout()
        control_box.addWidget(self.lineedit)
        control_box.addWidget(self.add_btn)

        self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        self.lineedit.setCompleter(self.completer)
        self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))
        self.add_btn.clicked.connect(lambda: self.add_tag(self.lineedit.text()))

        self.layout().addChildLayout(control_box)

    def add_item(self, item, state):
        pass

    def add_tag(self, text):
        """
        Adds user tags to tag list,
        You can add any tag you want here it does not have to be in labels.
        Adding a tag here will not add it to labels, you would have to add it manually to the txt
        """
        if self.labels is None:
            return

        pass

    def update_tag_status(self):
        """ Saves the check states of the current image"""
        pass

    def select_all_tags(self):
        """ Checks all tags"""
        pass

    def clear_tags(self):
        """ Unchecks all tags"""
        pass