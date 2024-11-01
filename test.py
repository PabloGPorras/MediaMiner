# streamlit_form.py
import streamlit as st
from sqlalchemy import inspect, Boolean, Date, DateTime, Float, Enum
from my_model import User  # Import your SQLAlchemy model here

def generate_form(model):
    # Display the form title
    st.title(f"Form for {model.__name__}")

    # Get model columns
    inspector = inspect(model)
    form_data = {}

    # Loop through columns and create form inputs based on column types
    for column in inspector.columns:
        column_name = column.name
        column_type = column.type

        # Handle different column types
        if isinstance(column_type, Integer):
            form_data[column_name] = st.number_input(column_name, step=1)
        elif isinstance(column_type, String):
            form_data[column_name] = st.text_input(column_name)
        elif isinstance(column_type, Boolean):
            form_data[column_name] = st.checkbox(column_name)
        elif isinstance(column_type, Date):
            form_data[column_name] = st.date_input(column_name)
        elif isinstance(column_type, DateTime):
            form_data[column_name] = st.date_input(column_name)
        elif isinstance(column_type, Float):
            form_data[column_name] = st.number_input(column_name, format="%.2f")
        elif isinstance(column_type, Enum):
            # For Enum fields, we create a dropdown list with enum options
            form_data[column_name] = st.selectbox(column_name, [e.value for e in column.type.enums])
        else:
            # Default to text input for other types
            form_data[column_name] = st.text_input(column_name)

    # Add a submit button
    submit_button = st.button("Submit")

    if submit_button:
        # Display the submitted form data
        st.write("Submitted Data:", form_data)

if __name__ == "__main__":
    generate_form(User)