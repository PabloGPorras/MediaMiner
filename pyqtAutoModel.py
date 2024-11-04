import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit, 
    QVBoxLayout, QFileDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from model import Base, User, UserRelatives  # Replace with your models

# Database Setup
from model import engine

Session = sessionmaker(bind=engine)
session = Session()

class ModelForm(QWidget):
    def __init__(self, model_class, instance=None, related_model_class=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_class = model_class
        self.instance = instance
        self.related_model_class = related_model_class  # Additional model for related entries
        self.fields = {}
        self.related_entries = []

        # Main form layout setup
        self.form_layout = QFormLayout()
        self.set_main_layout()

        # Set up window title and size
        self.setWindowTitle(f"Edit {model_class.__name__}")
        self.setMinimumSize(500, 600)

        # Populate main form if an instance is provided
        if self.instance:
            self.populate_form_from_instance()

        # If related model is provided, create sub-form for related entries
        if self.related_model_class:
            self.related_layout = QVBoxLayout()
            self._create_related_model_section()
            self.form_layout.addRow(self.related_layout)

    def set_main_layout(self):
        """Set up the main layout and build form fields for the primary model."""
        # Clear existing items in the form layout without deleting the layout itself
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Build main form fields
        for column in inspect(self.model_class).c:
            self._add_form_field(column)

        # Add Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)
        self.form_layout.addWidget(self.submit_button)

        # Set up the main layout if it’s not already set
        if not self.layout():
            main_layout = QVBoxLayout()
            main_layout.addLayout(self.form_layout)
            self.setLayout(main_layout)

    def _add_form_field(self, column):
        """Add form fields for each column in the main model."""
        label = QLabel(column.name.capitalize() + ":")
        field = None

        if column.type.python_type == int:
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

    def _create_related_model_section(self):
        """Create UI elements for managing related entries."""
        related_label = QLabel(f"{self.related_model_class.__name__}s")
        self.related_layout.addWidget(related_label)

        # Load existing related entries if the main instance is provided
        if self.instance:
            self.related_entries = session.query(self.related_model_class).filter_by(user_id=self.instance.id).all()
            for related_instance in self.related_entries:
                self._add_related_entry_form(related_instance)

        # Add button to add a new related entry
        add_button = QPushButton(f"Add {self.related_model_class.__name__}")
        add_button.clicked.connect(self._add_new_related_entry)
        self.related_layout.addWidget(add_button)

    def _add_related_entry_form(self, related_instance=None):
        """Add a form row for each related entry."""
        row_layout = QHBoxLayout()
        form_fields = {}

        # Dynamically create fields for each column in the related model
        for column in inspect(self.related_model_class).c:
            if column.name == 'id' or column.name == 'user_id':  # Skip ID fields
                continue
            field = QLineEdit() if column.type.python_type == str else QSpinBox()
            field.setPlaceholderText(column.name.capitalize())
            if related_instance:
                value = getattr(related_instance, column.name, None)
                field.setText(str(value) if value is not None else "")
            row_layout.addWidget(field)
            form_fields[column.name] = field

        # Add delete button for each related entry row
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self._remove_related_entry(row_layout, related_instance))
        row_layout.addWidget(delete_button)

        # Store the form fields in the layout and add it to the main layout
        self.related_layout.addLayout(row_layout)
        self.related_entries.append((related_instance, form_fields))

    def _add_new_related_entry(self):
        """Create a new blank related entry form row."""
        self._add_related_entry_form()

    def _remove_related_entry(self, layout, related_instance=None):
        """Remove a related entry row and delete it from the database if it exists."""
        if related_instance:
            session.delete(related_instance)
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.related_entries = [entry for entry in self.related_entries if entry[0] != related_instance]

    def populate_form_from_instance(self):
        """Populate main form fields with data from the instance."""
        for field_name, field_widget in self.fields.items():
            value = getattr(self.instance, field_name, None)
            if isinstance(field_widget, QLineEdit):
                field_widget.setText(str(value) if value is not None else "")
            elif isinstance(field_widget, QSpinBox) and value is not None:
                field_widget.setValue(int(value))
            elif isinstance(field_widget, QDoubleSpinBox) and value is not None:
                field_widget.setValue(float(value))
            elif isinstance(field_widget, QCheckBox):
                field_widget.setChecked(bool(value))
            elif isinstance(field_widget, QDateEdit) and isinstance(value, date):
                field_widget.setDate(QDate(value.year, value.month, value.day))
            elif isinstance(field_widget, QTimeEdit) and isinstance(value, time):
                field_widget.setTime(QTime(value.hour, value.minute, value.second))
            elif isinstance(field_widget, QDateTimeEdit) and isinstance(value, datetime):
                field_widget.setDateTime(QDateTime(value))

    def submit_form(self):
        """Save the main instance and related entries to the database."""
        if not self.instance:
            self.instance = self.model_class()

        # Update main model instance fields
        for field_name, field_widget in self.fields.items():
            value = field_widget.text() if isinstance(field_widget, QLineEdit) else field_widget.value()
            setattr(self.instance, field_name, value)

        # Commit the main model instance
        session.add(self.instance)
        session.commit()

        # Update related model instances
        for related_instance, form_fields in self.related_entries:
            if not related_instance:
                related_instance = self.related_model_class()
                related_instance.user_id = self.instance.id
            for field_name, field_widget in form_fields.items():
                setattr(related_instance, field_name, field_widget.text())
            session.add(related_instance)

        session.commit()
        print("Form submitted successfully!")
        self.close()
