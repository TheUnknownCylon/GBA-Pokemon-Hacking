
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QWidget, QScrollArea, QPixmap, QCheckBox, QLineEdit, QSizePolicy, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSpinBox, QLineEdit, QFormLayout

import tempfile
(_, tmpfilename) = tempfile.mkstemp()

class TrainerEditor(QWidget):
    '''
    Trainer editor widget.
    Holds a widget where the trainer settings can be changed,
    and holds 6 Pokemon edit widgets.
    '''
    
    def __init__(self, callback, trainersinfo, trainer, battlepokemon, pokemondata, movelist, itemslist, trainerclasses):
        super().__init__()
        self.callback = callback
        self.trainer = trainer
        self.pokemonwidgets = []
        self.pokemondata = pokemondata
        self.movelist = movelist
        self.itemslist = itemslist
        self.trainer = trainer
        self.trainersinfo = trainersinfo
        self.trainerclasses = trainerclasses
        self.initUI(battlepokemon)
        
    def initUI(self, battlepokemon):
        
        #Create a layout in which we will place a scrollable view
        # In this scrollable pane, the trainer and its pokemon are placed.
        # For smaller windows, all pokemon can be editted by scrolling from left to right.
        mainlayout = QVBoxLayout(self)
        scrollArea = QScrollArea()
        innerwidget = QWidget()

        #Create a layout for the innerwidget
        layout = QHBoxLayout()
        innerwidget.setLayout(layout)
        
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.setContentsMargins(0,0,0,0)
       
        for battlepoke in battlepokemon:
            pokewidget = TrainerPokemon(self, battlepoke, self.pokemondata, self.movelist, self.itemslist, parent=self)
            self.pokemonwidgets.append(pokewidget)
            layout.addWidget(pokewidget, 0)

        trainerinfo = Trainer(self, self.trainersinfo, self.trainer, self.trainerclasses, self.itemslist)
        layout.insertWidget(0, trainerinfo, 0)
        
        padlabel = QLabel(self)
        layout.addWidget(padlabel)
        
        scrollArea.setWidget(innerwidget)
        mainlayout.addWidget(scrollArea)
        
    def movesEnabled(self):
        return False #TODO TODO TODO!!!
        
        
    def setMovesSelectable(self, bool_selectable):
        for pkmnwidget in self.pokemonwidgets:
            pkmnwidget.setMovesEnabled(bool_selectable)
        
    
class Trainer(QWidget):
    def __init__(self, trainereditor, trainersinfo, trainer, trainerclasses, itemslist):
        super().__init__()
        self.trainereditor = trainereditor
        self.trainer  = trainer
        self.trainersinfo = trainersinfo
        self.trainerclasses = trainerclasses
        self.itemslist = itemslist
        self.initUI()
        
        
    def initUI(self):
        self.setMinimumSize(QSize(150, 450))
        self.setMaximumSize(QSize(150, 450))
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        #Create widgets
        l_sprite       = QLabel(self)
        i_sprite       = QSpinBox(self)
        i_trainerclass = QComboBox(self)
        i_name         = QLineEdit(self)
        l_songid       = QLabel("Song:", self)
        i_songid       = QSpinBox(self)
        i_doublebattle = QCheckBox("Double battle", self)
        i_choosemoves  = QCheckBox("Explicit movesets", self)
        l_items        = QLabel("Items:")
        i_item1        = QComboBox(self)
        i_item2        = QComboBox(self)
        i_item3        = QComboBox(self)
        i_item4        = QComboBox(self)

        
        #fill lists, set ranges values
        i_sprite.setRange(0, 255)
        i_songid.setRange(0, 0b01111111)
        i_trainerclass.addItems(self.trainerclasses)
        l_sprite.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        l_sprite.setMinimumSize(120, 64);
        l_sprite.setAlignment(Qt.AlignCenter)
        i_item1.addItems(self.itemslist)
        i_item2.addItems(self.itemslist)
        i_item3.addItems(self.itemslist)
        i_item4.addItems(self.itemslist)
        
        
        #Set fields according to the trainer object
        i_sprite.setValue(self.trainer.trainerspriteid)
        i_name.setText(self.trainer.getName().getText())
        i_songid.setValue(self.trainer.getSong())
        i_trainerclass.setCurrentIndex(self.trainer.trainerclass)
        i_doublebattle.setChecked(self.trainer.doublebattle)
        i_choosemoves.setChecked(self.trainer.customMoves())
        i_item1.setCurrentIndex(self.trainer.item1)
        i_item2.setCurrentIndex(self.trainer.item2)
        i_item3.setCurrentIndex(self.trainer.item3)
        i_item4.setCurrentIndex(self.trainer.item4)
        
        #Add all to layout
        layout.addWidget(l_sprite)
        layout.addWidget(i_sprite)
        layout.addWidget(i_trainerclass)
        layout.addWidget(i_name)
        layout.addWidget(l_songid)
        layout.addWidget(i_songid)
        layout.addWidget(i_doublebattle)
        layout.addWidget(i_choosemoves)
        layout.addWidget(l_items)
        layout.addWidget(i_item1)
        layout.addWidget(i_item2)
        layout.addWidget(i_item3)
        layout.addWidget(i_item4)
        
        #Connect to signals
        i_sprite.valueChanged.connect(self.updateSprite)
        i_choosemoves.stateChanged.connect(self.chooseMovesChanged)
        
        #Keep values for future refs
        self.l_sprite = l_sprite
        self.i_sprite = i_sprite
        
        self.updateSprite()
        self.chooseMovesChanged(i_choosemoves.checkState())
        
        
    def updateSprite(self):
        pokeid = self.i_sprite.value()
        f = open(tmpfilename, 'wb')
        self.trainersinfo.getSprite(pokeid).toPNG(f)
        f.close()
                    
        image = QPixmap(tmpfilename)
        self.l_sprite.setPixmap(image)
        
        
    def chooseMovesChanged(self, value):
        self.trainereditor.setMovesSelectable(value > 0)


class TrainerPokemon(QWidget):
    '''
    Trainers Pokemon edit widget.
    Vertically aligned pokemon editor:
        [ IMAGE of SPRITE   ]
        [ SPECIES SELECTBOX ] [Level NUM]
        @ [ ITEM SELECTBOX  ]
        Difficulty: [ AI Level NUMFIELD]
        ----
        Moves (greyed out if default):
        Move 1: [MOVE 1]
        Move 2: [MOVE 2]
        Move 3: [MOVE 3]
        Move 4: [MOVE 4]
        
    Moves are selectable by default.
    '''
    
    def __init__(self, trainereditor, trainerpokemon, pokemondata, moveslist, itemslist, parent=None):
        '''
        Takes a trainerpokemon resource object, which
        will be updated if the user changes some info in this widget.
        
        Pokemondata is a PokemonData object.
        Moveslist is a list of all move names (strings)
        Itemslist is a list of all item names (strings)
        '''
        super().__init__(parent)
        self.trainereditor = trainereditor
        self.pokemon = trainerpokemon
        self.pokemondata = pokemondata
        pokenames = pokemondata.names().getAllDecoded()
        pokenames[0] = "None"
        self.initUI(pokenames, moveslist, itemslist)


    def initUI(self, pokemonlist, moveslist, itemslist):
        
        self.setMinimumSize(QSize(150, 450))
        self.setMaximumSize(QSize(150, 450))
        layout = QVBoxLayout(self)
        
        #TODO sprite
        l_sprite  = QLabel(self)
        i_species = QComboBox(self)
        l_item    = QLabel("@", self)
        i_item    = QComboBox(self)
        
        l_level   = QLabel("Level:", self)
        i_level   = QSpinBox(self)
        
        l_ailevel = QLabel("Difficulty:", self)
        i_ailevel = QSpinBox(self)

        l_moves   = QLabel("Moves:", self)
        i_move1   = QComboBox(self)
        i_move2   = QComboBox(self)
        i_move3   = QComboBox(self)
        i_move4   = QComboBox(self)
        
        
        #fill lists, set ranges values
        l_sprite.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        l_sprite.setMinimumSize(120, 64);
        l_sprite.setAlignment(Qt.AlignCenter)
        i_level.setRange(1, 100)
        i_ailevel.setRange(0, 255)

        i_species.addItems(pokemonlist)
        i_item.addItems(itemslist)
        i_move1.addItems(moveslist)
        i_move2.addItems(moveslist)
        i_move3.addItems(moveslist)
        i_move4.addItems(moveslist)


        #set values to match the read pokemon
        i_level.setValue(self.pokemon.level or 0)
        i_ailevel.setValue(self.pokemon.ailevel or 0)
        i_species.setCurrentIndex(self.pokemon.species or 0)
        i_item.setCurrentIndex(self.pokemon.item or 0)
        i_move1.setCurrentIndex(self.pokemon.move1 or 0)
        i_move2.setCurrentIndex(self.pokemon.move2 or 0)
        i_move3.setCurrentIndex(self.pokemon.move3 or 0)
        i_move4.setCurrentIndex(self.pokemon.move4 or 0)
        
        
        #Add all to the layout
        layout.addWidget(l_sprite)

        layout.addWidget(i_species)
        layout.addWidget(l_level)
        layout.addWidget(i_level)
        layout.addWidget(l_item)
        layout.addWidget(i_item)
        layout.addWidget(l_ailevel)
        layout.addWidget(i_ailevel)
        layout.addWidget(l_moves)
        layout.addWidget(i_move1)
        layout.addWidget(i_move2)
        layout.addWidget(i_move3)
        layout.addWidget(i_move4)

        
        #Connect to actions
        i_species.currentIndexChanged.connect(self.speciesChanged)
        
        
        #Store refs for later use
        self.i_species = i_species
        self.l_sprite  = l_sprite
        self.i_level   = i_level
        self.i_ailevel = i_ailevel
        self.i_item    = i_item
        self.i_move1   = i_move1
        self.i_move2   = i_move2
        self.i_move3   = i_move3
        self.i_move4   = i_move4
        
        self.speciesChanged()
    
    
    def setMovesEnabled(self, boolval):
        #Don't accedently enable moves if we are disabled.
        if self.i_species.currentIndex() == 0 or self.trainereditor.movesEnabled() == False:
            boolval = False
            
        self.i_move1.setEnabled(boolval)
        self.i_move2.setEnabled(boolval)
        self.i_move3.setEnabled(boolval)
        self.i_move4.setEnabled(boolval)
    
        if boolval == False:
            self.i_move1.setCurrentIndex(0)
            self.i_move2.setCurrentIndex(0)
            self.i_move3.setCurrentIndex(0)
            self.i_move4.setCurrentIndex(0)
    
    
    def speciesChanged(self):
        pokeid = self.i_species.currentIndex()

        self.updateSprite(pokeid)
        if pokeid == 0:
            self.setMovesEnabled(False)
            self.i_item.setCurrentIndex(0)
            self.i_level.setValue(0)
            self.i_ailevel.setValue(0)
            
            self.i_level.setEnabled(False)
            self.i_ailevel.setEnabled(False)
            self.i_item.setEnabled(False)
        else:
            self.setMovesEnabled(True)
            self.i_level.setEnabled(True)
            self.i_ailevel.setEnabled(True)
            self.i_item.setEnabled(True)    
    
    def updateSprite(self, pokeid):
        f = open(tmpfilename, 'wb')
        self.pokemondata.getSprite(pokeid).toPNG(f)
        f.close()
                    
        image = QPixmap(tmpfilename)
        self.l_sprite.setPixmap(image)
        
        