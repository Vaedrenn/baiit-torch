import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
from unittest import TestCase
from gui.center_widget import MainWindow


class TestMainWindow(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()
        self.app.quit()

    def test_submit_button_click(self):
        """
        Test if the submit dialog shows up
        """
        categories = self.window.center_widget.categories
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
                    widget.reject()  # Use accept() to close the dialog
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
        category = 'rating'
        new_value = 90  # New threshold value
        dialog.spinboxes[category].setValue(new_value)
        self.assertEqual(thresholds[category], new_value / 100.0,
                         f"{category} threshold was not updated correctly.")

        new_value = 50  # change it back
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


if __name__ == "__main__":
    import unittest

    unittest.main()
