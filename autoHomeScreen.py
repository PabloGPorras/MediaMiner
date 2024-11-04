class HomeScreen(QWidget):
    def __init__(self, model_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class
        self.fields = [column.name for column in inspect(model_class).c]
        self.grouping_enabled = True
        self.group_by_column = None
        self.option_filters = {}

        # Main Layout
        self.layout = QVBoxLayout()

        # Create Item Button
        self.create_button = QPushButton("Create New Item")
        self.create_button.clicked.connect(self.open_create_form)
        self.layout.addWidget(self.create_button)

        # Toggle Filters / Grouping Options Button
        self.toggle_options_button = QPushButton("Show Filters / Grouping Options")
        self.toggle_options_button.clicked.connect(self.toggle_options_panel)
        self.layout.addWidget(self.toggle_options_button)

        # Create Options Panel
        self.options_panel = self.create_options_panel()

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.fields))
        self.table.setHorizontalHeaderLabels(self.fields)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        self.table.cellDoubleClicked.connect(self.open_edit_form)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.setWindowTitle(f"{self.model_class.__name__} Home")
        self.setMinimumSize(800, 600)

        # Load initial data
        self.load_data()

    def open_create_form(self):
        """Open the create form with a callback to refresh the table."""
        self.form = ModelForm(self.model_class, included_columns=['date', 'name', 'country', 'role'], callback=self.load_data)
        self.form.show()

    def load_data(self):
        """Fetch and display data with filtering and optional grouping."""
        filter_text = self.filter_input.text().lower()
        query = session.query(self.model_class)

        # Apply text filters
        if filter_text:
            filters = [
                getattr(self.model_class, field).ilike(f"%{filter_text}%")
                for field in self.fields if hasattr(getattr(self.model_class, field), 'ilike')
            ]
            query = query.filter(or_(*filters))

        # Apply option field filters
        option_filters = []
        for field, options in self.option_filters.items():
            selected = [opt for opt, cb in options.items() if cb.isChecked()]
            if selected:
                option_filters.append(getattr(self.model_class, field).in_(selected))

        if option_filters:
            query = query.filter(and_(*option_filters))

        data = query.all()

        # Group data or show flat list
        grouped_data = self._group_data(data) if self.grouping_enabled and self.group_by_column else [
            (False, [getattr(row, field) for field in self.fields]) for row in data
        ]

        # Clear and repopulate the table
        self.table.setRowCount(0)
        self.table.clearContents()
        for row_idx, (is_header, row_data) in enumerate(grouped_data):
            self.table.insertRow(row_idx)
            if is_header:
                item = QTableWidgetItem(row_data)
                item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                item.setBackground(QColor("#d3d3d3"))
                self.table.setItem(row_idx, 0, item)
                self.table.setSpan(row_idx, 0, 1, self.table.columnCount())
            else:
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def _group_data(self, data):
        """Group data based on the selected column."""
        grouped_data = []
        current_group = None

        for row in sorted(data, key=lambda x: getattr(x, self.group_by_column)):
            group_value = getattr(row, self.group_by_column)
            if group_value != current_group:
                grouped_data.append((True, f"Group: {group_value}"))
                current_group = group_value

            grouped_data.append((False, [getattr(row, field) for field in self.fields]))

        return grouped_data

    # Other methods remain the same...

class ModelForm(QWidget):
    def __init__(self, model_class, included_columns=None, instance=None, callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class
        self.instance = instance
        self.callback = callback  # Store the callback to refresh the table
        self.fields = {}

        # Set up the form layout
        form_layout = QVBoxLayout()
        included_columns = included_columns or []

        for column in inspect(self.model_class).c:
            if column.name in included_columns:
                label = QLabel(column.name.capitalize())
                field = QLineEdit()
                form_layout.addWidget(label)
                form_layout.addWidget(field)
                self.fields[column.name] = field

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_form)
        form_layout.addWidget(submit_button)

        self.setLayout(form_layout)
        self.setWindowTitle("Create / Edit Entry")
        self.setFixedSize(400, 300)

    def submit_form(self):
        """Submit the form data to the database."""
        new_entry = self.model_class()

        for field_name, field_widget in self.fields.items():
            setattr(new_entry, field_name, field_widget.text())

        try:
            session.add(new_entry)
            session.commit()
            print(f"{self.model_class.__name__} added successfully!")
            if self.callback:
                self.callback()  # Call the callback to refresh the table
            self.close()
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")

# Main Execution
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    home_screen = HomeScreen(User)
    home_screen.show()
    sys.exit(app.exec())
