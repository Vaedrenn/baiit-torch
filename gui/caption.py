from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDialogButtonBox


class CaptionWindow(QDialog):
    def __init__(self, parent=None, readonly=True):
        super().__init__(parent)
        self.model = parent.model
        self.filename = parent.current_item.data()
        self.setWindowTitle("Edit Caption")

        self.text_edit = QTextEdit()
        self.text_edit.setText(self.model.results[self.filename]['training_caption'])

        # whenever an item is changed in the main widget update the text
        self.parent().itemChanged.connect(self.change_text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        if readonly is True:
            self.setWindowTitle("Caption")
            self.text_edit.setReadOnly(True)
        else:
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)

            layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        self.model.results[self.filename]['training_caption'] = self.text_edit.toPlainText()
        super().accept()

    def change_text(self, item):
        filename = item.data()
        self.text_edit.setText(self.model.results[filename]['training_caption'])
