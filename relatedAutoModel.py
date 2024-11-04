from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit, 
    QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from model import engine

Session = sessionmaker(bind=engine)
session = Session()

class RelatedModelForm(QWidget):
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

        # Populate form with initial instance if provided
        if self.instance:
            self.populate_form_from_instance()

    def set_main_layout(self):
        """Set up the main layout and build form fields."""
        # Clear existing items in the form layout without deleting the layout itself
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Build form fields in the layout
        for column in inspect(self.model_class).c:
            if self._should_include_column(column.name):
                self._add_form_field(column)

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
                    index = field_widget.findText(str(value))
                    if index >= 0:
                        field_widget.setCurrentIndex(index)
                elif isinstance(field_widget, QDateEdit):
                    if isinstance(value, datetime):
                        value = value.date()
                    field_widget.setDate(QDate(value.year, value.month, value.day))
                elif isinstance(field_widget, QTimeEdit):
                    field_widget.setTime(QTime(value.hour, value.minute, value.second))
                elif isinstance(field_widget, QDateTimeEdit):
                    field_widget.setDateTime(QDateTime(value))
                elif isinstance(field_widget, QCheckBox):
                    field_widget.setChecked(bool(value))
                else:
                    field_widget.setText(str(value))
