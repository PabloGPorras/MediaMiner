from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QPoint

class NotificationOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 204, 204, 200); border: 1px solid red; padding: 5px;")

        # Create a scrollable area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        # Create a widget to hold the notifications
        self.notification_widget = QWidget()
        self.notification_layout = QVBoxLayout()
        self.notification_layout.setSpacing(5)
        self.notification_layout.setContentsMargins(10, 10, 10, 10)
        self.notification_widget.setLayout(self.notification_layout)

        # Add the notification widget to the scroll area
        self.scroll_area.setWidget(self.notification_widget)

        # Main layout of the overlay
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def add_error(self, error_message):
        # Create a label for the error message
        error_label = QLabel(error_message)
        error_label.setStyleSheet(
            "background-color: #ffeeee; border: 1px solid red; padding: 5px; "
            "border-radius: 5px; color: red; font-size: 12px;"
        )
        error_label.setWordWrap(True)
        error_label.setMaximumWidth(300)  # Limit width for readability
        self.notification_layout.addWidget(error_label)

    def clear_all_errors(self):
        """Clear all notifications."""
        while self.notification_layout.count():
            widget = self.notification_layout.takeAt(0).widget()
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

        # Add multiple error messages for demonstration
        for i in range(20):  # Add 20 error messages
            self.notification_overlay.add_error(f"Error message {i + 1}")

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
