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
    """Process all selected rows and extract the value in the 'unique_ref' column."""
    selected_rows = set()
    unique_ref_column = 1  # Replace with the actual column index of 'unique_ref'

    # Collect unique selected rows
    for item in self.table.selectedItems():
        selected_rows.add(item.row())

    # Process each selected row
    for row in selected_rows:
        unique_ref_item = self.table.item(row, unique_ref_column)
        if unique_ref_item:  # Check if the item exists
            unique_ref_value = unique_ref_item.text()
            print(f"Row {row + 1}, Unique Ref: {unique_ref_value}")



if __name__ == "__main__":
    app = QApplication([])

    # Create and show the main widget
    window = MyWidget()
    window.show()

    app.exec()
