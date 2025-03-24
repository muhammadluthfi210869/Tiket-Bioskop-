"""
Utility module for standardized dialog styles across the application.
"""

DIALOG_STYLESHEET = """
    QMessageBox {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid white;
    }
    QMessageBox QLabel {
        color: white;
        font-family: 'Montserrat';
    }
    QMessageBox QPushButton {
        background-color: #FFD700;
        color: black;
        border-radius: 5px;
        padding: 5px 15px;
        font-weight: bold;
        font-family: 'Montserrat';
        min-width: 80px;
    }
    QMessageBox QPushButton:hover {
        background-color: #F5CB0C;
    }
"""

def setup_message_box(msg_box, title, text, informative_text=None, icon=None):
    """Set up a QMessageBox with standardized styling."""
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    if icon:
        msg_box.setIcon(icon)
    msg_box.setStyleSheet(DIALOG_STYLESHEET)
    return msg_box 