from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QDialog, QVBoxLayout, QCompleter, QPushButton, QHBoxLayout, QLineEdit, \
    QLabel

from gui.CheckListWidget import CheckListWidget
from gui.gallery_model import ImageGalleryTableModel
from gui.multicompleter import MultiCompleter


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
        if self.model is None:
            return
        dialog = add_tag_dialog(parent=self.parentWidget())
        dialog.exec_()

    def view_caption(self):
        pass

    def edit_caption(self):
        pass


class add_tag_dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = parent.model

        self.setWindowTitle("Add Tags")

        main_layout = QVBoxLayout()

        self.text = QLabel(f"Adding Tags to: {parent.current_image}")

        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText("  Separate each tag with a comma")
        button = QPushButton("Add Tag")

        self.completer = MultiCompleter(self.parent().model.tags.keys())
        self.lineedit.setCompleter(self.completer)

        self.lineedit.returnPressed.connect(lambda: self.add_tag(self.lineedit.text()))
        button.clicked.connect(lambda: self.add_tag(self.lineedit.text()))

        tag_box = QHBoxLayout()
        tag_box.addWidget(self.lineedit)
        tag_box.addWidget(button)
        tag_box.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.text)

        main_layout.addLayout(tag_box)
        self.setLayout(main_layout)

    def add_tag(self, text):
        """
        Add new tags to the DataFrame and update the relevant image row.
        :param text: Comma-separated string of new tags.
        """
        curr_img = self.parent().current_image

        tags = [tag.strip() for tag in text.split(",")]

        df = self.model.state

        for t in tags:
            if t not in self.model.tags.keys():
                # add new column to the dataframe set all fields to False
                df[t] = False

            # if there is no field for user tags make one
            if 'user_tags' not in self.model.results[curr_img].keys():
                self.model.results[curr_img]['user_tags'] = {}

            self.model.results[curr_img]['user_tags'][str(t)] = 1

            # Find the row index of the current image and set the new tag to True
            row_idx = df.index[df['filename'] == curr_img].tolist()
            if row_idx:
                df.at[row_idx[0], t] = True

