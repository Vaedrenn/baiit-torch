import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QSplitter, \
    QSpinBox, QPushButton, QHBoxLayout, QCompleter, QLineEdit, QApplication, QListWidget

from gui.tuplelistwidget import TupleCheckListWidget
from gui.CheckListWidget import CheckListWidget


class TagDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.checklist = CheckListWidget()
        self.lineedit = QLineEdit()
        self.completer = QCompleter()
        self.add_btn = QPushButton("Add Tag")
        self.labels = []
        self.model = None

        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())
        font = QFont()
        font.setPointSize(14)  # Set the desired font size
        self.checklist.setFont(font)
        self.layout().addWidget(self.checklist)

        control_box = QHBoxLayout()
        control_box.addWidget(self.lineedit)
        control_box.addWidget(self.add_btn)

        self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        self.lineedit.setCompleter(self.completer)
        self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))
        self.add_btn.clicked.connect(lambda: self.add_tag(self.lineedit.text()))

        self.layout().addChildLayout(control_box)

    def set_model(self, model):
        self.model = model
        self.labels = self.model.tags.keys()

    def add_item(self, item: str, state: bool):
        """
        used to populate the list
        :param item: thing to add
        :param state: T/F
        :return: None
        """
        self.checklist.addItemState(item, state)

    def add_tag(self, text):
        """
        Adds user tags to tag list,
        You can add any tag you want here it does not have to be in labels.
        Adding a tag here will not add it to labels, you would have to add it manually to the txt
        """
        if self.labels is None:
            return

        self.add_item(text, True)


    def update_tag_status(self):
        """ Saves the check states of the current image"""
        pass

    def select_all_tags(self):
        """ Checks all tags"""
        if self.model is None:
            return


    def clear_tags(self):
        """ Unchecks all tags"""
        if self.model is None:
            return

