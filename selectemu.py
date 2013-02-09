#!/usr/bin/python
'''
This pointless tool helps the user select an emulator.
'''
import sys
from PyQt4.QtGui import QApplication, QFileDialog, QMessageBox, QInputDialog, QLineEdit

title = "Emulator Selection Tool"

app = QApplication(sys.argv)
QMessageBox.warning(None, title, "Please select your emulator of choise now.")
filename = QFileDialog.getOpenFileName(caption='Emulator Selection Tool', filter='All Files (*.*)')
path = filename + " %u"
output, ok = QInputDialog.getText(None, title, "So... this is what I recommend you to use, but you can change the command now if you wish.\nNote: %u is replaced by the rom its name!", QLineEdit.Normal, path)
if ok:
    try:
        QMessageBox.warning(None, title, "Thank you for using this tool. . ..")
        f = open("config.txt", 'w')
        f.write("emulator=%s"%output)
        f.close()
    except Exception as e:
        QMessageBox.warning(None, title, "Something went wrong!")
        raise e
else:
    QMessageBox.warning(None, title, "You hit cancel!")