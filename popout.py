def loadComments(self, row):
    uniqueRef = searchTableWidgetByColumnName(self.props['parent'].tableWidget, row, 'unique_ref').text()
    if self.props['uniqueRef'] != uniqueRef:
        self.props['uniqueRef'] = uniqueRef

    if hasattr(self, 'commentScreen'):
        self.commentScreen.setParent(None)

    self.commentScreen = CommentScreen(None, self.props)

    # Create a pop-out widget as a top-level window (no parent)
    self.popout = QWidget()
    self.popout.setWindowTitle("Pop-Out Window")
    self.popout.resize(300, 200)

    # Add some content to the pop-out
    layout = QVBoxLayout(self.popout)
    layout.addWidget(QLabel("This is a pop-out widget!"))

    # Show the pop-out as a top-level window
    self.popout.show()
