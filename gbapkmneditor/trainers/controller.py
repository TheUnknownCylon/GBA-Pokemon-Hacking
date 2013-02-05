
from gbahackpkmn.trainers import Trainers, TrainerPokemon
from gbahackpkmn.trainers.trainerclasses import TrainerClasses
from gbapkmneditor.trainers.views import TrainerEditor


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
        trainers = rom.trainers
        trainer = trainers.getTrainer(trainerid)
        
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
        
        self.mainview = TrainerEditor(self, trainersinfo, trainer, battlepokes, rom.pokemondata, movenames, itemnames, trainerclasses)
        
        
    def getView(self):
        return self.mainview
    
    