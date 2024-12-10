from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class TableWidgetWithCompactButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table with Compact Buttons")
        self.resize(600, 400)

        # Create the table widget
        self.table = QTableWidget(self)
        self.table.setRowCount(5)  # Set the number of rows
        self.table.setColumnCount(3)  # Set the number of columns
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Action"])

        # Adjust column sizes
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0)  # Keep ID column resizable
        self.table.horizontalHeader().setSectionResizeMode(1)  # Keep Name column resizable
        self.table.setColumnWidth(2, 30)  # Set the action column width to just fit the button

        # Populate the table with data
        for row in range(5):
            self.table.setItem(row, 0, QTableWidgetItem(f"PO-{row + 1:06}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"Item {row + 1}"))

            # Create a small button with an icon
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with the path to your icon file
            btn.setIconSize(QSize(16, 16))  # Set the size of the icon
            btn.setFixedSize(24, 24)  # Set the button size
            btn.setStyleSheet("border: none;")  # Remove the button border for a sleek look
            btn.clicked.connect(lambda checked, r=row: self.handle_button_click(r))  # Pass row number to the handler

            # Add the button to the table
            self.table.setCellWidget(row, 2, btn)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def handle_button_click(self, row):
        print(f"Button clicked on row {row}")

if __name__ == "__main__":
    app = QApplication([])
    window = TableWidgetWithCompactButtons()
    window.show()
    app.exec()
