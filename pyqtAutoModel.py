import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QPushButton, QComboBox, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit, 
    QVBoxLayout, QFileDialog, QHBoxLayout, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt, QTime, QDate, QDateTime
from sqlalchemy import inspect, create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date, time
from model import Base, User  # Replace with your models

# Database Setup
engine = create_engine('sqlite:///your_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='comments')

User.comments = relationship('Comment', back_populates='user', cascade="all, delete-orphan")

class ModelForm(QWidget):
    def __init__(self, model_class, instance=None, included_columns=None, edit_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_class = model_class
        self.instance = instance
        self.edit_mode = edit_mode
        self.included_columns = included_columns or []
        self.fields = {}

        # Main Layout with Form and Comments Section
        main_layout = QHBoxLayout()

        # Form Layout
        self.form_layout = QFormLayout()
        self.form_layout.setHorizontalSpacing(20)
        self.form_layout.setVerticalSpacing(15)
        
        for column in inspect(model_class).c:
            if column.name in self.included_columns:
                self._add_form_field(column)

        # Buttons for Submit and Bulk Import
        if not self.edit_mode:
            self.submit_button = QPushButton("Submit")
            self.submit_button.clicked.connect(self.submit_form)

            self.bulk_import_button = QPushButton("Bulk Import from CSV")
            self.bulk_import_button.clicked.connect(self.bulk_import_csv)

            self.form_layout.addWidget(self.submit_button)
            self.form_layout.addWidget(self.bulk_import_button)

        form_container = QWidget()
        form_container.setLayout(self.form_layout)
        main_layout.addWidget(form_container)

        # Comments Section
        self.comment_section = self.create_comment_section()
        main_layout.addWidget(self.comment_section)

        self.setLayout(main_layout)
        self.setWindowTitle("Edit Form with Comments")
        self.setFixedSize(800, 400)

        if self.instance:
            self.populate_form()
            self.load_comments()

        if self.edit_mode:
            self.disable_fields()

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

    def create_comment_section(self):
        """Create the comments section layout."""
        layout = QVBoxLayout()

        # List to display comments
        self.comment_list = QListWidget()
        layout.addWidget(QLabel("Comments"))
        layout.addWidget(self.comment_list)

        # Input field for adding new comments
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Add a comment...")
        layout.addWidget(self.comment_input)

        # Add Comment Button
        add_comment_button = QPushButton("Add Comment")
        add_comment_button.clicked.connect(self.add_comment)
        layout.addWidget(add_comment_button)

        # Scrollable container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        container.setLayout(layout)
        scroll_area.setWidget(container)

        return scroll_area

    def load_comments(self):
        """Load and display comments related to the instance."""
        if not self.instance:
            return

        self.comment_list.clear()
        comments = session.query(Comment).filter_by(user_id=self.instance.id).all()
        for comment in comments:
            item = QListWidgetItem(f"{comment.timestamp}: {comment.content}")
            self.comment_list.addItem(item)

    def add_comment(self):
        """Add a new comment."""
        content = self.comment_input.text().strip()
        if content and self.instance:
            try:
                new_comment = Comment(content=content, user_id=self.instance.id)
                session.add(new_comment)
                session.commit()
                self.load_comments()
                self.comment_input.clear()
            except Exception as e:
                session.rollback()
                print(f"Error adding comment: {e}")

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
                        setattr(new_entry, col, row[col])
                    session.add(new_entry)
                session.commit()
                print("Bulk import successful!")
            except Exception as e:
                session.rollback()
                print(f"Error during bulk import: {e}")
