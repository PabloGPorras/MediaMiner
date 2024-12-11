from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QShortcut
from PyQt6.QtGui import QKeySequence


class MainWindow:
    def __init__(self):
        self.app = QApplication([])
        self.table = QTableWidget(10, 3)  # Create a table with 10 rows and 3 columns

        # Populate the table
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(f"Row {row + 1}, Col {col + 1}"))

        # Set selection behavior to select rows
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Add a shortcut for deselecting all rows
        self.deselect_all_shortcut = QShortcut(QKeySequence("Ctrl+D"), self.table)
        self.deselect_all_shortcut.activated.connect(self.deselect_all)

        # Show the table
        self.table.resize(600, 400)
        self.table.show()
        self.app.exec()

    def deselect_all(self):
        """Deselect all selected rows."""
        self.table.clearSelection()


if __name__ == "__main__":
    MainWindow()
