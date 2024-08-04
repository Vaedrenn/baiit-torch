from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMenu, QAction, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, \
    QLabel

from gui.CheckListWidget import CheckListWidget
from gui.caption import CaptionWindow
from gui.gallery_model import ImageGalleryTableModel
from gui.multicompleter import MultiCompleter


class TagDisplay(CheckListWidget):

    def __init__(self):
        super().__init__()
        self.model = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemChanged.connect(lambda x: self.state_changed(x))

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
        if self.model is None or self.parent().current_item is None:
            return
        dialog = AddTagDialog(parent=self.parentWidget())
        dialog.exec_()
        self.parent().update_page(self.parent().current_item)

    def update_caption(self):
        if self.model is None or self.parent().current_item is None:
            return
        curr_img = self.parent().current_item.data()

        row = self.model.state[self.model.state['filename'] == curr_img]
        selected_columns = row.columns[row.iloc[0] == True]
        caption = ', '.join(selected_columns)

        self.model.results[curr_img]['training_caption'] = caption

    def view_caption(self):
        if self.model is None or self.parent().current_item is None:
            return
        caption_window = CaptionWindow(self.parent(), readonly=True)
        caption_window.show()

    def edit_caption(self):
        if self.model is None or self.parent().current_item is None:
            return
        caption_window = CaptionWindow(self.parent(), readonly=False)
        caption_window.exec_()

    def state_changed(self, item):
        curr_img = self.parent().current_item.data()
        df = self.model.state

        row_idx = df.index[df['filename'] == curr_img].tolist()
        if row_idx:
            if item.checkState() == Qt.Checked:
                self.model.state.at[row_idx[0], item.text()] = True
            else:
                self.model.state.at[row_idx[0], item.text()] = False

        self.update_caption()


class AddTagDialog(QDialog):
    new_tags = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = parent.model
        self.curr_image = parent.current_item.data()

        self.setWindowTitle("Add Tags")

        main_layout = QVBoxLayout()

        self.text = QLabel(f"Adding Tags to: {self.curr_image}")

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
        """
        Add new tags to the DataFrame and update the relevant image row.
        :param text: Comma-separated string of new tags.
        """
        curr_img = self.curr_image

        tags = {tag.strip() for tag in text.split(",")}

        if len(tags) == 0:
            return

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

        self.new_tags.emit(tags)
        self.accept()
