import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QSplitter, \
    QSpinBox, QPushButton, QHBoxLayout, QGroupBox, QCompleter, QLineEdit, QApplication, QComboBox

from gui.tuplelistwidget import TupleCheckListWidget


class TagDisplayWidget(QSplitter):
    def __init__(self, categories: dict, thresholds: dict):
        super().__init__()

        self.categories = categories  # category_dict = {"rating": 9, "general": 0, "characters": 4}
        self.thresholds = thresholds  # thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
        self.labels = []
        self.initUI()

    def initUI(self):
        self.setOrientation(Qt.Vertical)
        for category, cat_id in self.categories.items():
            new_item = TagDisplayComponent(category, cat_id, self.thresholds[category])
            self.addWidget(new_item)

        self.lineedit = QLineEdit()
        self.completer = QCompleter()
        tag_box = QWidget()
        tag_box.setLayout(QHBoxLayout())

        self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        button = QPushButton("Add Tag")
        self.cate_options = QComboBox()
        try:
            self.cate_options.addItems(self.categories.values())
        except TypeError:
            print("TagDisplayWidget.cate_options has type 'int' but 'str' is expected, \n"
                  " need to convert the ints in TagDisplayWidget.categories.values to strings ")

        self.lineedit.setCompleter(self.completer)
        self.lineedit.returnPressed.connect(lambda: self.add_tags(self.lineedit.text()))
        button.clicked.connect(lambda: self.add_tags(self.lineedit.text()))

        tag_box.layout().addWidget(self.lineedit)
        tag_box.layout().addWidget(self.cate_options)
        tag_box.layout().addWidget(button)
        tag_box.setContentsMargins(0, 5, 5, 20)
        self.addWidget(tag_box)


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
        plus_btn = QPushButton('+')
        minus_btn = QPushButton('-')

        font = QFont()
        font.setPointSize(10)
        label.setFont(font)

        plus_btn.setMaximumWidth(30)
        minus_btn.setMaximumWidth(30)

        slider.setMinimum(1)  # Anything lower than 1 will result in long load times when updating page
        slider.setMaximum(100)

        spinbox.setMinimum(1)
        spinbox.setMaximum(100)

        slider.valueChanged.connect(lambda value: spinbox.setValue(value))
        spinbox.valueChanged.connect(lambda value: slider.setValue(value))
        slider.valueChanged.connect(self.updateThreshold)
        spinbox.valueChanged.connect(self.updateThreshold)

        slider.setValue(int(self.threshold * 100))

        top = QGroupBox()
        top.setLayout(QHBoxLayout())
        top.layout().addWidget(label)
        top.layout().addStretch(1)
        top.layout().addWidget(plus_btn)
        top.layout().addWidget(minus_btn)
        # top.layout().setContentsMargins(0, 0, 0, 0)

        mid = QGroupBox()
        mid.setLayout(QHBoxLayout())
        mid.layout().addWidget(slider)
        mid.layout().addWidget(spinbox)
        # mid.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(top)
        self.layout().addWidget(mid)
        self.layout().addWidget(self.tag_list)

    def updateThreshold(self, value):
        self.threshold = value


if __name__ == '__main__':
    category_dict = {"rating": '9', "general": '0', "characters": '4'}
    thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}

    app = QApplication(sys.argv)
    window = TagDisplayWidget(categories=category_dict, thresholds=thresh_dict)
    window.show()
    sys.exit(app.exec_())
