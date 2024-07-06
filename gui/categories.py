import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QSplitter, \
    QSpinBox, QPushButton, QHBoxLayout, QCompleter, QLineEdit, QApplication

from gui.tuplelistwidget import TupleCheckListWidget


class TagDisplayWidget(QWidget):
    def __init__(self, thresholds: dict):
        super().__init__()
        self.widget_index = {}
        self.labels = {}
        self.setLayout(QVBoxLayout())
        self.tag_display = QSplitter()
        self.lineedit = QLineEdit()
        self.completer = QCompleter()

        # Create components from categories
        for category, value in thresholds.items():
            new_component = TagDisplayComponent(cat_name=category, threshold=value)
            self.tag_display.addWidget(new_component)
            self.widget_index[category] = new_component
        self.tag_display.setOrientation(Qt.Vertical)
        #
        # # buttons at the bottom
        # tag_box = QHBoxLayout()
        # self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        # button = QPushButton("Add Tag")
        #
        # self.lineedit.setCompleter(self.completer)
        # self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))
        # button.clicked.connect(lambda: self.add_tag(self.lineedit.text()))
        #
        # tag_box.addWidget(self.lineedit)
        # tag_box.addWidget(button)
        # tag_box.setContentsMargins(0, 0, 0, 0)
        #
        # button_box = QHBoxLayout()
        # button_box.setContentsMargins(0, 0, 0, 0)
        #
        # store_tags = QPushButton("Save Changes")
        # b_select_all = QPushButton("Select All")
        # b_clear = QPushButton("Clear")
        #
        # store_tags.clicked.connect(lambda: self.update_tag_status())
        # b_select_all.clicked.connect(lambda: self.select_all_tags())
        # b_clear.clicked.connect(lambda: self.clear_tags())
        #
        # button_box.layout().addWidget(store_tags)
        # button_box.layout().addWidget(b_select_all)
        # button_box.layout().addWidget(b_clear)

        self.layout().addWidget(self.tag_display)
        # self.layout().addLayout(tag_box)
        # self.layout().addLayout(button_box)

    def update_tag_status(self):
        """ Saves the check states of the current image"""
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

    def select_all_tags(self):
        """ Checks all tags"""
        pass

    def clear_tags(self):
        """ Unchecks all tags"""
        pass

    def get(self, category):
        return self.widget_index[category]


class TagDisplayComponent(QWidget):
    def __init__(self, cat_name: str, threshold=50):
        super().__init__()
        self.selected = None
        self.tag_list = TupleCheckListWidget()
        self.category = cat_name
        self.threshold = threshold

        self.setLayout(QVBoxLayout())
        label = QLabel(self.category.capitalize())

        self.layout().setContentsMargins(0, 0, 5, 5)

        font = QFont()
        font.setPointSize(10)
        label.setFont(font)

        top = QHBoxLayout()
        top.layout().addWidget(label)
        top.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addLayout(top)
        self.layout().addWidget(self.tag_list)

    def add_dict(self, tags: dict, checkstate: dict):
        self.tag_list.clear()
        for tag_name, value in tags.items():
            percentage = f"{value * 100:.2f}%"  # Format value as percentage
            self.tag_list.addPair(tag_name, percentage, True)


