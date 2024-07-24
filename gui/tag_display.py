from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QDialog, QVBoxLayout, QCompleter, QPushButton, QHBoxLayout, QLineEdit, \
    QLabel

from gui.CheckListWidget import CheckListWidget
from gui.center_widget import MultiCompleter
from gui.gallery_model import ImageGalleryTableModel


class TagDisplay(CheckListWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.model = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_model(self, model: ImageGalleryTableModel):
        self.model = model

    def show_context_menu(self, position):
        menu = QMenu()

        select_all_action = QAction('Select All', self)
        select_all_action.triggered.connect(self.select_all)
        menu.addAction(select_all_action)

        deselect_all_action = QAction('Deselect All', self)
        deselect_all_action.triggered.connect(self.deselect_all)
        menu.addAction(deselect_all_action)

        add_tag_action = QAction('Add Tag', self)
        add_tag_action.triggered.connect(self.add_tag)
        menu.addAction(add_tag_action)

        menu.addSeparator()

        view_caption_action = QAction('View Caption', self)
        view_caption_action.triggered.connect(self.view_caption)
        menu.addAction(view_caption_action)

        edit_caption_action = QAction('Edit Caption', self)
        edit_caption_action.triggered.connect(self.edit_caption)
        menu.addAction(edit_caption_action)

        menu.exec_(self.mapToGlobal(position))

    def select_all(self):
        self.checkAll()

    def deselect_all(self):
        self.unCheckAll()

    def add_tag(self):
        dialog = add_tag_dialog(parent=self.parentWidget())
        dialog.exec_()

    def view_caption(self):
        pass

    def edit_caption(self):
        pass


class add_tag_dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Tags")

        main_layout = QVBoxLayout()

        self.text = QLabel(f"Adding Tags to: {parent.current_image}")

        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText("  Add a tag here and hit enter")
        button = QPushButton("Add Tag")

        self.completer = MultiCompleter(self.model.tags.keys())
        self.lineedit.setCompleter(self.completer)

        self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))
        # button.clicked.connect(lambda: self.add_tag(self.lineedit.text()))

        tag_box = QHBoxLayout()
        tag_box.addWidget(self.lineedit)
        tag_box.addWidget(button)
        tag_box.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.text)

        main_layout.addLayout(tag_box)
        self.setLayout(main_layout)
