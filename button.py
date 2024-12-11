from PyQt6.QtWidgets import QTableWidget, QPushButton, QTableWidgetItem, QDialog, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QHeaderView


def loadDataObjects(table, objectArray: list, columnNameFilter: list = None, rowAction=None) -> None:
    # Grabbing the columns names
    firstObject = objectArray[0]
    columnNames = [column.name for column in firstObject.__table__.columns if column.name not in columnNameFilter]

    table.setRowCount(len(objectArray))
    table.setColumnCount(len(columnNames) + (1 if rowAction else 0))  # Add an extra column for the action if needed

    # Setting the header labels
    headerLabels = [""] if rowAction else []  # Add a blank header for the action column
    headerLabels += [str(column) for column in columnNames]
    table.setHorizontalHeaderLabels(headerLabels)

    if rowAction:
        # Adjust column sizes
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Fix Action column
        table.setColumnWidth(0, 16)  # Set the Action column width to match the button size

    # Populate row data
    for row, obj in enumerate(objectArray):
        if rowAction:
            # Create a small button with an icon
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with your icon file
            btn.setIconSize(QSize(16, 16))  # Set the size of the icon
            btn.setFixedSize(16, 16)  # Match the button size to the icon size
            btn.setStyleSheet("border: none; padding: 0;")  # Compact button
            btn.clicked.connect(lambda checked, r=row: show_custom_widget(rowAction, r))  # Pass row number to the handler

            # Add the button to the first column
            table.setCellWidget(row, 0, btn)

        # Populate other columns
        for col, columnName in enumerate(columnNames):
            if columnName not in columnNameFilter:
                item = QTableWidgetItem(str(getattr(obj, columnName)))
                table.setItem(row, col + (1 if rowAction else 0), item)  # Offset by 1 if rowAction is enabled


def show_custom_widget(rowAction, row):
    dialog = rowAction(row)
    dialog.exec()  # Show the dialog as a modal window


# Example of a custom dialog
class CustomActionWidget(QDialog):
    def __init__(self, row):
        super().__init__()
        self.setWindowTitle(f"Actions for Row {row}")
        self.setFixedSize(200, 150)

        layout = QVBoxLayout()
        layout.addWidget(QPushButton(f"Receive Purchase Order (Row {row})", self))
        layout.addWidget(QPushButton(f"Create Purchase Order Return (Row {row})", self))
        layout.addWidget(QPushButton(f"View Tracking (Row {row})", self))
        self.setLayout(layout)
