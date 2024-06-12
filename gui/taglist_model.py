from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractListModel, pyqtSignal, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListView, QAbstractItemView, QStyledItemDelegate

from gui.gallery_model import ImageGalleryTableModel


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
        if role == Qt.UserRole+1:
            print(f"row: {index.row()}")
            print(f"len of filtered tags: {len(self.filtered_tags)}")
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


class TagList(QListView):
    itemClicked = pyqtSignal(str)  # Define the custom signal

    def __init__(self):
        super(QListView, self).__init__()
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.clicked.connect(self.on_item_clicked)  # Connect the clicked signal to a slot
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)


    def on_item_clicked(self, index):
        tag = self.model().data(index, (Qt.UserRole+1))
        print(tag)
        self.itemClicked.emit(tag)  # Emit the custom signal with the item text
