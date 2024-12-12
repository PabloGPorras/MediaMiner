from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QPoint

class NotificationOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 204, 204, 200); border: 1px solid red;")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)  # Reduce spacing between notifications
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)

    def add_error(self, error_message):
        # Create a container for each error
        error_container = QWidget()
        error_container.setStyleSheet(
            "background-color: #ffeeee; border: 1px solid red; padding: 5px; border-radius: 5px;"
        )
        error_layout = QVBoxLayout()
        error_layout.setSpacing(1)
        error_layout.setContentsMargins(5, 5, 5, 5)
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

        # Close button to remove this specific error
        close_button = QPushButton("✖")
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent; 
                color: red; 
                font-weight: bold; 
                border: none; 
                font-size: 14px;
            }
            QPushButton:hover {
                color: darkred;
            }
            """
        )
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(lambda: self._remove_error(error_container))
        error_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add the container to the main layout
        self.layout.addWidget(error_container)

    def _remove_error(self, container):
        """Remove a single error notification."""
        self.layout.removeWidget(container)
        container.deleteLater()

    def clear_all_errors(self):
        """Clear all notifications."""
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error Notification Example")
        self.setGeometry(100, 100, 800, 600)

        # Central content
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        # Button to trigger errors
        error_button = QPushButton("Trigger Error")
        error_button.clicked.connect(self.trigger_error)
        central_layout.addWidget(error_button)

        self.setCentralWidget(central_widget)

        # Notification overlay
        self.notification_overlay = NotificationOverlay(self)
        self.notification_overlay.setGeometry(50, 50, 400, 200)  # Adjust initial position and size
        self.notification_overlay.hide()

    def trigger_error(self):
        # Show the notification overlay
        self.notification_overlay.show()
        self.notification_overlay.add_error(
            "A very long error message that demonstrates the overlay functionality. "
            "You can add multiple errors, and they will appear here."
        )
        self.notification_overlay.add_error("A short error occurred.")

        # Auto-hide overlay after 5 seconds (optional)
        QTimer.singleShot(5000, self.notification_overlay.hide)

    def moveEvent(self, event):
        """Reposition the notification overlay when the main window is moved."""
        super().moveEvent(event)
        if self.notification_overlay.isVisible():
            # Update the position of the overlay relative to the main window
            overlay_pos = self.geometry().topLeft() + QPoint(50, 50)  # Offset from the main window
            self.notification_overlay.move(overlay_pos)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
