'''
This submodule contains modules that show a GUI containing some PokeHack
tools for the GBA Pokemon Games. The gbahack and gbahackpkmn python projects
are included to read/write info from/to the ROM.

The GUI relies on QT4, and therefore, PyQt4 should be installed on your system.
This tool is cross-platform, and should work on any OS that has Python and QT
support.
'''

import sys
from PyQt4.QtGui import QApplication, QFileDialog

from gbahackpkmn import ROM

from gbapkmneditor import simpleconfig
from gbapkmneditor.gui.messages import showError


def readconfig(configfile):
    '''
    Reads a config file.
    If reading the config fails, an exception is thrown.
    '''
    try:
        config = simpleconfig.getConfig(configfile)
        print("Read config from %s"%configfile)
        return config
    except Exception as e:
        print("Reading config failed. Continue with defaults.\n %s"%repr(e))
        return {}
    

class App():
    def __init__(self, controller):
        config = readconfig("config.txt")
        app = QApplication(sys.argv)
        
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = QFileDialog.getOpenFileName(caption='Select ROM', filter='GBA (*.gba);;All Files (*.*)')

        if not filename:
            print("No file was selected.")
            return

        try:
            rom = ROM(filename)
        except Exception as e:
            showError(None, "There was an error opening the ROM "+filename+":\n"+str(e))
            return
        
        controller(rom, config)
        sys.exit(app.exec_())
