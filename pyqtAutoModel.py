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
    """Handles creating and managing fields for a given SQLAlchemy model."""
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
        # Clear any existing fields if reinitializing
        for i in reversed(range(self.form_layout.count())):
            widget = self.form_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create new fields based on the updated settings
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
            field_widget.setText(str(value))

    def collect_data(self):
        """Collect data from form fields and return as a dictionary."""
        return {field_name: field_widget.text() for field_name, field_widget in self.fields.items()}

    
    def create_field(self, column, editable=True):
        """Create an appropriate field based on column type."""
        options_attr = f"{column.name}_options"
        
        # Use QComboBox if there are predefined options
        if hasattr(self.model_class, options_attr):
            field = QComboBox()
            field.addItems(getattr(self.model_class, options_attr))
            field.setEnabled(editable)

        # Use QSpinBox for integer columns
        elif column.type.python_type == int:
            field = QSpinBox()
            field.setRange(-999999999, 999999999)
            field.setReadOnly(not editable)

        # Use QDoubleSpinBox for float columns
        elif column.type.python_type == float:
            field = QDoubleSpinBox()
            field.setRange(-999999999.0, 999999999.0)
            field.setDecimals(6)
            field.setReadOnly(not editable)

        # Use QCheckBox for boolean columns
        elif column.type.python_type == bool:
            field = QCheckBox()
            field.setEnabled(editable)

        # Use QDateEdit for date columns
        elif column.type.python_type == QDate:
            field = QDateEdit()
            field.setCalendarPopup(True)
            field.setDate(QDate.currentDate())
            field.setEnabled(editable)

        # Use QDateTimeEdit for datetime columns
        elif column.type.python_type == QDateTime:
            field = QDateTimeEdit()
            field.setCalendarPopup(True)
            field.setDateTime(QDateTime.currentDateTime())
            field.setEnabled(editable)

        # Default to QLineEdit for text and other types
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
        """
        Initialize ModelForm with an array of ModelFormFields instances.
        
        Parameters:
            form_fields (list): A list of dictionaries, each containing:
                - `form`: Instance of ModelFormFields
                - `title`: Title of the section (str)
                - `duplicatable`: Whether this form is duplicatable (bool)
        """
        super().__init__(*args, **kwargs)
        
        # Store form fields
        self.form_fields = form_fields
        self.forms_container = {}

        # Initialize layout
        self.main_layout = QVBoxLayout(self)

        # Build each form field section
        for field_info in self.form_fields:
            self.add_form_section(field_info)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)
        self.main_layout.addWidget(self.submit_button)

    def add_form_section(self, field_info):
        """Add a section to the main layout for each form in form_fields."""
        form_fields = field_info['form']
        title = field_info['title']
        duplicatable = field_info.get('duplicatable', False)

        # Layout for each section
        section_layout = QVBoxLayout()
        section_layout.addWidget(QLabel(title))
        
        # Container for multiple instances if duplicatable
        form_container = QVBoxLayout()
        self.forms_container[title] = form_container
        section_layout.addLayout(form_container)
        
        # Add initial form instance
        self.add_form_instance(form_fields, title, duplicatable=duplicatable)

        # Add button for adding forms if duplicatable
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

        # Create a container widget to hold both the form and the delete button (if duplicatable)
        form_container_widget = QWidget()
        form_layout = QVBoxLayout(form_container_widget)
        form_layout.addWidget(form_instance)

        # Only add the delete button if the form is duplicatable
        if duplicatable:
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda: self.remove_form_instance(form_container_widget, title))
            form_layout.addWidget(delete_button)

        # Add the container widget to the form container layout
        self.forms_container[title].addWidget(form_container_widget)

    def remove_form_instance(self, form_container_widget, title):
        """Remove a specific form instance from the layout."""
        # Find and remove the widget from the layout
        self.forms_container[title].removeWidget(form_container_widget)
        form_container_widget.deleteLater()  # Properly delete the widget

    def load_data(self, instances_data):
        """Load data for each form instance based on the provided instances_data."""
        for title, instance_data_list in instances_data.items():
            form_container = self.forms_container.get(title, None)
            if not form_container:
                continue

            # Clear existing forms
            for i in reversed(range(form_container.count())):
                widget = form_container.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Add new instances for each item in instance_data_list
            for instance_data in instance_data_list:
                form_fields = next(f['form'] for f in self.form_fields if f['title'] == title)
                self.add_form_instance(form_fields, title, instance_data, duplicatable=(title == "Relatives"))


    def submit_form(self):
        """Submit form data for each form instance in ModelForm."""
        try:
            all_data = {}

            for field_info in self.form_fields:
                title = field_info['title']
                duplicatable = field_info.get('duplicatable', False)
                form_container = self.forms_container[title]

                if duplicatable:
                    # Collect data from each instance of duplicatable forms
                    data_list = []
                    for i in range(form_container.count()):
                        form_instance_widget = form_container.itemAt(i).widget()
                        form_instance = form_instance_widget.findChild(ModelFormFields)
                        if form_instance:
                            data_list.append(form_instance.collect_data())
                    all_data[title] = data_list
                else:
                    # Collect data from single-instance forms
                    form_instance = form_container.itemAt(0).widget().findChild(ModelFormFields)
                    if form_instance:
                        all_data[title] = form_instance.collect_data()

            print("Collected form data:", all_data)

            # Insert your database save logic here
            session.commit()
            print("Data saved successfully!")

        except Exception as e:
            session.rollback()
            print("An error occurred:", e)
        finally:
            session.close()

    def update_form_fields(self, title, included_columns=None, editable_fields=None):
            form_container = self.forms_container.get(title)
            if form_container:
                form_fields = next((f['form'] for f in self.form_fields if f['title'] == title), None)
                if form_fields:
                    # Update the included_columns and editable_fields if provided
                    if included_columns is not None:
                        form_fields.update_included_columns(included_columns)
                    if editable_fields is not None:
                        form_fields.update_editable_fields(editable_fields)

                    # Remove and re-add the form to refresh the UI
                    for i in reversed(range(form_container.count())):
                        widget = form_container.itemAt(i).widget()
                        if widget:
                            widget.deleteLater()

                    # Re-add updated form instance
                    self.add_form_instance(form_fields, title, duplicatable=(title == "Relatives"))


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

# Show the form
form.show()

# Execute the application
sys.exit(app.exec())
