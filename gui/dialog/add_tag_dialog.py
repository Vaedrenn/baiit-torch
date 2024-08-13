from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

from gui.custom_components.multicompleter import MultiCompleter


class AddTagDialog(QDialog):
    new_tags = pyqtSignal(object)

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
