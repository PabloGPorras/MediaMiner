from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #ffcccc; border: 1px solid red; padding: 5px;")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMinimumHeight(50)

    def add_error(self, error_message):
        # Create a container for each error
        error_container = QWidget()
        error_container.setStyleSheet("border-bottom: 1px solid red; padding: 5px;")
        error_layout = QHBoxLayout()
        error_container.setLayout(error_layout)

        # Error label
        error_label = QLabel(error_message)
        error_label.setStyleSheet("color: red; font-size: 14px;")
        error_label.setWordWrap(True)
        error_layout.addWidget(error_label)

        # Close button
        close_button = QPushButton("✖")
        close_button.setStyleSheet(
            "background-color: transparent; color: red; font-weight: bold; border: none; padding: 0 5px;"
        )
        close_button.clicked.connect(lambda: self._remove_error(error_container))
        error_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Add the container to the main layout
        self.layout.addWidget(error_container)

    def _remove_error(self, container):
        self.layout.removeWidget(container)
        container.deleteLater()


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
        # Add an error message
        self.notification_area.add_error("An error occurred! Please try again.")
        self.notification_area.add_error("Another issue occurred! Check your input.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
