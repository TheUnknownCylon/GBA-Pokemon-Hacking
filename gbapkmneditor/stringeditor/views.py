
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QWidget, QVBoxLayout, QSplitter, QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QFont, QFormLayout

from gbapkmneditor.gui import LNTextEdit
from gbapkmneditor.gui.messages import showYesNo, showInfo
from gbahackpkmn.pokescript.ast import ASTResourceString

inputlabeltext = '''Please enter <b>the first part</b> of the text you want to search for.'''
resultslabeltext = '''The following matches were found, (click on a match to edit it):'''
findstartpointtext = '''It seems that the startpoint of this text is not valid, since there are no pointers to the text. Click this button if you would like to search for a start point.'''

class MainView(QWidget):
    '''Simple one column widget containing a search, and select part.'''
    def __init__(self, callback, scripteditcontroller):
        super(MainView, self).__init__()
        self._callback = callback
        self.scripteditcontroller = scripteditcontroller
        self.initUI()
        
        #Keep track of all selectable result items
        self.selectableitems = {}
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        #Input part
        input_label = QLabel(inputlabeltext, self)
        input_label.setWordWrap(True)
        input_field = QLineEdit("MOM: Oh, good!", self)
        input_search = QPushButton("Search!", self)
        
        splitview = QSplitter(self)
        splitview.setOrientation(Qt.Vertical)
        splitview.setChildrenCollapsible(False)
        
        #Results list
        results_label = QLabel(resultslabeltext, self)
        results_label.setWordWrap(True)
        results_list = QTreeWidget()
        results_list.setColumnCount(3) #pointer, refs to pointer, text
        results_list.header().resizeSection(0, 100)
        results_list.header().resizeSection(1, 40)
        results_list.setFocusPolicy(Qt.NoFocus)
        #results_list.setMaximumSize(QSize(16777215, 100))

        stringeditor = self.scripteditcontroller.getview()
        
        #Pack all into the layout
        layout.addWidget(input_label)
        layout.addWidget(input_field)
        layout.addWidget(input_search)
        
        layout.addWidget(results_label)
        #layout.addWidget(results_list)
        #layout.addWidget(stringeditor)
        splitview.addWidget(results_list)
        splitview.addWidget(stringeditor)
        splitview.setSizes([100, 500])
        layout.addWidget(splitview)

        #Connect to actions
        input_search.clicked.connect(self.searchClick)
        results_list.itemSelectionChanged.connect(self.resultSelected)
        
        #Keeps some elements for later use
        self.input_field = input_field
        self.results_list = results_list
        self.stringeditor = stringeditor
        
        #Show the widget
        self.move(300, 150)
        self.setWindowTitle('Pokemon GBA String Editor')    
        self.show()
        
    
    def searchClick(self, button):
        self._callback.search(self.input_field.text())
        
        
    def resultSelected(self):
        selected = self.results_list.selectedItems()[0]
        pointer = selected.data(0, Qt.UserRole)
        self._callback.stringselected(pointer)
        
        
    def setResults(self, results_list):
        self.results_list.clear()
        self.selectableitems = {}
        for (pointer, count, pokestring) in results_list:
            p = QTreeWidgetItem(['%X'%pointer, repr(count), pokestring.getText()])
            p.setData(0, Qt.UserRole, pointer)
            #self.selectableitems[p] = pointer
            self.results_list.addTopLevelItem(p)


    def stringselected(self, pokestring):
        self.stringeditor.setString(pokestring)
        

        
class StringEditorView(QWidget):
    '''This widget contains the StringEdit field.'''
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        
        self.offset = 0         # Offset of currently oaded script
        self.pointerscount = 0  # Number of pointers to the offset
        self.oldsize = 0        # Old size of currently loaded bytestring.
        self.freespace = 0      # Free space available after currently loaded bytestring.
                
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        formlayout = QFormLayout()
        label_charscount = QLabel()
        label_offset = QLabel()
        label_pointersToOffset = QLabel()
        formlayout.addRow("Used / Maximum number of chars:", label_charscount)
        formlayout.addRow("String offset:", label_offset)
        formlayout.addRow("Pointers to offset:", label_pointersToOffset)
        
        find_startpoint = QPushButton("Try to find start of string.", self)
        find_startpoint.hide()
        editor_save = QPushButton("Save", self)
        editor_save_repoint = QPushButton("Save and update pointers.", self)
        editor_save_repoint.hide()
        
        stringeditor = LNTextEdit(self)
        font = QFont("Monospace");
        font.setStyleHint(QFont.TypeWriter);
        stringeditor.setFont(font)
        
        layout.addWidget(stringeditor)
        layout.addLayout(formlayout)
        layout.addWidget(find_startpoint)
        layout.addWidget(editor_save)
        layout.addWidget(editor_save_repoint)

        #self.label_totalchars = label_totalchars
        self.stringeditor = stringeditor
        self.label_charscount = label_charscount
        self.label_offset = label_offset
        self.label_pointersToOffset = label_pointersToOffset
        self.editor_save = editor_save
        self.find_startpoint = find_startpoint
        self.editor_save_repoint = editor_save_repoint
        
        stringeditor.edit.textChanged.connect(self.updateUI)
        find_startpoint.clicked.connect(self.findStartpoint)
        editor_save.clicked.connect(self.save)
        editor_save_repoint.clicked.connect(self.saveandrepoint)
        
        self.updateUI()
        

    def setString(self, offset, pokestringresource):
        '''Set the String, string is formatted as if it was PokeScript.'''
        thetext = ASTResourceString("", pokestringresource).text("", False)
        self.label_offset.setText("0x%X"%offset)
        self.offset = offset
        
        pointerscount = self.callback.getNumberOfPointers(offset)
        self.pointerscount = pointerscount
        self.label_pointersToOffset.setText("%d"%pointerscount)
        self.find_startpoint.setVisible(pointerscount==0)
        self.find_startpoint.setEnabled(pointerscount==0)
        
        strlength = len(pokestringresource.bytestring())
        #Possibly, there is additional free space at the end of the String
        self.oldsize = strlength - 1 #Remove the end of sequence byte
        self.freespace = self.callback.freespace(offset+strlength)
        
        self.stringeditor.setText(thetext)
        self.updateUI()
    
    
    def updateUI(self):
        r = self.callback.compilestring(self.stringeditor.edit.toPlainText())

        l_cur = len(r.bytestring()) - 1 #-1 for the end of sequence byte
        l_old = self.oldsize
        l_free = self.freespace
        l_max = l_old + l_free
        self.label_charscount.setText("%d / %d (%d old size + %d free space)."%(l_cur, l_max, l_old, l_free))
        
        self.editor_save.setEnabled(l_cur <= l_max)
        self.editor_save_repoint.setVisible(l_cur > l_max)
        self.editor_save_repoint.setEnabled(l_cur > l_max and self.pointerscount > 0)

    
    def findStartpoint(self, button):
        #User want to find a/the start point for this string
        self.callback.findStartpoint(self.offset)
        
        
    def save(self, button):
        #The user wants to save the script, is it wise? If yes: save...
        r = self.callback.compilestring(self.stringeditor.edit.toPlainText())
        if self.pointerscount == 0 and len(r.bytestring()) != self.oldsize+1:
            if not showYesNo(self, "There are no pointers to this text. Updating the text with a new one of a different length may lead to data corruption. Are you sure you want to continue?", "Warning!"):
                return
        
        newpointer = self.callback.save(self.offset, r)
        showInfo(self, "Saved string at 0x%X."%newpointer)

    
    def saveandrepoint(self, button):
        #The user wants to save, but there is no space
        # -> Save and repoint.
        r = self.callback.compilestring(self.stringeditor.edit.toPlainText())
        newpointer = self.callback.saveandrepoint(self.offset, r)
        showInfo(self, "Saved string at 0x%X, updated all pointers to this text."%newpointer)
        self.callback.selectString(newpointer)
    
    