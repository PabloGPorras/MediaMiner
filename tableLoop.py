from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout
        layout = QVBoxLayout(self)

        # Create a QTableWidget
        self.table = QTableWidget(5, 3)  # 5 rows, 3 columns
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)  # Select entire rows
        layout.addWidget(self.table)

        # Populate the table with some data
        for row in range(5):
            for col in range(3):
                self.table.setItem(row, col, QTableWidgetItem(f"Row {row+1}, Col {col+1}"))

        # Add a button to process selected rows
        button = QPushButton("Process Selected Rows")
        button.clicked.connect(self.process_selected_rows)
        layout.addWidget(button)

    def process_selected_rows(self):
        """Process all selected rows."""
        selected_rows = set()
        for item in self.table.selectedItems():  # Get all selected items
            selected_rows.add(item.row())  # Collect unique row numbers

        # Loop over the selected rows
        for row in selected_rows:
            print(f"Processing Row {row + 1}")
            # Access data for each column in the selected row
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    print(f"Row {row + 1}, Col {col + 1}: {item.text()}")


if __name__ == "__main__":
    app = QApplication([])

    # Create and show the main widget
    window = MyWidget()
    window.show()

    app.exec()
