import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit, 
    QVBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from model import Base, User  # Replace with your models

# Database Setup
from model import engine

Session = sessionmaker(bind=engine)
session = Session()

class ModelForm(QWidget):
    def __init__(self, model_class, instance=None, included_columns=None, excluded_columns=None,
                 editable_fields=None, non_editable_fields=None, edit_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_class = model_class
        self.instance = instance
        self.edit_mode = edit_mode
        self.included_columns = included_columns or []
        self.excluded_columns = excluded_columns or []
        self.editable_fields = editable_fields or []
        self.non_editable_fields = non_editable_fields or []
        self.fields = {}

        # Main form layout setup
        self.form_layout = QFormLayout()
        self.set_main_layout()
        self.setWindowTitle("Edit Form" if self.edit_mode else "Create New Entry")
        self.setFixedSize(400, 400)

        # Populate form with initial instance if provided
        if self.instance:
            self.populate_form_from_instance()

    def set_main_layout(self):
        """Set up the main layout and build form fields."""
        # Clear existing layout if reinitializing
        QWidget().setLayout(self.form_layout)
        
        # Build form layout
        for column in inspect(self.model_class).c:
            if self._should_include_column(column.name):
                self._add_form_field(column)

        # Add buttons for Submit and Bulk Import if not in edit mode
        if not self.edit_mode:
            self.submit_button = QPushButton("Submit")
            self.submit_button.clicked.connect(self.submit_form)

            self.bulk_import_button = QPushButton("Bulk Import from CSV")
            self.bulk_import_button.clicked.connect(self.bulk_import_csv)

            self.form_layout.addWidget(self.submit_button)
            self.form_layout.addWidget(self.bulk_import_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        self.setLayout(main_layout)

        # Set field editability based on configuration
        if self.edit_mode:
            self.set_field_editability()

    def _should_include_column(self, column_name):
        """Determine if a column should be included based on included and excluded columns."""
        if self.included_columns and column_name not in self.included_columns:
            return False
        if self.excluded_columns and column_name in self.excluded_columns:
            return False
        return True

    def _add_form_field(self, column):
        label = QLabel(column.name.capitalize() + ":")
        field = None

        options_attr = f"{column.name}_options"
        if hasattr(self.model_class, options_attr):
            field = QComboBox()
            field.addItems(getattr(self.model_class, options_attr))
        elif column.type.python_type == int:
            field = QSpinBox()
            field.setRange(-999999999, 999999999)
        elif column.type.python_type == float:
            field = QDoubleSpinBox()
            field.setRange(-999999999.99, 999999999.99)
        elif column.type.python_type == bool:
            field = QCheckBox()
        elif column.type.python_type == date:
            field = QDateEdit()
            field.setDate(QDate.currentDate())
            field.setCalendarPopup(True)
        elif column.type.python_type == time:
            field = QTimeEdit()
            field.setTime(QTime.currentTime())
        elif column.type.python_type == datetime:
            field = QDateTimeEdit()
            field.setDateTime(QDateTime.currentDateTime())
            field.setCalendarPopup(True)
        else:
            field = QLineEdit()
            field.setPlaceholderText(f"Enter {column.name}")

        self.form_layout.addRow(label, field)
        self.fields[column.name] = field

    def populate_form_from_instance(self):
        """Populate form fields with data from the provided model instance."""
        for field_name, field_widget in self.fields.items():
            value = getattr(self.instance, field_name, None)
            if value is not None:
                if isinstance(field_widget, QComboBox):
                    index = field_widget.findText(value)
                    if index >= 0:
                        field_widget.setCurrentIndex(index)
                elif isinstance(field_widget, QDateEdit):
                    field_widget.setDate(value)
                elif isinstance(field_widget, QTimeEdit):
                    field_widget.setTime(value)
                elif isinstance(field_widget, QDateTimeEdit):
                    field_widget.setDateTime(value)
                elif isinstance(field_widget, QCheckBox):
                    field_widget.setChecked(bool(value))
                else:
                    field_widget.setText(str(value))

    def set_field_editability(self):
        """Set fields to be editable or non-editable based on editable_fields and non_editable_fields."""
        for field_name, field_widget in self.fields.items():
            if self.editable_fields and field_name in self.editable_fields:
                field_widget.setEnabled(True)
            elif self.non_editable_fields and field_name in self.non_editable_fields:
                field_widget.setEnabled(False)
            elif not self.editable_fields and not self.non_editable_fields:
                field_widget.setEnabled(True)
            else:
                field_widget.setEnabled(field_name in self.editable_fields)

    def submit_form(self):
        """Submit form data to the database."""
        if not self.instance:
            self.instance = self.model_class()

        for field_name, field_widget in self.fields.items():
            if isinstance(field_widget, QComboBox):
                setattr(self.instance, field_name, field_widget.currentText())
            elif isinstance(field_widget, QDateEdit):
                setattr(self.instance, field_name, field_widget.date().toPyDate())
            elif isinstance(field_widget, QTimeEdit):
                setattr(self.instance, field_name, field_widget.time().toPyTime())
            elif isinstance(field_widget, QDateTimeEdit):
                setattr(self.instance, field_name, field_widget.dateTime().toPyDateTime())
            elif isinstance(field_widget, QCheckBox):
                setattr(self.instance, field_name, field_widget.isChecked())
            else:
                setattr(self.instance, field_name, field_widget.text())

        try:
            session.add(self.instance)
            session.commit()
            print(f"{self.model_class.__name__} added/updated successfully!")
            self.close()
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")

    def bulk_import_csv(self):
        """Bulk import data from CSV."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                df = pd.read_csv(file_name)
                model_columns = [col.name for col in inspect(self.model_class).c]
                for _, row in df.iterrows():
                    new_entry = self.model_class()
                    for col in model_columns:
                        if pd.notnull(row[col]):
                            setattr(new_entry, col, row[col])
                    session.add(new_entry)

                session.commit()
                print("Bulk import successful!")
            except Exception as e:
                session.rollback()
                print(f"Error during bulk import: {e}")

    def reinitialize(self, instance=None, included_columns=None, excluded_columns=None,
                     editable_fields=None, non_editable_fields=None, edit_mode=False):
        """Reinitialize form with new settings and optionally a new instance."""
        self.instance = instance
        self.included_columns = included_columns or self.included_columns
        self.excluded_columns = excluded_columns or self.excluded_columns
        self.editable_fields = editable_fields or self.editable_fields
        self.non_editable_fields = non_editable_fields or self.non_editable_fields
        self.edit_mode = edit_mode
        self.fields.clear()  # Clear the existing fields dictionary

        # Reset the main layout with the new settings
        self.set_main_layout()

        # Populate the form if a new instance is provided
        if self.instance:
            self.populate_form_from_instance()
        