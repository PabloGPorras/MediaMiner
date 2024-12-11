from PyQt6.QtWidgets import QTableWidget, QPushButton, QVBoxLayout, QWidget, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
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
            # Create a container widget to hold the button
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
            layout.setSpacing(0)  # No spacing
            layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # Align to top-left

            # Create the action button
            btn = QPushButton(container)
            btn.setIcon(QIcon("path/to/your/icon.png"))  # Replace with your icon file
            btn.setIconSize(QSize(16, 16))  # Set the icon size
            btn.setStyleSheet("border: none; padding: 0;")  # Compact style
            btn.clicked.connect(lambda checked, r=row: print(f"Action triggered for row {r}"))  # Example action

            # Add the button to the container layout
            layout.addWidget(btn)

            # Add the container to the first column
            table.setCellWidget(row, 0, container)

        # Populate the rest of the columns (shift by 
