
from gbahackpkmn.trainers import TrainerPokemon
from gbapkmneditor.trainers.views import TrainerEditor
from gbahackpkmn.strings import PokeString


class Controller():
    def __init__(self, rom, config):
        singletrainer = TrainerEditorController(rom, 0x79)

        mainview = singletrainer.getView()
        mainview.move(300, 150)
        mainview.setWindowTitle('Pokemon Trainer Editor')    
        mainview.show()
        
        
class TrainerEditorController():
    '''
    Does not provide save / undo actions.
    '''
    def __init__(self, rom, trainerid):
        self.rom = rom
        
        trainers = rom.trainers
        traineroffset, trainer = trainers.getTrainer(trainerid)
        
        trainersinfo = rom.trainers
        movenames = rom.movesdata.names().getAllDecoded()
        itemnames = rom.itemsdata.namesList()
        trainerclasses = rom.trainers.getTrainerClasses().names().getAllDecoded()
        
        movenames[0] = "None"
        itemnames[0] = "None"
        
        battlepokes = trainer.getBattlePokemon()
        for i in range(0, 6):
            if i >= len(battlepokes):
                battlepokes.append(TrainerPokemon())
        
        self.trainer = trainer
        self.traineroffset = traineroffset
        self.mainview = TrainerEditor(self, trainersinfo, trainer, battlepokes, rom.pokemondata, movenames, itemnames, trainerclasses)
        
    
    def save(self, name, ismale, trainerclass, trainersprite, songid,
            item1, item2, item3, item4, doublebattle, pokes):
        self.trainer.setName(PokeString(name))
        self.trainer.setSong(songid)
        self.trainer.setMale(ismale)
        self.trainer.trainerclass = trainerclass
        self.trainer.trainerspriteid = trainersprite
        self.trainer.doublebattle = doublebattle
        self.trainer.item1 = item1
        self.trainer.item2 = item2
        self.trainer.item3 = item3
        self.trainer.item4 = item4
        self.trainer.setBattlePokemon(pokes)

        self.trainer.update(self.rom, self.traineroffset)
    
    
    def getView(self):
        return self.mainview
    
    