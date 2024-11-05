from PyQt6.QtWidgets import (
    QWidget, QLabel, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, 
    QDateEdit, QTimeEdit, QDateTimeEdit, QLineEdit
)
from PyQt6.QtCore import QDate, QTime, QDateTime
from sqlalchemy import inspect
from datetime import datetime, date, time

class RelatedModelForm(QWidget):
    def __init__(self, related_model_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_model_class = related_model_class
        self.fields = {}
        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)
        self.build_form()

    def build_form(self):
        """Dynamically build form fields based on related model columns."""
        # Generate form fields based on columns in related model class
        for column in inspect(self.related_model_class).c:
            label = QLabel(column.name.capitalize() + ":")
            field = self.create_field(column)
            self.form_layout.addRow(label, field)
            self.fields[column.name] = field

    def create_field(self, column):
        """Create an appropriate field based on column type."""
        options_attr = f"{column.name}_options"
        if hasattr(self.related_model_class, options_attr):
            field = QComboBox()
            field.addItems(getattr(self.related_model_class, options_attr))
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

    def collect_data(self):
        """Collect data from form fields into a dictionary."""
        data = {}
        for field_name, field_widget in self.fields.items():
            # Handle each field type accordingly to get the value
            if isinstance(field_widget, QComboBox):
                data[field_name] = field_widget.currentText()
            elif isinstance(field_widget, QDateEdit):
                data[field_name] = field_widget.date().toPyDate()
            elif isinstance(field_widget, QTimeEdit):
                data[field_name] = field_widget.time().toPyTime()
            elif isinstance(field_widget, QDateTimeEdit):
                data[field_name] = field_widget.dateTime().toPyDateTime()
            elif isinstance(field_widget, QCheckBox):
                data[field_name] = field_widget.isChecked()
            else:
                data[field_name] = field_widget.text()
        return data
