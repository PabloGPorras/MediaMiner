from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit, QFileDialog, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import QDate, QTime, QDateTime
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from models import engine

Session = sessionmaker(bind=engine)
session = Session()

class ModelForm(QWidget):
    def __init__(self, primary_model_class, related_model_class=None, primary_instance=None, 
                 included_columns=None, excluded_columns=None,
                 editable_fields=None, non_editable_fields=None, edit_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_model_class = primary_model_class
        self.related_model_class = related_model_class
        self.primary_instance = primary_instance
        self.edit_mode = edit_mode
        self.included_columns = included_columns or []
        self.excluded_columns = excluded_columns or []
        self.editable_fields = editable_fields or []
        self.non_editable_fields = non_editable_fields or []
        self.primary_fields = {}
        self.related_forms = []  # Track instances of related forms for dynamic management

        # Main layout
        self.form_layout = QFormLayout()
        self.set_main_layout()
        self.setWindowTitle("Edit Form" if self.edit_mode else "Create New Entry")
        self.setFixedSize(700, 700)

        # Populate form with initial instance if provided
        if self.primary_instance:
            self.populate_form_from_instance()

    def set_main_layout(self):
        """Set up the main layout and build form fields for both primary and related models."""
        # Clear existing items in the form layout without deleting the layout itself
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Build primary model fields
        self.build_model_section(self.primary_model_class, self.primary_fields, "Primary Model Fields")

        # Add "Add Related Entry" button and related forms area if there’s a related model
        if self.related_model_class:
            self.add_related_button = QPushButton("Add Related Entry")
            self.add_related_button.clicked.connect(self.add_related_form)
            self.form_layout.addWidget(self.add_related_button)

            # Scroll area for related forms
            self.related_scroll_area = QScrollArea()
            self.related_scroll_area.setWidgetResizable(True)
            self.related_forms_container = QWidget()
            self.related_forms_layout = QVBoxLayout(self.related_forms_container)
            self.related_scroll_area.setWidget(self.related_forms_container)
            self.form_layout.addRow(QLabel(f"{self.related_model_class.__name__}s:"), self.related_scroll_area)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)
        self.form_layout.addWidget(self.submit_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        self.setLayout(main_layout)

    def build_model_section(self, model_class, fields_dict, section_title):
        """Helper to build fields for a specific model section."""
        self.form_layout.addRow(QLabel(section_title))  # Add section title

        for column in inspect(model_class).c:
            if self._should_include_column(column.name):
                label = QLabel(column.name.capitalize() + ":")
                field = self.create_field(column)
                self.form_layout.addRow(label, field)
                fields_dict[column.name] = field

                # Set field editability based on provided configurations
                if column.name in self.editable_fields:
                    field.setEnabled(True)
                elif column.name in self.non_editable_fields:
                    field.setEnabled(False)

    def _should_include_column(self, column_name):
        """Determine if a column should be included based on included and excluded columns."""
        if self.included_columns and column_name not in self.included_columns:
            return False
        if self.excluded_columns and column_name in self.excluded_columns:
            return False
        return True

    def create_field(self, column):
        """Create an appropriate field based on column type."""
        options_attr = f"{column.name}_options"
        if hasattr(self.primary_model_class, options_attr):
            field = QComboBox()
            field.addItems(getattr(self.primary_model_class, options_attr))
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
        return field

    def populate_form_from_instance(self):
        """Populate primary form fields with data from the provided model instance."""
        for field_name, field_widget in self.primary_fields.items():
            value = getattr(self.primary_instance, field_name, None)
            if value is not None:
                if isinstance(field_widget, QComboBox):
                    index = field_widget.findText(str(value))
                    if index >= 0:
                        field_widget.setCurrentIndex(index)
                elif isinstance(field_widget, QDateEdit):
                    field_widget.setDate(QDate(value.year, value.month, value.day))
                elif isinstance(field_widget, QTimeEdit):
                    field_widget.setTime(QTime(value.hour, value.minute, value.second))
                elif isinstance(field_widget, QDateTimeEdit):
                    field_widget.setDateTime(QDateTime(value))
                elif isinstance(field_widget, QCheckBox):
                    field_widget.setChecked(bool(value))
                else:
                    field_widget.setText(str(value))

    def add_related_form(self):
        """Add a new RelatedModelForm instance to the related forms area."""
        related_form = RelatedModelForm(self.related_model_class)
        self.related_forms.append(related_form)

        # Add delete button for each related form
        form_container = QWidget()
        form_layout = QVBoxLayout()
        form_layout.addWidget(related_form)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.remove_related_form(form_container, related_form))
        form_layout.addWidget(delete_button)
        form_container.setLayout(form_layout)

        self.related_forms_layout.addWidget(form_container)

    def remove_related_form(self, form_container, related_form):
        """Remove a specific related form."""
        self.related_forms_layout.removeWidget(form_container)
        form_container.deleteLater()
        self.related_forms.remove(related_form)

    def reinitialize(self, primary_instance=None, included_columns=None, excluded_columns=None,
                     editable_fields=None, non_editable_fields=None):
        """Reinitialize form with new settings and optionally a new instance."""
        self.primary_instance = primary_instance
        self.included_columns = included_columns or self.included_columns
        self.excluded_columns = excluded_columns or self.excluded_columns
        self.editable_fields = editable_fields or self.editable_fields
        self.non_editable_fields = non_editable_fields or self.non_editable_fields
        self.primary_fields.clear()  # Clear the existing fields dictionary

        # Reset the main layout with the new settings
        self.set_main_layout()

        # Populate the form if a new instance is provided
        if self.primary_instance:
            self.populate_form_from_instance()

    def submit_form(self):
        """Submit form data for the primary model and all related forms to the database."""
        if not self.primary_instance:
            self.primary_instance = self.primary_model_class()

        # Collect data from the primary model form fields
        for field_name, field_widget in self.primary_fields.items():
            if isinstance(field_widget, QComboBox):
                setattr(self.primary_instance, field_name, field_widget.currentText())
            elif isinstance(field_widget, QDateEdit):
                setattr(self.primary_instance, field_name, field_widget.date().toPyDate())
            elif isinstance(field_widget, QTimeEdit):
                setattr(self.primary_instance, field_name, field_widget.time().toPyTime())
            elif isinstance(field_widget, QDateTimeEdit):
                setattr(self.primary_instance, field_name, field_widget.dateTime().toPyDateTime())
            elif isinstance(field_widget, QCheckBox):
                setattr(self.primary_instance, field_name, field_widget.isChecked())
            else:
                setattr(self.primary_instance, field_name, field_widget.text())

        try:
            session.add(self.primary_instance)
            session.commit()
            print(f"{self.primary_model_class.__name__} added/updated successfully!")

            # Commit all related model instances
            for related_form in self.related_forms:
                related_instance = self.related_model_class(**related_form.collect_data())
                session.add(related_instance)

            session.commit()
            print(f"Related {self.related_model_class.__name__} instances added successfully!")
            self.close()
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
