import json
import sys
from unittest import TestCase

from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog

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
        with open("test results.json", 'r') as infile:
            self.real_results = json.load(infile)

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

        submit_button = None
        for btn in self.window.center_widget.findChildren(QPushButton):
            if btn.toolTip() == "Predict tags for images":
                submit_button = btn

        self.assertIsNotNone(submit_button, "Submit button not found!")

        # Simulate interaction with the submit dialog
        submit_dialog_interaction()
        QTest.mouseClick(submit_button, Qt.LeftButton)
        self.wait_for_results()

        # Validate displayed images and tag processing
        self.verify_results()

        # Test adding a tag
        self._test_add_tags()

        self._test_check("test tag")

        self._test_view_caption()

        self._test_filter()

        self._test_edit_caption()

    def test_json_load(self):
        self.window.show()

        filename = "test results.json"
        try:
            with open(filename, 'r') as infile:
                results = json.load(infile)
        except Exception as e:
            self.fail(f"Unexpected exception raised: {str(e)}")

        self.window.center_widget.process_results(results)

        # Validate displayed images and tag processing
        self.verify_results()

        # Test adding a tag
        self._test_add_tags()

        self._test_check("test tag")

        self._test_view_caption()

        self._test_filter()

        self._test_edit_caption()

    # ---- Helper Methods ----

    def wait_for_results(self):
        """
        Connect the results signal to a slot that will stop the event loop.
        """

        def handle_results(results):
            self._check_results(results)
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
        self.compare_results(first_item.data(role=Qt.DisplayRole))

    def compare_results(self, image_name):
        """
        Compare tags from JSON file with the UI.
        """
        result = self.real_results[image_name]
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

    def _test_add_tags(self):
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

        # Check if the new items follow the expected convention: spacer, category, tags.
        checklist = self.window.center_widget.checklist
        items = [checklist.item(x).data(Qt.DisplayRole) for x in range(checklist.count())]

        length = len(items) - 1
        self.assertEqual(items[length - 3], None)
        self.assertEqual(items[length - 2], "User_tags")
        self.assertEqual(items[length - 1], "test tag")

        fname = self.window.center_widget.current_item.data(Qt.DisplayRole)
        self._verify_caption(fname, "test tag")

    def _verify_caption(self, filename, added_tag):
        """
        Checks if the added tag is added to the caption
        """
        caption = self.window.center_widget.model.results[filename]['training_caption']
        self.assertTrue(added_tag in caption, f"{added_tag} not found in {filename} caption")

    def _test_view_caption(self):
        """
        Test the 'view caption' functionality.
        Check if it shows up and check if it shows the current caption
        """
        filename = self.window.center_widget.current_item.data(Qt.DisplayRole)
        caption = self.window.center_widget.model.results[filename]['training_caption']

        checklist = self.window.center_widget.checklist
        checklist.view_caption()

        # Only use single shot for _exec
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.windowTitle() == "Caption":
                self.assertEqual(caption, widget.text_edit.toPlainText(),
                                 f"caption: {caption}, displayed: {widget.text_edit.toPlainText()}")
                self.assertTrue("test tag" in widget.text_edit.toPlainText(),
                                f"test tag not in caption, displayed: {widget.text_edit.toPlainText()}")
                QApplication.processEvents()
                break

    def _test_check(self, added_tag):
        """
        Test to see if checking and unchecking the item updates the caption
        """
        filename = self.window.center_widget.current_item.data(Qt.DisplayRole)
        checklist = self.window.center_widget.checklist

        # get item from checklist
        test_item = -1
        for i in range(checklist.count()):
            item = checklist.item(i)
            if added_tag == item.text():
                test_item = i
                break

        test_item = checklist.item(test_item)

        item_rect = checklist.visualItemRect(test_item)
        QTest.mouseClick(checklist.viewport(), Qt.LeftButton, pos=item_rect.center())  # select the item
        QTest.keyClick(checklist, Qt.Key_Space)  # uncheck the item
        QTest.qWait(100)  # allow ui to update

        self.assertEqual(test_item.checkState(), Qt.Unchecked, f"Item at index {test_item} still checked.")
        caption = self.window.center_widget.model.results[filename]['training_caption']

        self.assertFalse(added_tag in caption,
                         f"{added_tag} is still in caption after being unchecked {filename} caption \n {caption}")

        QTest.keyClick(checklist, Qt.Key_Space)  # recheck the item
        QTest.qWait(100)

        self.assertEqual(test_item.checkState(), Qt.Checked, f"Item at index {test_item} was not checked.")
        caption = self.window.center_widget.model.results[filename]['training_caption']  # Refresh the caption
        self.assertTrue(added_tag in caption,
                        f"{added_tag} is not in caption after being checked {filename} caption \n {caption}")

    def _test_edit_caption(self):
        """
        Test the 'Edit caption' functionality.
        Check if it shows up and check if it shows the current caption
        """
        image_gallery = self.window.center_widget.image_gallery
        first_item = image_gallery.model().index(0)
        rect = image_gallery.visualRect(first_item)
        QTest.mouseClick(image_gallery.viewport(), Qt.LeftButton, pos=rect.center())

        filename = self.window.center_widget.current_item.data(Qt.DisplayRole)
        caption = self.window.center_widget.model.results[filename]['training_caption']
        checklist = self.window.center_widget.checklist

        def dialog_interaction():
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.windowTitle() == "Edit Caption":
                    # check if test_tag is shown
                    self.assertEqual(caption, widget.text_edit.toPlainText(),
                                     f"caption: {caption}, displayed: {widget.text_edit.toPlainText()}")
                    self.assertTrue("test tag" in widget.text_edit.toPlainText(),
                                    f"test tag not in caption, displayed: {widget.text_edit.toPlainText()}")

                    # check if text can be changed
                    new_caption = caption.replace(", test tag", "")
                    widget.text_edit.setText(new_caption)
                    self.assertFalse("test tag" in widget.text_edit.toPlainText(),
                                     f"test tag still in caption, displayed: {widget.text_edit.toPlainText()}")
                    widget.accept()
                    QApplication.processEvents()

                    results_caption = self.window.center_widget.model.results[filename]['training_caption']
                    self.assertEqual(results_caption, new_caption, "caption is not updated")
                    break

        QTimer.singleShot(1000, dialog_interaction)
        checklist.edit_caption()

    def _test_filter(self):
        """
        testing the filter functionality.
        """

        filter_list = self.window.center_widget.filter_list
        gallery = self.window.center_widget.image_gallery
        searchbar = self.window.center_widget.searchbar

        searchbar.setText("test tag")
        QTest.keyPress(searchbar, Qt.Key_Return)

        self.assertEqual(gallery.model().rowCount(), 1)  # There should only be one item with that tag
        filename = gallery.model().index(0, 0).data(Qt.DisplayRole)
        caption = self.window.center_widget.model.results[filename]['training_caption']
        self.assertTrue("test tag" in caption,
                        f"test tag is not in caption of {filename} caption: \n {caption}")

        self.window.center_widget.clear_filter()
        self.assertEqual(gallery.model().rowCount(), 3)

        # multi tag check
        searchbar.setText("ship, cloudy sky")
        QTest.keyPress(searchbar, Qt.Key_Return)
        self.assertEqual(gallery.model().rowCount(), 2)  # There should be 2 items with that tag
        filename = gallery.model().index(0, 0).data(Qt.DisplayRole)
        caption = self.window.center_widget.model.results[filename]['training_caption']
        self.assertTrue("ship" in caption and "cloudy sky" in caption,
                        f"ship and cloudy sky is not in caption of {filename} caption: \n {caption}")

        # Click on "ship" and "cloudy sky" tags in filter_list for multi-tag check
        model = filter_list.model()
        for tag in ["ship", "cloudy sky"]:
            for i in range(model.rowCount()):
                index = model.index(i, 0)  # Get the index of the item
                if index.data(Qt.DisplayRole) == tag:  # If the item's text matches the tag
                    rect = filter_list.visualRect(index)
                    QTest.mouseClick(filter_list.viewport(), Qt.LeftButton, pos=rect.center())

                    self.assertEqual(gallery.model().rowCount(), 2,
                                     f"There should be 2 items with the {tag} tags.")
                    self.assertTrue(tag in caption,
                                    f"{tag} is not both in the caption of {filename}. Caption: \n{caption}")
                    break
        self.window.center_widget.clear_filter()

    def _check_results(self, results):
        # Convert results to a serializable format
        serializable_results = _tensor_to_json(results)

        self.assertEqual(serializable_results, self.real_results)


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
