from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QDateTimeEdit, QTimeEdit
from PyQt6.QtCore import QDate, QDateTime, QTime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QScrollArea
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, inspect
# Define the database URI. You can change this to any database URI supported by SQLAlchemy.
# For SQLite, use 'sqlite:///your_database.db'
DATABASE_URI = 'sqlite:///your_database.db'

# Create the engine
engine = create_engine(DATABASE_URI, echo=True)

# Base class for declarative models
Base = declarative_base()

# Create a configured "Session" class
session = Session(bind=engine)

class ModelForm(QWidget):
    def __init__(self, primary_model_class, related_model_class=None, primary_instance=None, 
                 included_columns=None, excluded_columns=None, editable_fields=None, non_editable_fields=None,
                 related_included_columns=None, related_excluded_columns=None, related_editable_fields=None, related_non_editable_fields=None,
                 edit_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store primary and related model information
        self.primary_model_class = primary_model_class
        self.primary_instance = primary_instance
        self.included_columns = included_columns or []
        self.excluded_columns = excluded_columns or []
        self.editable_fields = editable_fields or []
        self.non_editable_fields = non_editable_fields or []
        self.edit_mode = edit_mode

        self.related_model_class = related_model_class
        self.related_included_columns = related_included_columns or []
        self.related_excluded_columns = related_excluded_columns or []
        self.related_editable_fields = related_editable_fields or []
        self.related_non_editable_fields = related_non_editable_fields or []
        self.related_forms = []

        # Dictionary to store primary form field widgets
        self.primary_fields = {}

        # Main layout setup
        self.main_layout = QVBoxLayout(self)
        
        # Add scroll area for related forms
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.related_forms_layout = QVBoxLayout()  # Initialize related_forms_layout here
        self.related_container = QWidget()
        self.related_container.setLayout(self.related_forms_layout)
        self.scroll_area.setWidget(self.related_container)
        self.main_layout.addWidget(self.scroll_area)

        # Build the main layout and form fields
        self.set_main_layout()

    def set_main_layout(self):
        """Set up the main layout and build form fields."""
        # Primary model fields
        primary_layout = QFormLayout()
        primary_layout.addRow(QLabel("Primary Model Fields"))
        for column in inspect(self.primary_model_class).c:
            if self._should_include_column(column.name, self.included_columns, self.excluded_columns):
                field = self._create_field(column, editable=(column.name in self.editable_fields))
                primary_layout.addRow(QLabel(column.name.capitalize()), field)
                self.primary_fields[column.name] = field  # Store field in primary_fields

        # Add related model label and button
        related_layout = QVBoxLayout()
        if self.related_model_class:
            related_layout.addWidget(QLabel(self.related_model_class.__name__ + "s:"))
            add_related_button = QPushButton("Add Related Entry")
            add_related_button.clicked.connect(self.add_related_form)
            related_layout.addWidget(add_related_button)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_form)

        # Assemble main layout
        self.main_layout.addLayout(primary_layout)  # Add the primary form layout here
        self.main_layout.addWidget(self.scroll_area)  # Add scroll area for related entries
        self.main_layout.addLayout(related_layout)  # Add related entry button layout below the related form
        self.main_layout.addWidget(submit_button)  # Add the submit button at the end

    def load_data(self, primary_instance=None, related_instances=None):
        """Load data into the form from a primary instance and related instances."""
        if primary_instance:
            for field_name, field_widget in self.primary_fields.items():
                # Use `getattr` to retrieve the value from the instance
                value = getattr(primary_instance, field_name, "")
                field_widget.setText(str(value))  # Set the field value as text (convert if necessary)

        if related_instances:
            # Clear any existing related forms first
            for related_form in self.related_forms:
                self.remove_related_form(related_form.parentWidget(), related_form)

            # Add a new form for each related instance
            for related_instance in related_instances:
                form_container = QWidget()
                form_layout = QVBoxLayout(form_container)

                # Create a RelatedModelForm with the related instance's data
                related_form = RelatedModelForm(
                    self.related_model_class,
                    included_columns=self.related_included_columns,
                    excluded_columns=self.related_excluded_columns,
                    editable_fields=self.related_editable_fields,
                    non_editable_fields=self.related_non_editable_fields,
                )
                related_form.load_data(related_instance)  # Load data into the related form
                form_layout.addWidget(related_form)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda: self.remove_related_form(form_container, related_form))
                form_layout.addWidget(delete_button)

                self.related_forms_layout.addWidget(form_container)  # Add to related_forms_layout
                self.related_forms.append(related_form)
                
    def update_fields(self, included_columns=None, excluded_columns=None, editable_fields=None, non_editable_fields=None,
                      edit_mode=None, related_included_columns=None, related_excluded_columns=None, 
                      related_editable_fields=None, related_non_editable_fields=None, related_edit_mode=None):
        """Update visibility, editability, and edit mode of form fields and related entries."""
        # Update primary model fields
        self.included_columns = included_columns or self.included_columns
        self.excluded_columns = excluded_columns or self.excluded_columns
        self.editable_fields = editable_fields or self.editable_fields
        self.non_editable_fields = non_editable_fields or self.non_editable_fields
        if edit_mode is not None:
            self.edit_mode = edit_mode  # Update edit mode if provided

        for column_name, field in self.primary_fields.items():
            # Update visibility
            if self._should_include_column(column_name, self.included_columns, self.excluded_columns):
                field.show()
            else:
                field.hide()

            # Update editability based on edit_mode
            if self.edit_mode and column_name in self.editable_fields:
                field.setReadOnly(False)
            else:
                field.setReadOnly(True)

        # Update related model fields
        self.related_included_columns = related_included_columns or self.related_included_columns
        self.related_excluded_columns = related_excluded_columns or self.related_excluded_columns
        self.related_editable_fields = related_editable_fields or self.related_editable_fields
        self.related_non_editable_fields = related_non_editable_fields or self.related_non_editable_fields
        if related_edit_mode is not None:
            self.related_edit_mode = related_edit_mode  # Update related edit mode if provided

        # Update each related form's fields
        for related_form in self.related_forms:
            related_form.update_fields(
                included_columns=self.related_included_columns,
                excluded_columns=self.related_excluded_columns,
                editable_fields=self.related_editable_fields,
                non_editable_fields=self.related_non_editable_fields,
                edit_mode=self.related_edit_mode
            )

    def submit_form(self):
        """Submit form data for both primary and related forms."""

        try:
            # Step 1: Collect data from primary form
            primary_data = {}
            for field_name, field_widget in self.primary_fields.items():
                primary_data[field_name] = field_widget.text()  # Adjust for widget types as needed

            if self.edit_mode and self.primary_instance:
                # If edit mode, update the existing primary instance
                for key, value in primary_data.items():
                    setattr(self.primary_instance, key, value)
                primary_instance = self.primary_instance
            else:
                # Otherwise, create a new primary model instance
                primary_instance = self.primary_model_class(**primary_data)
                session.add(primary_instance)

            # Commit to get the primary instance ID (if necessary for related records)
            session.commit()

            # Step 2: Collect data from related forms and associate with primary instance
            for related_form in self.related_forms:
                related_data = related_form.collect_data()

                # Create a related model instance with the collected data
                related_instance = self.related_model_class(**related_data)

                # Set foreign key reference to primary instance (assuming foreign key field is "user_id")
                if hasattr(related_instance, 'user_id'):
                    related_instance.user_id = primary_instance.id

                session.add(related_instance)

            # Step 3: Commit all changes to the database
            session.commit()
            print("Data saved successfully!")

        except Exception as e:
            session.rollback()  # Rollback in case of error
            print("An error occurred:", e)
        finally:
            session.close()  # Always close the session

    def _should_include_column(self, column_name, included_columns, excluded_columns):
        """Helper to determine if a column should be included based on parameters."""
        if included_columns and column_name not in included_columns:
            return False
        if excluded_columns and column_name in excluded_columns:
            return False
        return True

    def _create_field(self, column, editable=True):
        """Create a field based on column type."""
        field = QLineEdit()
        field.setReadOnly(not editable)
        return field

    def add_related_form(self):
        """Add a new RelatedModelForm with a delete button."""
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        # Pass the related model and relevant include/exclude parameters
        related_form = RelatedModelForm(
            self.related_model_class,
            included_columns=self.related_included_columns,
            excluded_columns=self.related_excluded_columns,
            editable_fields=self.related_editable_fields,
            non_editable_fields=self.related_non_editable_fields,
        )
        form_layout.addWidget(related_form)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.remove_related_form(form_container, related_form))
        form_layout.addWidget(delete_button)

        self.related_forms_layout.addWidget(form_container)  # Add to related_forms_layout
        self.related_forms.append(related_form)

    def remove_related_form(self, form_container, related_form):
        """Remove a related form from the layout and list."""
        self.related_forms_layout.removeWidget(form_container)
        form_container.deleteLater()

        if related_form in self.related_forms:
            self.related_forms.remove(related_form)

class RelatedModelForm(QWidget):
    def __init__(self, related_model_class, included_columns=None, excluded_columns=None,
                 editable_fields=None, non_editable_fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_model_class = related_model_class
        self.included_columns = included_columns or []
        self.excluded_columns = excluded_columns or []
        self.editable_fields = editable_fields or []
        self.non_editable_fields = non_editable_fields or []
        self.fields = {}

        # Form layout
        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)
        self.build_form()

    def build_form(self):
        """Build form fields based on related model columns."""
        for column in inspect(self.related_model_class).c:
            # Use _should_include_column to determine if the column should be included
            if self._should_include_column(column.name, self.included_columns, self.excluded_columns):
                editable = column.name in self.editable_fields if self.editable_fields else True
                field = self.create_field(column, editable)
                self.form_layout.addRow(QLabel(column.name.capitalize()), field)
                self.fields[column.name] = field

    def _should_include_column(self, column_name, included_columns, excluded_columns):
        """Determine if a column should be included based on included/excluded columns."""
        if included_columns and column_name not in included_columns:
            return False
        if excluded_columns and column_name in excluded_columns:
            return False
        return True

    def create_field(self, column, editable):
        """Create a field based on column type."""
        field = QLineEdit()
        field.setReadOnly(not editable)
        return field

    def collect_data(self):
        """Collect data from the related form fields."""
        data = {}
        for field_name, field_widget in self.fields.items():
            data[field_name] = field_widget.text()  # Adjust for specific widget types if needed
        return data
