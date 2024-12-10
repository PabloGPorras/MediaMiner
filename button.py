from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget

class TableWidgetExample(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Table with Buttons")
        self.resize(600, 400)
        
        # Create the table widget
        self.table = QTableWidget(self)
        self.table.setRowCount(5)  # Set the number of rows
        self.table.setColumnCount(3)  # Set the number of columns
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Action"])

        # Populate the table with data
        for row in range(5):
            self.table.setItem(row, 0, QTableWidgetItem(f"PO-{row + 1:06}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"Item {row + 1}"))

            # Create a button for each row
            btn = QPushButton("Edit")
            btn.clicked.connect(lambda checked, r=row: self.handle_button_click(r))  # Pass row number to the handler
            self.table.setCellWidget(row, 2, btn)
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def handle_button_click(self, row):
        print(f"Button clicked on row {row}")

if __name__ == "__main__":
    app = QApplication([])
    window = TableWidgetExample()
    window.show()
    app.exec()
