from datetime import date, time
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    QFileDialog, QScrollArea, QHBoxLayout, QApplication
)
from PyQt6.QtCore import QDate, QTime, QDateTime
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine, inspect
import sys

from models import User, UserRelatives

DATABASE_URI = 'sqlite:///your_database.db'
engine = create_engine(DATABASE_URI, echo=True)
Base = declarative_base()
session = Session(bind=engine)


class ModelFormFields(QWidget):
    def __init__(self, model_class, included_columns=None, editable_fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class
        self.included_columns = included_columns or []
        self.editable_fields = editable_fields or []
        self.fields = {}

        # Setup form layout
        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)
        self.build_fields()

    def build_fields(self):
        """Create form fields based on model columns and inclusion/exclusion criteria."""
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.fields = {}
        for column in inspect(self.model_class).c:
            if column.name in self.included_columns:
                editable = column.name in self.editable_fields
                field = self.create_field(column, editable)
                self.form_layout.addRow(QLabel(column.name.capitalize()), field)
                self.fields[column.name] = field

    def load_data(self, instance):
        """Load data from an instance into the form fields."""
        for field_name, field_widget in self.fields.items():
            value = getattr(instance, field_name, "")

            # Handle different widget types appropriately
            if isinstance(field_widget, QLineEdit):
                field_widget.setText(str(value))
            elif isinstance(field_widget, QComboBox):
                index = field_widget.findText(str(value), Qt.MatchFixedString)
                if index >= 0:
                    field_widget.setCurrentIndex(index)
            elif isinstance(field_widget, QSpinBox):
                field_widget.setValue(int(value))
            elif isinstance(field_widget, QDoubleSpinBox):
                field_widget.setValue(float(value))
            elif isinstance(field_widget, QCheckBox):
                field_widget.setChecked(bool(value))
            elif isinstance(field_widget, QDateEdit):
                if isinstance(value, date):
                    field_widget.setDate(QDate(value.year, value.month, value.day))
            elif isinstance(field_widget, QDateTimeEdit):
                if isinstance(value, datetime.datetime):
                    field_widget.setDateTime(QDateTime(value.year, value.month, value.day, value.hour, value.minute, value.second))


def collect_data(self):
    """Collect data from form fields and return as a dictionary with appropriate data types."""
    data = {}
    for field_name, field_widget in self.fields.items():
        if isinstance(field_widget, QLineEdit):
            data[field_name] = field_widget.text()
        elif isinstance(field_widget, QComboBox):
            data[field_name] = field_widget.currentText()
        elif isinstance(field_widget, QSpinBox) or isinstance(field_widget, QDoubleSpinBox):
            data[field_name] = field_widget.value()
        elif isinstance(field_widget, QCheckBox):
            data[field_name] = field_widget.isChecked()
        elif isinstance(field_widget, QDateEdit):
            data[field_name] = field_widget.date().toPyDate()  # Converts QDate to Python date
        elif isinstance(field_widget, QDateTimeEdit):
            data[field_name] = field_widget.dateTime().toPyDateTime()  # Converts QDateTime to Python datetime
        elif isinstance(field_widget, QTimeEdit):
            data[field_name] = field_widget.time().toPyTime()  # Converts QTime to Python time
        else:
            data[field_name] = field_widget.text()  # Fallback to text for unknown widgets

    return data


    def create_field(self, column, editable=True):
        options_attr = f"{column.name}_options"
        
        if hasattr(self.model_class, options_attr):
            field = QComboBox()
            field.addItems(getattr(self.model_class, options_attr))
            field.setEnabled(editable)
        elif column.type.python_type == int:
            field = QSpinBox()
            field.setRange(-999999999, 999999999)
            field.setReadOnly(not editable)
        elif column.type.python_type == float:
            field = QDoubleSpinBox()
            field.setRange(-999999999.0, 999999999.0)
            field.setDecimals(6)
            field.setReadOnly(not editable)
        elif column.type.python_type == bool:
            field = QCheckBox()
            field.setEnabled(editable)
        elif column.type.python_type == QDate:
            field = QDateEdit()
            field.setCalendarPopup(True)
            field.setDate(QDate.currentDate())
            field.setEnabled(editable)
        elif column.type.python_type == QDateTime:
            field = QDateTimeEdit()
            field.setCalendarPopup(True)
            field.setDateTime(QDateTime.currentDateTime())
            field.setEnabled(editable)
        else:
            field = QLineEdit()
            field.setReadOnly(not editable)

        return field

    def update_included_columns(self, included_columns):
        """Update which columns are included and rebuild the fields."""
        self.included_columns = included_columns
        self.build_fields()

    def update_editable_fields(self, editable_fields):
        """Update which fields are editable and rebuild the fields."""
        self.editable_fields = editable_fields
        self.build_fields()


class ModelForm(QWidget):
    def __init__(self, form_fields, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.form_fields = form_fields
        self.forms_container = {}

        self.main_layout = QVBoxLayout(self)

        for field_info in self.form_fields:
            self.add_form_section(field_info)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)
        self.main_layout.addWidget(self.submit_button)

    def add_form_section(self, field_info):
        form_fields = field_info['form']
        title = field_info['title']
        duplicatable = field_info.get('duplicatable', False)

        section_layout = QVBoxLayout()
        section_layout.addWidget(QLabel(title))
        
        form_container = QVBoxLayout()
        self.forms_container[title] = form_container
        section_layout.addLayout(form_container)
        
        self.add_form_instance(form_fields, title, duplicatable=duplicatable)

        if duplicatable:
            add_button = QPushButton(f"Add {title}")
            add_button.clicked.connect(lambda: self.add_form_instance(form_fields, title, duplicatable=True))
            section_layout.addWidget(add_button)

        self.main_layout.addLayout(section_layout)

    def add_form_instance(self, form_fields, title, instance_data=None, duplicatable=False):
        """Add a new instance of ModelFormFields to the container layout."""
        form_instance = ModelFormFields(
            model_class=form_fields.model_class,
            included_columns=form_fields.included_columns,
            editable_fields=form_fields.editable_fields
        )

        if instance_data:
            form_instance.load_data(instance_data)

        form_container_widget = QWidget()
        form_layout = QVBoxLayout(form_container_widget)
        form_layout.addWidget(form_instance)

        if duplicatable:
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda: self.remove_form_instance(form_container_widget, title))
            form_layout.addWidget(delete_button)

        self.forms_container[title].addWidget(form_container_widget)


    def remove_form_instance(self, form_container_widget, title):
        self.forms_container[title].removeWidget(form_container_widget)
        form_container_widget.deleteLater()

    def load_data(self, instances_data):
        """
        Load data into the form from SQLAlchemy instances.
        
        Parameters:
            instances_data (dict): A dictionary where keys are form section titles
                                and values are SQLAlchemy instances (or lists of them)
        """
        for title, instance_data_list in instances_data.items():
            form_container = self.forms_container.get(title, None)
            if not form_container:
                continue

            # Clear existing forms in the section
            for i in reversed(range(form_container.count())):
                widget = form_container.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Handle single instance (non-duplicatable) and multiple instances (duplicatable)
            for instance_data in (instance_data_list if isinstance(instance_data_list, list) else [instance_data_list]):
                form_fields = next(f['form'] for f in self.form_fields if f['title'] == title)
                duplicatable = next(f['duplicatable'] for f in self.form_fields if f['title'] == title)
                self.add_form_instance(form_fields, title, instance_data=instance_data, duplicatable=duplicatable)


            
    def submit_form(self):
        try:
            all_data = {}
    
            for field_info in self.form_fields:
                title = field_info['title']
                duplicatable = field_info.get('duplicatable', False)
                form_container = self.forms_container[title]
                model_class = field_info['form'].model_class
    
                if duplicatable:
                    data_list = []
                    for i in range(form_container.count()):
                        form_instance_widget = form_container.itemAt(i).widget()
                        form_instance = form_instance_widget.findChild(ModelFormFields)
                        if form_instance:
                            data = form_instance.collect_data()
                            data_list.append(data)
                            # Create an instance of the model class with the collected data and add to session
                            instance = model_class(**data)
                            session.add(instance)
                    all_data[title] = data_list
                else:
                    form_instance = form_container.itemAt(0).widget().findChild(ModelFormFields)
                    if form_instance:
                        data = form_instance.collect_data()
                        all_data[title] = data
                        # Create or update the instance of the model class with the collected data
                        instance = model_class(**data)
                        session.add(instance)
    
            print("Collected form data:", all_data)
    
            # Commit all new instances to the database
            session.commit()
            print("Data saved successfully!")
    
        except Exception as e:
            session.rollback()  # Rollback in case of error
            print("An error occurred:", e)
        finally:
            session.close()


    def update_form_fields(self, title, included_columns=None, editable_fields=None):
        form_container = self.forms_container.get(title)
        if form_container:
            form_fields = next((f['form'] for f in self.form_fields if f['title'] == title), None)
            if form_fields:
                if included_columns is not None:
                    form_fields.update_included_columns(included_columns)
                if editable_fields is not None:
                    form_fields.update_editable_fields(editable_fields)

                # Remove and re-add the form to refresh the UI
                for i in reversed(range(form_container.count())):
                    widget = form_container.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()

                # Re-add updated form instance with correct duplicatable setting
                duplicatable = next((f['duplicatable'] for f in self.form_fields if f['title'] == title), False)
                self.add_form_instance(form_fields, title, duplicatable=duplicatable)



# Initialize QApplication
app = QApplication(sys.argv)

# Initialize form fields
user_form_fields = ModelFormFields(User, included_columns=['name', 'email'], editable_fields=['name'])
relative_form_fields = ModelFormFields(UserRelatives, included_columns=['relation', 'name'], editable_fields=['name', 'relation'])

# Create ModelForm with multiple fields
form = ModelForm([
    {'form': user_form_fields, 'title': 'User', 'duplicatable': False},
    {'form': relative_form_fields, 'title': 'Relatives', 'duplicatable': True}
])

form.update_form_fields('User',included_columns=['name','email'],editable_fields=[])
# Show the form
form.show()

# Execute the application
sys.exit(app.exec())
