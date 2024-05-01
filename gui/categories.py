import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QSplitter, \
    QSpinBox, QPushButton, QHBoxLayout, QGroupBox, QCompleter, QLineEdit, QApplication, QComboBox, QFrame

from gui.tuplelistwidget import TupleCheckListWidget


class TagDisplayWidget(QWidget):
    def __init__(self, categories: dict, thresholds: dict):
        super().__init__()
        self.categories = categories  # category_dict = {"rating": 9, "general": 0, "characters": 4}
        self.thresholds = thresholds  # thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
        self.labels = []
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())
        self.tag_display = TagDisplaySplitter(self.categories, self.thresholds)
        self.layout().addWidget(self.tag_display)
        self.lineedit = QLineEdit()
        self.completer = QCompleter()
        tag_box = QWidget()
        tag_box.setLayout(QHBoxLayout())

        self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        button = QPushButton("Add Tag")

        self.lineedit.setCompleter(self.completer)
        self.lineedit.returnPressed.connect(lambda: self.add_tags(self.lineedit.text()))
        button.clicked.connect(lambda: self.add_tags(self.lineedit.text()))

        tag_box.layout().addWidget(self.lineedit)
        tag_box.layout().addWidget(button)
        tag_box.layout().setContentsMargins(0, 0, 0, 0)

        button_box = QWidget()
        button_box.setLayout(QHBoxLayout())
        button_box.layout().setContentsMargins(0, 0, 0, 0)

        store_tags = QPushButton("Save Changes")
        b_select_all = QPushButton("Select All")
        b_clear = QPushButton("Clear")

        store_tags.clicked.connect(lambda: self.update_tag_status())
        b_select_all.clicked.connect(lambda: self.select_all_tags())
        b_clear.clicked.connect(lambda: self.clear_tags())

        button_box.layout().addWidget(store_tags)
        button_box.layout().addWidget(b_select_all)
        button_box.layout().addWidget(b_clear)

        self.layout().addWidget(tag_box)
        self.layout().addWidget(button_box)

class TagDisplaySplitter(QSplitter):
    def __init__(self, categories: dict, thresholds: dict):
        super().__init__()

        self.categories = categories  # category_dict = {"rating": 9, "general": 0, "characters": 4}
        self.thresholds = thresholds  # thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
        self.initUI()

    def initUI(self):
        self.setOrientation(Qt.Vertical)
        for category, cat_id in self.categories.items():
            new_item = TagDisplayComponent(category, cat_id, self.thresholds[category])
            self.addWidget(new_item)
        self.setChildrenCollapsible(False)


class TagDisplayComponent(QWidget):
    def __init__(self, cat_name: str, cat_id: int, threshold=50):
        super().__init__()
        self.tag_list = TupleCheckListWidget()
        self.category = cat_name
        self.category_id = cat_id
        self.threshold = threshold
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())
        label = QLabel(self.category.capitalize())
        slider = QSlider(Qt.Horizontal)
        spinbox = QSpinBox()
        # self.layout().setContentsMargins(0, 0, 0, 0)

        font = QFont()
        font.setPointSize(10)
        label.setFont(font)

        slider.setMinimum(1)  # Anything lower than 1 will result in long load times when updating page
        slider.setMaximum(100)

        spinbox.setMinimum(1)
        spinbox.setMaximum(100)

        slider.valueChanged.connect(lambda value: spinbox.setValue(value))
        spinbox.valueChanged.connect(lambda value: slider.setValue(value))
        slider.valueChanged.connect(self.updateThreshold)
        spinbox.valueChanged.connect(self.updateThreshold)

        slider.setValue(int(self.threshold * 100))

        top = QWidget()
        top.setLayout(QHBoxLayout())
        top.layout().addWidget(label)
        # top.layout().addStretch(1)
        top.layout().addWidget(QLabel("    "))
        top.layout().setContentsMargins(0, 0, 0, 0)
        top.layout().addWidget(slider)
        top.layout().addWidget(spinbox)

        # mid = QWidget()
        # mid.setLayout(QHBoxLayout())
        # mid.layout().addWidget(slider)
        # mid.layout().addWidget(spinbox)
        # mid.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(top)
        # self.layout().addWidget(mid)
        self.layout().addWidget(self.tag_list)

    def updateThreshold(self, value):
        self.threshold = value


if __name__ == '__main__':
    category_dict = {"rating": '9', "characters": '4', "general": '9'}
    thresh_dict = {"rating": 0.0, "characters": 0.35, "general": 7}

    app = QApplication(sys.argv)
    window = TagDisplayWidget(categories=category_dict, thresholds=thresh_dict)
    window.show()
    sys.exit(app.exec_())
