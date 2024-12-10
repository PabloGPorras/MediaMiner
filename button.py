from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class TableWidgetWithIconButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table with Icon Buttons")
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

            # Create a small button with an icon
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with the path to your icon file
            btn.setIconSize(QSize(16, 16))  # Set the size of the icon
            btn.setFixedSize(24, 24)  # Set the button size
            btn.setStyleSheet("border: none;")  # Remove the button border to make it sleek
            btn.clicked.connect(lambda checked, r=row: self.handle_button_click(r))  # Pass row number to the handler

            # Add the button to the table
            self.table.setCellWidget(row, 2, btn)

        # Resize the columns to fit the content
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(2, 30)  # Ensure the "Action" column is small enough for the button

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def handle_button_click(self, row):
        print(f"Button clicked on row {row}")

if __name__ == "__main__":
    app = QApplication([])
    window = TableWidgetWithIconButtons()
    window.show()
    app.exec()
