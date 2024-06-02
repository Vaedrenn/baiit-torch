import json
import os
import shutil
import sys

from PyQt5.QtCore import QSize, QRegularExpression, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, \
    QLineEdit, QCompleter, QTextEdit, QStyleFactory, QMainWindow, QListWidget, \
    QListWidgetItem, QMessageBox, QFileDialog, QStyledItemDelegate

import io

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import ImageFileDirectory_v2

from gui.categories import TagDisplayWidget
from gui.dark_palette import create_dark_palette
from gui.gallery_model import ImageGalleryTableModel
from gui.image_gallery import ImageGallery


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setPalette(create_dark_palette())
        self.center_widget = CentralWidget()
        self.setCentralWidget(self.center_widget)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.threshold = {"rating": 0.0, "characters": 0.7, "general": 0.35}  # load from settings
        self.categories = {"rating": 9, "characters": 4, "general": 0}  # load from settings
        self.model = None
        self.model_folder = None  # cache
        self.proxy_model = QSortFilterProxyModel()

        self.searchbar = QLineEdit()
        self.filter_completer = QCompleter()
        self.clear_btn = QPushButton()
        self.tag_list = QListWidget()
        self.caption = QTextEdit()

        self.image_gallery = ImageGallery()
        self.tag_display = TagDisplayWidget(thresholds=self.categories)

        self.initUI()

    def initUI(self):
        self.setLayout(QHBoxLayout())
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setPalette(create_dark_palette())

        # Frame 1  tag search and filter, caption
        filter_widget = QWidget()
        filter_widget.setLayout(QVBoxLayout())
        filter_widget.layout().setContentsMargins(0, 0, 0, 0)
        filter_widget.setMaximumWidth(300)

        search_box = QHBoxLayout()
        self.searchbar.setPlaceholderText("  Filter Tags")
        self.searchbar.returnPressed.connect(lambda: self.filter_images(self.searchbar.text()))
        self.clear_btn = QPushButton("Clear Filter")
        self.clear_btn.clicked.connect(self.clear_filter)

        search_box.addWidget(self.searchbar)
        search_box.addWidget(self.clear_btn)

        self.tag_list.setSelectionMode(QListWidget.MultiSelection)  # Toggle style selection
        self.tag_list.itemClicked.connect(lambda: self.filter_images(self.searchbar.text()))  # on click filter
        tag_delegate = TagListItemDelegate()
        self.tag_list.setItemDelegate(tag_delegate)

        self.caption.setReadOnly(True)
        self.caption.setMaximumHeight(200)

        filter_widget.layout().addLayout(search_box)
        filter_widget.layout().addWidget(self.tag_list)
        # filter_widget.layout().addWidget(self.caption)

        # Frame 2   image gallery
        self.image_gallery.clicked.connect(self.update_page)  # on click change image

        # Frame 3   tag display, shows all tags related to image separated into their respective categories
        self.tag_display.setMaximumWidth(300)
        self.tag_display.layout().setContentsMargins(0, 0, 0, 0)

        # Navbar
        navbar = QWidget()
        navbar.setLayout(QVBoxLayout())
        navbar.setMaximumWidth(40)
        navbar.layout().setContentsMargins(0, 0, 0, 0)
        navbar.layout().setSpacing(5)
        self.add_buttons_to_navbar(navbar)

        # Wrapup
        self.layout().addWidget(navbar)
        self.layout().addWidget(filter_widget)
        self.layout().addWidget(self.image_gallery)
        self.layout().addWidget(self.tag_display)

    def add_buttons_to_navbar(self, navbar):
        buttons_info = [
            ("Predict tags for images", "gui/ICONS/play.png", self.submit),
            ("Write tags to file", "gui/ICONS/WRITE.png", self.write_tags),
            ("Export tags", "gui/ICONS/EXPORT.png", self.export_tags),
            ("Move images to folder", "gui/ICONS/MOVE.png", self.move_images),
            ("", "gui/ICONS/GALLERY.png", self.move_images),  # Connect when needed
            ("Settings", "gui/ICONS/SETTINGS.png", self.settings)
        ]

        for tooltip, icon_path, callback in buttons_info:
            btn = QPushButton()
            btn.setIconSize(QSize(30, 30))
            btn.setIcon(QIcon(icon_path))
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            if tooltip == "Settings":
                navbar.layout().addStretch()
            navbar.layout().addWidget(btn)

    def submit(self):
        from gui.submit_dialog import ThresholdDialog
        dialog = ThresholdDialog(parent=self)
        dialog.results.connect(lambda x: self.process_results(x))
        dialog.exec_()
        # results = self.import_tags("results.json")
        # self.process_results(results)

    def process_results(self, data: dict):
        if data is None:
            return
        if hasattr(self, 'model') and self.model is not None:
            self.model.deleteLater()  # Delete the old model to free up memory
            self.model = None  # Immediately set it to None to avoid issues

        # Create and assign model
        self.model = ImageGalleryTableModel(data)
        self.proxy_model.setSourceModel(self.model)
        self.image_gallery.setModel(self.proxy_model)

        # Add tags to filter list
        self.tag_list.clear()
        for tag, count in sorted(self.model.tags.items(), key=lambda item: item[1], reverse=True):
            formatted_tag = f"{count:>4}  {tag}"
            self.tag_list.addItem(QListWidgetItem(formatted_tag))

        # Assign Completer
        self.search_completer = MultiCompleter(self.model.tags.keys())
        self.searchbar.setCompleter(self.search_completer)

    def filter_images(self, text=None):
        # Get all tags and remove (number)
        selected_tags = [
            item.text().split(maxsplit=1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]
        if not selected_tags and text is None:
            # Clear filter if no tags are selected
            self.proxy_model.setFilterRegularExpression(QRegularExpression())
            return
        if text != "" and text is not None:
            tags = [tag.strip() for tag in text.split(",")]
            selected_tags.extend(tags)

        regex_pattern = "(?=.*{})".format(")(?=.*".join(selected_tags))  # Regex for selecting things with all tags

        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(
            Qt.UserRole)  # Filter by UserRole, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def clear_filter(self):
        """
        clears filters
        """
        self.tag_list.clearSelection()
        self.searchbar.clear()
        # Create QRegularExpression object
        regex = QRegularExpression('', QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(
            Qt.UserRole)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def update_page(self, item):
        filename = item.data()
        for category in self.categories.keys():
            tags = self.model.get_tags(filename, category)
            self.update_tags(category, tags, True)
            self.update_caption(item)

    def update_tags(self, category, tags, tag_state):
        """ Refreshes the tags in the given checklist"""
        if tags is None:
            return
        widget = self.tag_display.get(category)
        widget.add_dict(tags, tag_state)

    def update_caption(self, item):
        self.caption.setText(item.data(role=Qt.UserRole))

    def write_tags(self):
        """
        Write tags to image's exif
        :return: True if successful, False if labels or model is missing
        """
        if not self.model:
            return False

        # Placeholder method for writing tags to file
        print("Write tags action triggered")
        selected_rows = self.image_gallery.selectedIndexes()
        for row in selected_rows:
            filepath = self.model.data(row)
            text = self.model.data(row, role=Qt.UserRole)

            with Image.open(filepath) as img:
                ifd = ImageFileDirectory_v2()
                exif_stream = io.BytesIO()
                _TAGS = dict(((v, k) for k, v in TAGS.items()))  # enumerate possible exif tags
                ifd[_TAGS["ImageDescription"]] = text
                ifd.save(exif_stream)
                hex = b"Exif\x00\x00" + exif_stream.getvalue()

                img.save(filepath, exif=hex)

    def import_tags(self, filename=None):
        options = QFileDialog.Options()
        if filename is None:
            filename, _ = QFileDialog.getOpenFileName(None, "Import Tags", "", "JSON Files (*.json);;All Files (*)",
                                                      options=options)
        if filename:
            try:
                with open(filename, 'r') as infile:
                    results = json.load(infile)
                # QMessageBox.information(None, "Import Successful", f"Tags imported from {filename}")
                return results
            except Exception as e:
                QMessageBox.critical(None, "Import Failed", f"An error occurred: {str(e)}")
                return None

    def _tensor_to_json(self, obj):
        from torch import Tensor
        if isinstance(obj, Tensor):
            return obj.tolist()  # Convert tensor to list
        elif isinstance(obj, dict):
            return {k: self._tensor_to_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._tensor_to_json(i) for i in obj]
        else:
            return obj

    def export_tags(self):
        options = QFileDialog.Options()
        output_file, _ = QFileDialog.getSaveFileName(None, "Export Tags", "", "JSON Files (*.json);;All Files (*)",
                                                     options=options)
        if output_file:
            try:
                # Convert results to a serializable format
                serializable_results = self._tensor_to_json(self.model.results)
                with open(output_file, 'w') as outfile:
                    json.dump(serializable_results, outfile, indent=4)
                QMessageBox.information(None, "Export Successful", f"Tags exported to {output_file}")
            except Exception as e:
                QMessageBox.critical(None, "Export Failed", f"An error occurred: {str(e)}")

    def move_images(self):
        selected_rows = self.image_gallery.selectedIndexes()
        num_files = len(selected_rows)
        if num_files == 0:
            return
        target_dir = QFileDialog.getExistingDirectory(None, "Select Target Directory")
        if target_dir == '':
            return

        # Create the target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        confirmation = QMessageBox.question(
            None,
            "Confirm Move",
            f"Do you want to move {num_files} files to {target_dir}?",
            QMessageBox.Ok | QMessageBox.Cancel
        )

        if confirmation != QMessageBox.Ok:
            return

        # Move each file to the target directory
        for f in selected_rows:
            file_path = f.data()
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(target_dir, file_name)
            shutil.move(file_path, destination_path)

            # update model info after moving, idk if I should remove this option
            self.model.results[destination_path] = self.model.results.pop(file_path)
            self.model.icons[destination_path] = self.model.icons.pop(file_path)
            index = self.model.filenames.index(file_path)
            self.model.filenames[index] = destination_path

        # Deselect all selected rows
        self.image_gallery.clearSelection()
        QMessageBox.information(None, "Move Completed", f"Moved {num_files} files to {target_dir}")

    def settings(self):
        # Placeholder method for settings
        print("Settings action triggered")


class MultiCompleter(QCompleter):
    """ Multi Tag completer, allows for comma separated tag searching"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setMaxVisibleItems(5)

    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)

        lst = str(self.widget().text()).split(', ')
        if len(lst) > 1:
            path = ', '.join(lst[:-1]) + ', ' + path

        return path

    def splitPath(self, path):
        return [path.split(',')[-1].strip()]


class TagListItemDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying larger item with larger text"""

    def sizeHint(self, option, index):
        # Customize the size of items
        return QSize(100, 25)  # Adjust the width and height as needed

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Customize the font size of the item text
        option.font.setPointSize(12)  # Adjust the font size as needed

if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QMainWindow using QWidget as central widget
    window = CentralWidget()
    window.resize(1200, 800)
    window.show()

    # Execute application
    sys.exit(app.exec())
