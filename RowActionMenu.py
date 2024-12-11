from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt


class RowActionMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Row Action Menu")
        self.setLayout(QVBoxLayout())

        # Example buttons in the menu
        self.rejectButton = QPushButton("Reject Request", self)
        self.rejectButton.clicked.connect(self.reject_request)
        self.viewButton = QPushButton("View Request", self)
        self.viewButton.clicked.connect(self.view_request)

        # Add buttons to layout
        self.layout().addWidget(self.rejectButton)
        self.layout().addWidget(self.viewButton)

    def update_buttons_state(self, selected_count):
        """Enable or disable buttons based on the number of selected rows."""
        if selected_count > 1:
            # Disable buttons that should not work with multiple rows
            self.rejectButton.setEnabled(False)
            self.viewButton.setEnabled(False)
        else:
            # Enable buttons for single selection
            self.rejectButton.setEnabled(True)
            self.viewButton.setEnabled(True)

    def reject_request(self):
        print("Reject request logic goes here.")

    def view_request(self):
        print("View request logic goes here.")


class MainWindow(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Create a sample table widget
        self.table = QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Populate the table
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(f"Row {row + 1}, Col {col + 1}"))

        # Connect selection changes to button update logic
        self.table.selectionModel().selectionChanged.connect(self.update_row_action_menu)

        # Show the table
        self.table.resize(600, 400)
        self.table.show()

        # Create the RowActionMenu
        self.row_action_menu = RowActionMenu()

    def update_row_action_menu(self):
        """Update the RowActionMenu based on the current table selection."""
        selected_rows = len(self.table.selectionModel().selectedRows())
        self.row_action_menu.update_buttons_state(selected_rows)


if __name__ == "__main__":
    import sys

    app = MainWindow(sys.argv)
    sys.exit(app.exec())
