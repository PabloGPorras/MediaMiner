from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)  # Reduce spacing between notifications
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        # Connect a mouse press event to clear notifications
        self.mousePressEvent = self.clear_all_notifications

    def add_error(self, error_message):
        # Create a container for each error
        error_container = QWidget()
        error_container.setStyleSheet(
            "background-color: #ffeeee; border: 1px solid red; padding: 3px; border-radius: 3px;"
        )
        error_layout = QVBoxLayout()
        error_layout.setSpacing(1)
        error_layout.setContentsMargins(3, 3, 3, 3)
        error_container.setLayout(error_layout)

        # Scrollable area for long error messages
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(60)  # Set max height for the error box
        scroll_area.setStyleSheet("border: none;")

        # Error label
        error_label = QLabel(error_message)
        error_label.setStyleSheet("color: red; font-size: 12px;")
        error_label.setWordWrap(True)
        error_label.setMaximumWidth(300)  # Optional: Limit the width for better readability
        scroll_area.setWidget(error_label)

        error_layout.addWidget(scroll_area)

        # Add the container to the main layout
        self.layout.addWidget(error_container)

    def clear_all_notifications(self, event):
        """Clear all notifications when the area is clicked."""
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error Notification Example")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Notification area
        self.notification_area = NotificationWidget(self)
        self.notification_area.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.notification_area)

        # Central content
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        # Button to trigger errors
        error_button = QPushButton("Trigger Error")
        error_button.clicked.connect(self.trigger_error)
        central_layout.addWidget(error_button)

        # Set central widget
        main_layout.addWidget(central_widget)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def trigger_error(self):
        # Show the notification area if hidden
        self.notification_area.setVisible(True)
        # Add error messages (one short, one long)
        self.notification_area.add_error("An error occurred! Please try again.")
        self.notification_area.add_error(
            "A very long error message that exceeds the maximum height of the notification box. "
            "This message demonstrates how scrolling works within the error box, ensuring that "
            "the user interface remains compact and visually appealing."
        )


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
