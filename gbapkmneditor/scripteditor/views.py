
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QPushButton, QSizePolicy, QListWidget, QListWidgetItem, QIntValidator, QPixmap, QLabel, QToolBar, QHBoxLayout, QVBoxLayout, QFont, QWidget, QLineEdit, QTreeWidget, QTreeWidgetItem

from gbapkmneditor.gui import LNTextEdit

import tempfile
(_, tmpfilename) = tempfile.mkstemp()

class MainView(QWidget):
    
    def __init__(self, callback):
        super(MainView, self).__init__()
        self.callback = callback
        self.initUI()
        
    def initUI(self):
        ''' '''
        columns = QHBoxLayout()
        self.setLayout(columns)
        
        self.main = EditorControlWidget(self.callback)
        self.left = leftwidget(self.callback)

        columns.addWidget(self.left)
        columns.addWidget(self.main)
        
        self.move(300, 150)
        self.setWindowTitle('Pokemon GBA Script Editor')    
        self.show()
    
    def setScriptList(self, eventsmap):
        self.left.setScriptList(eventsmap)
    
    def getScript(self):
        return self.main.getEditor().edit.toPlainText()
        
    def setScript(self, script):
        self.main.getEditor().setText(script)
    
    def setEditor(self, widget):
        self.main.setWidget(widget)
    
    def setResoursesList(self, rlist):
        self.left.setResoursesList(rlist)
    
    
class EditorControlWidget(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.initUI()
        
    def getEditor(self):
        return self.scripteditor.getEditor()
        
        
    def initUI(self):
        
        #Main resource is the scripteditor, and is always available
        scripteditor = ScriptEditorWidget(self.callback)
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)        
        layout.addWidget(scripteditor)
        self.layout = layout
        self.scripteditor = scripteditor
    
    
    def setWidget(self, widget=None):
        if widget == None:
            widget = self.scripteditor
        
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().setParent(None)
            
        self.layout.addWidget(widget)
        
    
class ScriptEditorWidget(QWidget):
    def __init__(self, callback):
        super().__init__()
        
        self.callback = callback
        
        #Toolbar
        toolbar = QToolBar(self)
        self.button_test = toolbar.addAction("Test script")
        self.button_burn = toolbar.addAction("Write script to ROM")
        #self.button_reload = toolbar.addAction("Refresh")
        self.button_pokescriptdoc = toolbar.addAction("PokeScript doc")
        self.button_pokescriptdoc.setToolTip("Opens your webbrowser, pointing at a page where some elemnets of PokeScript are explained.")
        self.button_scriptdoc = toolbar.addAction("List of commands.")
        self.button_scriptdoc.setToolTip("Opens a list of available commands in your default browser.")
        toolbar.actionTriggered.connect(self.toolbarAction)
        
        #Code editor
        sourceeditor = LNTextEdit(self)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        sourceeditor.setFont(font)
        sourceeditor.setLineWrapMode(0)
        
        #Wrap it up
        layout = QVBoxLayout(self)
        layout.addWidget(toolbar)
        layout.addWidget(sourceeditor)
        layout.setContentsMargins(0, 0, 0, 0)
        
        #Store elements that we need later
        self.sourceeditor = sourceeditor
    
    def getEditor(self):
        return self.sourceeditor
    
    def toolbarAction(self, action):
        if action == self.button_test:
            self.callback.testScript()
        elif action == self.button_burn:
            self.callback.burnScript()
        elif action == self.button_scriptdoc:
            self.callback.showcommandslist()
        elif action == self.button_pokescriptdoc:
            self.callback.showpokescriptdoc()
        else:
            print("Unknown action.")
            


class leftwidget(QWidget):
    '''Generates the left view.'''
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setMinimumSize(QSize(210, 200))
        self.setMaximumSize(QSize(210, 16777215))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.lockresource = False

        numbervalidator = QIntValidator(0, 999)
    
        #Rom info and emulator
        emulator = QPushButton("Start Emulator", self)

    
        #Map/bank select buttons
        column_left_layout = QVBoxLayout(self)
        column_left_layout.setContentsMargins(0, 0, 0, 0);
        column_left_layout.setSpacing(2)
        mapinput_l  = QLabel('Map:', self)
        mapinput_f  = QLineEdit(self)
        mapinput_f.setValidator(numbervalidator)
        bankinput_l = QLabel('Bank:', self)
        bankinput_f = QLineEdit(self)
        bankinput_f.setValidator(numbervalidator)
        button_load = QPushButton(self)
        button_load.setText("Load scripts")
        
        #Select element on the map view
        select_script = QTreeWidget(self)
        select_script.setColumnCount(2)
        select_script.setHeaderHidden(True)
        select_script.header().resizeSection(0, 160)
        select_script.header().resizeSection(1, 20)
        select_script.setStyleSheet("outline: 0;")
        select_script.setFocusPolicy(Qt.NoFocus)

        resources_l = QLabel("Script resources:", self)
        resourceselector = QListWidget(self)
        resourceselector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        column_left_layout.addWidget(emulator)

        column_left_layout.addWidget(bankinput_l)
        column_left_layout.addWidget(bankinput_f)
        column_left_layout.addWidget(mapinput_l)
        column_left_layout.addWidget(mapinput_f)
        column_left_layout.addWidget(button_load)
        column_left_layout.addWidget(select_script)
        column_left_layout.addWidget(resources_l)
        column_left_layout.addWidget(resourceselector)
        
        #Finally connect proper signals
        button_load.clicked.connect(self.maploadclick)
        select_script.itemSelectionChanged.connect(self.itemselected)
        resourceselector.itemSelectionChanged.connect(self.resourceselected)
        emulator.clicked.connect(self.emulate)
        
        #Keep some elements for local thingy
        self.mapinput = mapinput_f
        self.bankinput = bankinput_f
        self.scriptselect = select_script
        self.resourceselector = resourceselector
        
    
    def maploadclick(self, *args, **kwargs):
        self.callback.mapchange(
            int(self.bankinput.text()),
            int(self.mapinput.text())
        )
    
    def emulate(self):
        self.callback.startEmulator()
    
    def setScriptList(self, eventsmap):
        '''EventsMap: from GbaHackPkmn'''
        self.eventsmap = eventsmap
        
        self.scriptselect.clear()
        
        self._persons = []
        self._signposts = []
        self._scripts = []
        
        #persons
        personslist = QTreeWidgetItem(['Persons'])
        self.scriptselect.addTopLevelItem(personslist)
        for i in range(0, eventsmap.getNumberOfPersons()):
            p = QTreeWidgetItem(personslist, ['Person %i'%(i+1)])
            self._persons.append(p)
            
            try:
                spriteid = eventsmap.getPerson(i).spriteid
                f = open(tmpfilename, 'wb')
                self.callback.getOverworld().getPersonSprite(spriteid).toPNG(0, f)
                f.close()
                
                image = QPixmap(tmpfilename)
                imageLabel = QLabel()
                imageLabel.setPixmap(image)
            
                self.scriptselect.setItemWidget(p, 1, imageLabel)
            except Exception as e:
                print("Could not set sprite: "+str(e))

        #Signposts
        signpostslist = QTreeWidgetItem(['Signposts'])
        for i in range(0, eventsmap.getNumberOfSigns()):
            p = QTreeWidgetItem(signpostslist, ['Signpost %i'%(i+1)])
            self._signposts.append(p)
        self.scriptselect.addTopLevelItem(signpostslist)
        
        #Scripts
        scriptlist = QTreeWidgetItem(['Scripts'])
        for i in range(0, eventsmap.getNumberOfScripts()):
            p = QTreeWidgetItem(scriptlist, ['Script %i'%(i+1)])
            self._scripts.append(p)
        self.scriptselect.addTopLevelItem(scriptlist)
        
        self.scriptselect.expandAll()
    
    
    def itemselected(self):
        selected = self.scriptselect.selectedItems()[0]
        if selected in self._persons:
            mapEvent = self.eventsmap.getPerson(self._persons.index(selected))
        elif selected in self._scripts:
            mapEvent = self.eventsmap.getScript(self._scripts.index(selected))
        elif selected in self._signposts:
            mapEvent = self.eventsmap.getSign(self._signposts.index(selected))
        else:
            return
        self.callback.mapeventselected(mapEvent)
        
    
    def setResoursesList(self, resourcelist):
        self.lockresource = True
        self.resourceselector.clear()
        self.lockresource = False
        
        item = QListWidgetItem("Script Editor")
        item.setData(Qt.UserRole, ("scripteditor", None))
        self.resourceselector.addItem(item)
        self.resourceselector.setCurrentItem(item)
        
        for resourcetype, value in resourcelist:
            if resourcetype == "trainerbattle":
                item = QListWidgetItem("Trainerbattle 0x%X"%value)
                item.setData(Qt.UserRole, (resourcetype, value))
                self.resourceselector.addItem(item)
                
    
    def resourceselected(self):
        if self.lockresource == True:
            return
        index = self.resourceselector.currentRow()
        data = self.resourceselector.item(index).data(Qt.UserRole)
        print(data)
        self.callback.resourceSelected(data)
