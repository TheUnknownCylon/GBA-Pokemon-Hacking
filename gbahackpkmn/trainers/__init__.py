from gbahack.gbabin.bytes import ByteArrayReader

from gbahack import Resource
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT
from gbahackpkmn.strings import PokeString

from gbahackpkmn.trainers.trainerclasses import TrainerClasses

from gbahack.sprites import readCompressedSprite, toPNG
from gbahack.tools.lzss import decompress_bytes
from gbahack.palettes import Palette16

from gbahack.gbabin import BBlock

class Trainers():
    def __init__(self, rom):
        self.rom = rom
        self.trainerstable = rom.metadata['trainerstable']
        self.trainerclasses = TrainerClasses(rom)


    def getSprite(self, spriteid):
        return TrainerSprite(self.rom, spriteid)
    

    def getTrainerClasses(self):
        return self.trainerclasses
    
        
    def getTrainer(self, index):
        '''Returns a Trainer resource from ROM.'''
        traineroffset = self.trainerstable + index * Trainer.size()
        return traineroffset, self.rom.getRM().get(Trainer, traineroffset)



class TrainerPokemon(Resource):
    name = 'trainerpokemon'
    
    def __init__(self):
        self.ailevel = 0
        self.level   = 0
        self.species = 0
        self.item    = None
        
        self.move1   = None
        self.move2   = None
        self.move3   = None
        self.move4   = None

    def readPkmndata(self, rom, offset):
        p = offset
        p, self.ailevel = rom.readByte(p)
        p, _            = rom.readByte(p)
        p, self.level   = rom.readByte(p)
        p, _            = rom.readByte(p)
        p, self.species = rom.readShort(p)
        return p
    
    def readItem(self, rom, offset):
        p, self.item = rom.readShort(offset)
        if self.item == 0: self.item = None
        return p
     
    def readMoves(self, rom, offset):
        p, self.move1 = rom.readShort(offset)
        p, self.move2 = rom.readShort(p)
        p, self.move3 = rom.readShort(p)
        p, self.move4 = rom.readShort(p)
        
        if self.move1 == 0: self.move1 = None
        if self.move2 == 0: self.move2 = None
        if self.move3 == 0: self.move3 = None
        if self.move4 == 0: self.move4 = None
        return p
    
    def _bytestring(self, item=False, moves=False):
        bblock = BBlock()
        bblock.addByte(self.ailevel)
        bblock.addByte(0)
        bblock.addByte(self.level)
        bblock.addByte(0)
        bblock.addShort(self.species)
        if not item and not moves:
            bblock.addShort(0)
        elif item and not moves:
            bblock.addShort(self.item or 0)
        else:
            if item:
                bblock.addShort(self.item or 0)
            bblock.addShort(self.move1 or 0)
            bblock.addShort(self.move2 or 0)
            bblock.addShort(self.move3 or 0)
            bblock.addShort(self.move3 or 0)
            if not item:
                bblock.addShort(0)
        return bblock.toArray()


class TrainerPokemonWithItem(TrainerPokemon):
    @classmethod
    def read(cls, rom, offset):
        poke = cls()
        p = poke.readPkmndata(rom, offset)
        p = poke.readItem(rom, p)
        return poke
    
    @staticmethod
    def size():
        return 8

    @staticmethod
    def getBattlePokemonClass():
        return 2
    
    def bytestring(self):
        return self._bytestring(item=True, moves=False)
    

class TrainerPokemonWithMoveset(TrainerPokemon):
    @classmethod
    def read(cls, rom, offset):
        poke = cls()
        p = poke.readPkmndata(rom, offset)
        p = poke.readMoves(rom, p)
        return poke
    
    @staticmethod
    def size():
        return 16

    @staticmethod
    def getBattlePokemonClass():
        return 1
    
    def bytestring(self):
        return self._bytestring(item=False, moves=True)
    

class TrainerPokemonWithItemMoveset(TrainerPokemonWithMoveset):
    @classmethod
    def read(cls, rom, offset):
        poke = cls()
        p = poke.readPkmndata(rom, offset)
        p = poke.readItem(rom, p)
        p = poke.readMoves(rom, p)
        return poke

    @staticmethod
    def getBattlePokemonClass():
        return 3
    
    def bytestring(self):
        return self._bytestring(item=True, moves=True)
    

class Trainer(DataStruct):
    '''Data structure defining a Pokemon Trainer.'''
    name = 'trainer'
    
    fields = [
        (RT.byte, "battlepokemonclass"),  #values 0-4, all pokemon have:
                                          #0: no item / default moveset
                                          #1: no item / custom moveset
                                          #2: item    / default moveset
                                          #3: item    / custom moveset
        (RT.byte, "trainerclass"),
        (RT.byte, "song_genderibtmap"), #Leftmost byte: gener, rest: songid
        (RT.byte, "trainerspriteid"),
        
        (RT.bytestr(12, 0xFF), "namebytes"),
        
        (RT.short, "item1"),
        (RT.short, "item2"),
        (RT.short, "item3"),
        (RT.short, "item4"),
        
        (RT.byte, "doublebattle"),  #0: no, 1: yes
        (RT.byte, "unknown2a"),
        (RT.short, "unknown2b"),
        
        (RT.int, "unknown3"),
        
        (RT.byte, "numberofpokemon"),
        (RT.byte, "unknown4a"),
        (RT.short, "unknown4b"),
        
        (RT.pointer, "pointertopokemondefs")
        ]
        
    
    @staticmethod
    def getPokemonClassByClassID(battlepokemonclass):
        pokeclass = TrainerPokemonWithItem
        if battlepokemonclass == 1:
            pokeclass = TrainerPokemonWithMoveset
        if battlepokemonclass == 3:
            pokeclass = TrainerPokemonWithItemMoveset
        return pokeclass
    
    
    @classmethod
    def read(cls, rom, pointer):
        '''Extends the original read function,
        for this trainer class, also its battle pokemon are loaded.'''
        s = super().read(rom, pointer)
        s.pokeclass = cls.getPokemonClassByClassID(s.battlepokemonclass)
        
        s.battlepokemon = []
        for i in range(0, s.numberofpokemon):
            poke = rom.getRM().get(s.pokeclass, s.pointertopokemondefs + i * s.pokeclass.size())
            s.battlepokemon.append(poke)
            
        s.trainersprite = TrainerSprite(rom, s.trainerspriteid)
        return s
    
    
    @classmethod
    def delete(self, rom, pointer):
        '''Removes the trainer and its battle Pokemon from the ROM.'''
        oldtrainer = super().delete(rom, pointer)
        for i in range(0, len(oldtrainer.battlepokemon)):
            pkmn = oldtrainer.battlepokemon[i]
            pkmn.delete(rom, oldtrainer.pointertopokemondefs+i*pkmn.size())
        return oldtrainer
        
        
    def write(self, rom, pointer, force):
        '''Writes the trainer resource to rom, and also the trainers battle pokemon.'''
        #First write the trainer its pokeys, next write the trainer itself with
        # a pointer to the trainers pokemon.
        pkmnsize = self.getPokemonClassByClassID(self.battlepokemonclass).size()
        pkmnoffset = rom.findSpace(self.pointertopokemondefs or 0x080000, pkmnsize * self.numberofpokemon)
        
        for i in range(0, self.numberofpokemon):
            self.battlepokemon[i].write(rom, pkmnoffset+i*pkmnsize, force=True)        
        self.pointertopokemondefs = pkmnoffset
        super().write(rom, pointer, force)
        
        
    def getName(self):
        '''Returns the trainer name as a PokeString resource.'''
        return PokeString.frombytes(self.get('namebytes'))
    
    
    def setName(self, pokestr):
        self.namebytes = pokestr.bytestring()
        
    
    def getSong(self):
        '''Returns the battle song for this trainer battle.'''
        return 0b01111111 & self.song_genderibtmap
        
        
    def setSong(self, songid):
        '''Sets a song ID for the battle, note that songid < 0x80.'''
        if self.isMale():
            self.song_genderibtmap = songid
        else:
            self.song_genderibtmap = 0x80+songid
        
        
    def isMale(self):
        '''Returns true if the trainer gender is male, False if trainer is female.'''
        return 0b10000000 & self.song_genderibtmap == 0
    
    
    def setMale(self, value):
        '''Sets the male value. Set value to False for Female gender.'''
        print("_------_>> "+repr(value))
        if value == False:
            genderbyte = 0x80
        else:
            genderbyte = 0
        self.song_genderibtmap = genderbyte + self.getSong()


    def getBattlePokemon(self):
        '''Returns a BattlePokemon structue.
        The pokemon_index should be <= numberofpokemon'''
        return self.battlepokemon
    
    
    def customMoves(self):
        return self.battlepokemonclass & 1
    
    
    def getSprite(self, f):
        return self.sprite.toPNG()
    
    def setBattlePokemon(self, pokemon):
        '''
        Sets the players its battle pokemon, all pokemon should be of the same
        TrainerPokemon subclass, otherwise an exception is raised. The list
        should contain at least one Pokemon.
        '''
        if len(pokemon) < 1:
            raise Exception("Empty PokemonList! Can not save.")
        
        #Set the correct pokemonclass, verify all pokes to match this class.
        self.battlepokemonclass = pokemon[0].getBattlePokemonClass()
        for singlepokemon in pokemon:
            if singlepokemon.getBattlePokemonClass() != self.battlepokemonclass:
                raise Exception("All Pokemon should be of same BattlePokemon class!")
        
        self.battlepokemon = pokemon
        self.numberofpokemon = len(pokemon)
        
        
class TrainerSprite():
    def __init__(self, rom, trainerspriteid):
        md = rom.metadata
        _, spritepointer = rom.readPointer(md['table_trainer_sprites'] + 8 * trainerspriteid)
        _, palpointer = rom.readPointer(md['table_trainer_palettes'] + 8 * trainerspriteid)
        
        palettebytes = decompress_bytes(rom.bytes[palpointer:])
        self.palette = Palette16.read(ByteArrayReader(palettebytes), 0)
        self.sprite = readCompressedSprite(rom, spritepointer, 64, 64)
        
        
    def toPNG(self, f):
        return toPNG(f, self.sprite, self.palette)
    
    