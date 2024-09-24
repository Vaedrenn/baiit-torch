import json
import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QMenu
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer, QEventLoop, QPoint
from unittest import TestCase
from gui.center_widget import MainWindow


def find_dialog(title):
    """
    Find the dialog by its window title.
    """
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QDialog) and widget.windowTitle() == title:
            return widget
    return None


def submit_dialog_interaction():
    """
    Set up a QTimer to simulate user interaction with the dialog.
    """

    def interaction():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.windowTitle() == "Set Thresholds":
                widget.model_input.setText(r"wd-vit-tagger-v3")
                widget.dir_input.setText(r"images")
                widget.confirm_button.click()
                break

    QTimer.singleShot(1000, interaction)


def flag_check(item):
    """
    Check if both Qt.ItemIsSelectable and Qt.ItemIsUserCheckable flags are set.
    """
    return (item.flags() & Qt.ItemIsSelectable) and (item.flags() & Qt.ItemIsUserCheckable)


class TestMainWindow(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.event_loop = QEventLoop()

    def tearDown(self):
        self.window.close()
        self.app.quit()

    def test_submit_button_click(self):
        """
        Test if the submit dialog shows up
        """
        thresholds = self.window.center_widget.threshold

        # Find the submit button in the navigation bar
        submit_button = None
        for btn in self.window.center_widget.findChildren(QPushButton):
            if btn.toolTip() == "Predict tags for images":
                submit_button = btn
                break

        # Assert that the submit button was found
        self.assertIsNotNone(submit_button, "Submit button not found!")

        # Set up a QTimer to close the dialog after it opens
        def close_dialog():
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.windowTitle() == "Set Thresholds":
                    widget.cancel_button.click()  # Use accept() to close the dialog
                    break

        QTimer.singleShot(1000, close_dialog)  # Close dialog after 1 second

        # Simulate a button click
        QTest.mouseClick(submit_button, Qt.LeftButton)

        dialog = None

        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.windowTitle() == "Set Thresholds":
                dialog = widget

        # Check if the dialog initializes with the correct values
        for category, value in thresholds.items():
            spinbox = dialog.spinboxes[category]
            self.assertEqual(spinbox.value(), int(value * 100), f"{category} spinbox did not initialize correctly.")

        # Test if changing thresholds works
        category = 'characters'
        new_value = 90  # New threshold value
        dialog.spinboxes[category].setValue(new_value)
        self.assertEqual(thresholds[category], new_value / 100.0,
                         f"{category} threshold was not updated correctly.")

        new_value = 70  # change it back
        dialog.spinboxes[category].setValue(new_value)
        self.assertEqual(thresholds[category], new_value / 100.0,
                         f"{category} threshold was not updated correctly.")

        # Test changing the inputs
        dialog.model_input.setText("wd-vit-tagger-v3")
        self.assertEqual(dialog.model_input.text(), "wd-vit-tagger-v3")

        dialog.dir_input.setText("images")
        self.assertEqual(dialog.dir_input.text(), "images")

        # Since the dialog is modal and blocks, the test will only continue after the dialog is closed
        # Add an assertion to verify the dialog was successfully closed
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.windowTitle() == "Set Thresholds":
                self.assertFalse(widget.isVisible(), "ThresholdDialog is still visible!")

    def test_submit_results(self):
        """
        Main test to handle the overall flow: submit, interaction, and result verification.
        """
        self.window.show()

        submit_button = self.find_submit_button()
        self.assertIsNotNone(submit_button, "Submit button not found!")

        # Simulate interaction with the submit dialog
        submit_dialog_interaction()
        QTest.mouseClick(submit_button, Qt.LeftButton)
        self.wait_for_results()

        # Validate displayed images and tag processing
        self.verify_results()

        # Test adding a caption
        self.test_add_tags()

        # Test if new items follow convention
        self.check_tag_convention()

        # Placeholder for other tests: view, edit caption, and filters
        self.test_view_caption()
        self.test_edit_caption()
        self.test_filter()

    # ---- Helper Methods ----

    def find_submit_button(self):
        """
        Find the submit button in the navigation bar.
        """
        for btn in self.window.center_widget.findChildren(QPushButton):
            if btn.toolTip() == "Predict tags for images":
                return btn
        return None

    def wait_for_results(self):
        """
        Connect the results signal to a slot that will stop the event loop.
        """

        def handle_results(results):
            self.check_results(results)
            self.event_loop.quit()

        dialog = find_dialog("Set Thresholds")
        dialog.results.connect(handle_results)
        self.event_loop.exec_()

    def verify_results(self):
        """
        Verify if images are displayed in the gallery.
        """
        image_gallery = self.window.center_widget.image_gallery
        self.assertGreater(image_gallery.model().rowCount(), 0, "No images are displayed in the gallery!")

        first_item = image_gallery.model().index(0)
        rect = image_gallery.visualRect(first_item)
        QTest.mouseClick(image_gallery.viewport(), Qt.LeftButton, pos=rect.center())
        self.compare_data(first_item.data(role=Qt.DisplayRole))

    def compare_data(self, image_name):
        """
        Compare tags from JSON file with the UI.
        """
        with open("test results.json", 'r') as infile:
            real_results = json.load(infile)

        result = real_results[image_name]
        test_tags = result['training_caption'].split(", ")

        # Check JSON data against data displayed in checklist
        checklist = self.window.center_widget.checklist
        items = [checklist.item(x) for x in range(checklist.count())]
        tags = [i.data(Qt.DisplayRole) for i in items if flag_check(i)]
        categories = [i.data(Qt.DisplayRole) for i in items if not flag_check(i)]

        self.assertEqual(len(test_tags), len(tags), "Tag counts don't line up")

        for t in test_tags:
            self.assertIn(t, tags, f"{t} is not found in test_tags: {test_tags}")

        for t in tags:
            self.assertIn(t, test_tags, f"{t} is not found in tags: {tags}")

        self.verify_categories(categories)

    def verify_categories(self, categories):
        """
        Check if tag is being displayed as a category.
        """
        widget_categories = self.window.center_widget.categories
        for category in categories:
            if category and category != "None":
                self.assertIn(str(category).lower(), widget_categories,
                              f"Tag {category.lower()} shouldn't be in categories")

    def test_add_tags(self):
        """
        Test the functionality to add a tag.
        """

        def dialog_interaction():
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.windowTitle() == "Add Tags":
                    widget.lineedit.setText("test tag")
                    self.assertEqual(widget.lineedit.text(), "test tag", "Line edit did not contain expected text")
                    QTest.mouseClick(widget.add_button, Qt.LeftButton)
                    QApplication.processEvents()
                    break

        QTimer.singleShot(500, dialog_interaction)  # Needed to interact with dialogs
        checklist = self.window.center_widget.checklist
        checklist.add_tag()

        items = [checklist.item(x).data(Qt.DisplayRole) for x in range(checklist.count())]
        self.assertIn("test tag", items)

    def check_tag_convention(self):
        """
        Check if the new items follow the expected convention: spacer, category, tags.
        """
        checklist = self.window.center_widget.checklist
        items = [checklist.item(x).data(Qt.DisplayRole) for x in range(checklist.count())]

        length = len(items) - 1
        self.assertEqual(items[length - 3], None)
        self.assertEqual(items[length - 2], "User_tags")
        self.assertEqual(items[length - 1], "test tag")

    def test_view_caption(self):
        """
        Placeholder for testing the 'view caption' functionality.
        """
        pass

    def test_edit_caption(self):
        """
        Placeholder for testing the 'edit caption' functionality.
        """
        pass

    def test_filter(self):
        """
        Placeholder for testing the filter functionality.
        """
        pass

    def check_results(self, results):
        # Convert results to a serializable format
        serializable_results = _tensor_to_json(results)

        with open("test results.json", 'r') as infile:
            real_results = json.load(infile)
            self.assertEqual(serializable_results, real_results)


def _tensor_to_json(obj):
    from torch import Tensor
    if isinstance(obj, Tensor):
        return obj.tolist()  # Convert tensor to list
    elif isinstance(obj, dict):
        return {k: _tensor_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_tensor_to_json(i) for i in obj]
    else:
        return obj


if __name__ == "__main__":
    import unittest

    unittest.main()
