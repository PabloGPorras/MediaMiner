from PyQt6.QtWidgets import QTableWidget, QPushButton, QTableWidgetItem, QDialog, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QHeaderView


def loadDataObjects(table, objectArray: list, columnNameFilter: list = None, rowAction=None) -> None:
    # Grab the column names
    firstObject = objectArray[0]
    columnNames = [column.name for column in firstObject.__table__.columns if column.name not in columnNameFilter]

    # Set up the table dimensions
    table.setRowCount(len(objectArray))
    table.setColumnCount(len(columnNames) + (1 if rowAction else 0))  # Add one column for the action button

    # Set the header labels (prepend an empty header for the action button)
    headerLabels = [""] if rowAction else []  # Blank header for the action column
    headerLabels += [str(column) for column in columnNames]
    table.setHorizontalHeaderLabels(headerLabels)

    if rowAction:
        # Adjust the size of the action button column
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Fix Action column
        table.setColumnWidth(0, 50)  # Adjust width as desired

    # Populate the rows
    for row, obj in enumerate(objectArray):
        if rowAction:
            # Create the action button
            btn = QPushButton()
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with your icon file
            btn.setIconSize(QSize(16, 16))  # Set the icon size
            btn.setStyleSheet("border: none; padding: 0;")  # Compact style
            
            # Set the button to expand and fill the cell
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            btn.clicked.connect(lambda checked, r=row: show_custom_widget(rowAction, r))  # Pass row number to handler

            # Add the button to the first column
            table.setCellWidget(row, 0, btn)

        # Populate the rest of the columns (shift by 1 because the action button occupies the first column)
        for col, columnName in enumerate(columnNames):
            if columnName not in columnNameFilter:
                item = QTableWidgetItem(str(getattr(obj, columnName)))
                table.setItem(row, col + 1, item)  # Shift columns by 1


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
