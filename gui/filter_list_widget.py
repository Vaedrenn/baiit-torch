from PyQt5.QtCore import Qt, pyqtSignal, QItemSelectionModel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListView, QAbstractItemView

TAG = Qt.UserRole + 1


class FilterList(QListView):
    itemClicked = pyqtSignal(str)  # Define the custom signal

    def __init__(self):
        super(QListView, self).__init__()
        self.selected_items = set()

        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.clicked.connect(self.on_item_clicked)  # Connect the clicked signal to a slot
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

    def on_item_clicked(self, index):
        """
        When item is clicked add/remove item to selected items and emit the item.
        """
        tag = self.model().data(index, TAG)
        if tag in self.selected_items:
            self.selected_items.remove(tag)
        else:
            self.selected_items.add(tag)
        self.itemClicked.emit(tag)  # Emit the custom signal with the item text

        # Update the selection state of all items in the model based on the selected_items list.
        for row in range(self.model().rowCount()):
            index = self.model().index(row)
            tag = self.model().data(index, TAG)
            if tag in self.selected_items:
                self.selectionModel().select(index, QItemSelectionModel.Select)
            else:
                self.selectionModel().select(index, QItemSelectionModel.Deselect)
