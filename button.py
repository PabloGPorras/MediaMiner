from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class TableWidgetWithSmallActionColumn(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table with Small Action Column")
        self.resize(600, 400)

        # Create the table widget
        self.table = QTableWidget(self)
        self.table.setRowCount(5)  # Set the number of rows
        self.table.setColumnCount(3)  # Set the number of columns
        self.table.setHorizontalHeaderLabels(["Action", "ID", "Name"])

        # Adjust column sizes
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0)  # Fix Action column
        self.table.setColumnWidth(0, 16)  # Set the Action column width to match the icon size

        # Populate the table with data
        for row in range(5):
            # Create a small button with an icon
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with the path to your icon file
            btn.setIconSize(QSize(16, 16))  # Set the size of the icon
            btn.setFixedSize(16, 16)  # Match the button size to the icon size
            btn.setStyleSheet("border: none; padding: 0;")  # Remove border and padding to make it compact
            btn.clicked.connect(lambda checked, r=row: self.handle_button_click(r))  # Pass row number to the handler

            # Add the button to the first column
            self.table.setCellWidget(row, 0, btn)

            # Populate the other columns
            self.table.setItem(row, 1, QTableWidgetItem(f"PO-{row + 1:06}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"Item {row + 1}"))

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def handle_button_click(self, row):
        print(f"Button clicked on row {row}")

if __name__ == "__main__":
    app = QApplication([])
    window = TableWidgetWithSmallActionColumn()
    window.show()
    app.exec()
