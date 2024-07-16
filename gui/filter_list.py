from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractListModel, pyqtSignal, QSize, QItemSelectionModel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListView, QAbstractItemView, QStyledItemDelegate

from gui.gallery_model import ImageGalleryTableModel

TAG = Qt.UserRole+1
class TagListModel(QAbstractListModel):

    def __init__(self, model: ImageGalleryTableModel):
        super().__init__()
        self.other_model = model
        self.other_model.layoutChanged.connect(self.filter)
        self.filtered_tags = None

    def rowCount(self, parent=QModelIndex()):
        if self.filtered_tags is not None:
            return len(self.filtered_tags)
        else:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            tag, count = self.filtered_tags[index.row()]
            formatted_tag = f"{count:>5}  {tag}"
            return formatted_tag
        if role == TAG:
            tag, count = self.filtered_tags[index.row()]
            return tag
        return QVariant()

    def filter(self):
        tag_counts = self.other_model.filtered_state.drop(columns=['filename']).sum()
        tag_counts = tag_counts.sort_values(ascending=False)
        tag_counts = tag_counts[tag_counts >= 1]
        tag_counts = tag_counts.to_dict()
        self.filtered_tags = list(tag_counts.items())
        self.layoutChanged.emit()

    def default(self):
        tag_counts = self.other_model.state.drop(columns=['filename']).sum()
        tag_counts = tag_counts.sort_values(ascending=False)
        tag_counts = tag_counts.to_dict()
        self.filtered_tags = list(tag_counts.items())
        self.layoutChanged.emit()

class TagList(QListView):
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
        tag = self.model().data(index, TAG)
        if tag in self.selected_items:
            self.selected_items.remove(tag)
        else:
            self.selected_items.add(tag)
        self.itemClicked.emit(tag)  # Emit the custom signal with the item text

        for row in range(self.model().rowCount()):
            index = self.model().index(row)
            tag = self.model().data(index, TAG)
            if tag in self.selected_items:
                self.selectionModel().select(index, QItemSelectionModel.Select)
            else:
                self.selectionModel().select(index, QItemSelectionModel.Deselect)
