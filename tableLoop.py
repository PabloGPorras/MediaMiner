from PyQt6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QPushButton, QStandardItemModel, QStandardItem


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout
        layout = QVBoxLayout(self)

        # Create a QTableView and model
        self.table = QTableView()
        self.model = QStandardItemModel(5, 3)  # 5 rows, 3 columns
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        # Populate the model with some data
        for row in range(5):
            for col in range(3):
                self.model.setItem(row, col, QStandardItem(f"Row {row+1}, Col {col+1}"))

        # Add a button to process selected rows
        button = QPushButton("Process Selected Rows")
        button.clicked.connect(self.process_selected_rows)
        layout.addWidget(button)

    def process_selected_rows(self):
        """Process all selected rows."""
        selected_rows = set()
        for index in self.table.selectionModel().selectedIndexes():  # Get all selected indexes
            selected_rows.add(index.row())  # Collect unique row numbers

        # Loop over the selected rows
        for row in selected_rows:
            print(f"Processing Row {row + 1}")
            # Access data for each column in the selected row
            for col in range(self.model.columnCount()):
                item = self.model.item(row, col)
                if item:
                    print(f"Row {row + 1}, Col {col + 1}: {item.text()}")


if __name__ == "__main__":
    app = QApplication([])

    # Create and show the main widget
    window = MyWidget()
    window.show()

    app.exec()
