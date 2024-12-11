from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QDialog, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class CustomActionWidget(QDialog):
    def __init__(self, row):
        super().__init__()
        self.setWindowTitle("Actions")
        self.setFixedSize(200, 150)

        layout = QVBoxLayout()
        layout.addWidget(QPushButton(f"Receive Purchase Order (Row {row})", self))
        layout.addWidget(QPushButton(f"Create Purchase Order Return (Row {row})", self))
        layout.addWidget(QPushButton(f"View Tracking (Row {row})", self))
        self.setLayout(layout)

class TableWithCustomActions(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table with Action Buttons and Custom Widget")
        self.resize(600, 400)

        # Create the table widget
        self.table = QTableWidget(self)
        self.table.setRowCount(5)  # Set the number of rows
        self.table.setColumnCount(3)  # Set the number of columns
        self.table.setHorizontalHeaderLabels(["Action", "ID", "Name"])

        # Adjust column sizes
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0)
        self.table.setColumnWidth(0, 16)  # Set the Action column width to match the button size

        # Populate the table with data
        for row in range(5):
            # Create a small button with an icon
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with your icon
            btn.setIconSize(QSize(16, 16))  # Set the size of the icon
            btn.setFixedSize(16, 16)  # Match the button size to the icon size
            btn.setStyleSheet("border: none; padding: 0;")  # Compact button
            btn.clicked.connect(lambda checked, r=row: self.show_custom_widget(r))  # Pass row number to the handler

            # Add the button to the first column
            self.table.setCellWidget(row, 0, btn)

            # Populate the other columns
            self.table.setItem(row, 1, QTableWidgetItem(f"PO-{row + 1:06}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"Item {row + 1}"))

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def show_custom_widget(self, row):
        dialog = CustomActionWidget(row)
        dialog.exec()  # Show the dialog as a modal window

if __name__ == "__main__":
    app = QApplication([])
    window = TableWithCustomActions()
    window.show()
    app.exec()
