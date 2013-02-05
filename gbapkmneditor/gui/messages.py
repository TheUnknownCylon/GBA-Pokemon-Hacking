import sys
from PyQt4.QtGui import QFileDialog, QMessageBox

def showError(w, message, title="Error", quit=False):
    QMessageBox.warning(w, "Error", message)
    if quit:
        sys.exit(0)

def showInfo(w, message):
    QMessageBox.warning(w, "Information", message) 

def showYesNo(w, message, title="Question"):
    reply = QMessageBox.question(w, title, message,
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    return reply == QMessageBox.Yes