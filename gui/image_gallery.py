import os

from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QDesktopServices, QFontMetrics
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListView, QStyledItemDelegate, QStyleOptionViewItem, QMenu, \
    QAction

from gui.caption import CaptionWindow


class ImageGallery(QListView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        delegate = ThumbnailDelegate()
        self.setItemDelegate(delegate)
        self.setViewMode(QListWidget.IconMode)
        self.setAcceptDrops(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # ctrl and shift click selection
        self.setIconSize(QSize(200, 200))
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(50)
        self.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize
        self.doubleClicked.connect(self.open_image)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def open_image(self, index):
        """
        Display Open image in image explorer
        :param index: index in the model, item holds file path and tag info
        """
        file_path = self.model().data(index, Qt.DisplayRole)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustSpacing()

    def adjustSpacing(self):
        """
        Evenly distributes the extra space at the end of the row to the margins of each item
        :return: None
        """
        icon_size = self.iconSize().width() + 10  # 10 is the min spacing between each item
        available_width = self.viewport().width() - 1  # Viewport will auto adjust if not - 1

        num_columns = max(1, available_width // icon_size)
        extra_space = available_width - (num_columns * icon_size)
        new_spacing = max(0, extra_space // (num_columns + 1))  # +1 for the space before the 1st item

        new_grid_size = QSize(icon_size + new_spacing, 225)  # evenly distribute extra space
        self.setGridSize(new_grid_size)

    def show_context_menu(self, position):
        menu = QMenu()

        select_all_action = QAction('Select All', self)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)

        deselect_all_action = QAction('Deselect All', self)
        deselect_all_action.triggered.connect(self.clearSelection)
        menu.addAction(deselect_all_action)

        remove_selection_action = QAction('Remove From Results', self)
        remove_selection_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_selection_action)

        menu.addSeparator()

        add_tag_action = QAction('Add Tag to Selected', self)
        add_tag_action.triggered.connect(self.add_tag)
        menu.addAction(add_tag_action)

        menu.addSeparator()

        view_caption_action = QAction('View Caption', self)
        view_caption_action.triggered.connect(self.view_caption)
        menu.addAction(view_caption_action)

        menu.exec_(self.mapToGlobal(position))

    def remove_selected(self):
        pass

    def add_tag(self):
        if self.model is None or self.parent().current_item is None:
            return
        # dialog = AddTagDialog(parent=self.parentWidget())
        # dialog.exec_()
        # self.parent().update_page(self.parent().current_item)
        pass

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


class ThumbnailDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying images, removes check box and names for better formatting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayRoleEnabled = True

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Remove checkbox area
        option.features &= ~QStyleOptionViewItem.HasCheckIndicator

        if self.displayRoleEnabled:
            # Truncate the display text to 200 pixels
            font_metrics = QFontMetrics(option.font)
            display_text = os.path.basename(index.data(Qt.DisplayRole))
            if display_text:
                option.text = font_metrics.elidedText(display_text, Qt.ElideRight, 200)

        # Center the icon vertically
        option.decorationSize = QSize(200, 200)
