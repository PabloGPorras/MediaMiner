from PyQt6.QtWidgets import QApplication, QTableWidget, QPushButton, QTableWidgetItem
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
        table.setColumnWidth(0, 70)  # Adjust width as desired

    # Populate the rows
    for row, obj in enumerate(objectArray):
        if rowAction:
            # Create the action button
            btn = QPushButton(table)
            btn.setText("Action")  # Optional: Add button text
            btn.setFixedSize(50, 30)  # Set the size of the button
            btn.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")  # Optional styling
            btn.clicked.connect(lambda checked, r=row: print(f"Action triggered for row {r}"))  # Example action

            # Add the button to the first column
            table.setCellWidget(row, 0, btn)

        # Populate the rest of the columns (shift by 1 because the action button occupies the first column)
        for col, columnName in enumerate(columnNames):
            if columnName not in columnNameFilter:
                item = QTableWidgetItem(str(getattr(obj, columnName)))
                table.setItem(row, col + 1, item)  # Shift columns by 1


# Example usage
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Sample table and data
    tableWidget = QTableWidget()
    tableWidget.setRowCount(3)
    tableWidget.setColumnCount(3)

    # Simulated object with columns
    class SampleObject:
        def __init__(self, group_id, unique_ref, request_type):
            self.group_id = group_id
            self.unique_ref = unique_ref
            self.request_type = request_type

        @property
        def __table__(self):
            from collections import namedtuple
            Column = namedtuple("Column", ["name"])
            return namedtuple("Table", ["columns"])(columns=[
                Column("group_id"),
                Column("unique_ref"),
                Column("request_type"),
            ])

    # Sample data
    objects = [
        SampleObject("GROUP001", "UNIQUE001", "TYPE001"),
        SampleObject("GROUP002", "UNIQUE002", "TYPE002"),
        SampleObject("GROUP003", "UNIQUE003", "TYPE003"),
    ]

    # Load data into the table
    loadDataObjects(
        tableWidget, objects, columnNameFilter=[], rowAction=lambda row: print(f"Action for row {row}")
    )

    # Show the table
    tableWidget.resize(800, 400)
    tableWidget.show()

    sys.exit(app.exec())
