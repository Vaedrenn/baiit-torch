from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QVariant

from gui.filter_list_widget import TAG
from gui.model.gallery_model import ImageGalleryTableModel


class FilterListModel(QAbstractListModel):

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
