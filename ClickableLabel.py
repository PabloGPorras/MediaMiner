from PyQt6.QtWidgets import QApplication, QLabel

class ClickableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        self.close()  # Close the label on click
        super().mousePressEvent(event)

# Example usage
app = QApplication([])
label = ClickableLabel("Click me to close")
label.show()
app.exec()
