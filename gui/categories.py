import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QSplitter, \
    QStyledItemDelegate, QListView, QGridLayout, QSpinBox, QPushButton, QHBoxLayout, QFrame, QGroupBox

from gui.tuplelistwidget import TupleCheckListWidget


class TagDisplayWidget(QSplitter):
    def __init__(self):
        super().__init__()
        self.categories = {}  # category_dict = {"rating": 9, "general": 0, "characters": 4}
        self.thresholds = {}  # thresh_dict = {"rating": 0.0, "general": 0.35, "characters": 7}
        self.initUI()

    def initUI(self):
        self.setOrientation(Qt.Vertical)


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

        slider.setValue(self.threshold)

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

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = TagDisplayComponent('goose',6,50)
#     window.show()
#     sys.exit(app.exec_())