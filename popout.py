from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main widget layout
        self.layout = QVBoxLayout(self)
        
        # Button to show the pop-out widget
        self.button = QPushButton("Show Pop-Out")
        self.button.clicked.connect(self.show_popout)

        # Add button to layout
        self.layout.addWidget(self.button)

    def show_popout(self):
        # Create a pop-out widget
        self.popout = QWidget()
        self.popout.setWindowTitle("Pop-Out Window")
        self.popout.resize(300, 200)
        
        # Add some content to the pop-out
        layout = QVBoxLayout(self.popout)
        label = QLabel("This is a pop-out widget!")
        layout.addWidget(label)

        # Show the pop-out as a top-level window
        self.popout.show()

if __name__ == "__main__":
    app = QApplication([])

    # Main application widget
    main_window = MainWidget()
    main_window.setWindowTitle("Main Window")
    main_window.resize(400, 300)
    main_window.show()

    app.exec()
