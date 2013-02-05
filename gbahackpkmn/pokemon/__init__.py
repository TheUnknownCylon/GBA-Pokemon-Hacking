from gbahack.gbabin.bytes import ByteArrayReader
from gbahack.sprites import readCompressedSprite, toPNG
from gbahack.tools.lzss import decompress_bytes
from gbahack.palettes import Palette16
from gbahackpkmn.strings import StringList


class PokemonData():
    
    def __init__(self, rom):
        self.rom = rom
        pokenamestable = rom.metadata['pokenamestable']
        self.numberofpokemon = rom.metadata['numpoke']
        self._names = StringList(rom, pokenamestable, 11, self.numberofpokemon)
        
        
    def getNumberOf(self):
        '''Returns the number of Pokemon in the ROM.'''
        return self.numberofpokemon
        
        
    def names(self):
        '''Returns a StringList object containing all the Pokemon names.'''
        return self._names
        
        
    def getSprite(self, pkmnid):
        return PokemonSprite(self.rom, pkmnid)
        

        
        
class PokemonSprite():
    def __init__(self, rom, pkmnid):
        #Sprites are stored in the ROM as following:
        #  Table frontsprite pointers: per pokey[pointer + 4 bytes other]
        #    pointer: lzss encoded sprite
        #  Table frontsprite tablepointer: per pokey[pointer + 4 bytes other]
        #    pointer: two lzss encrypted palettes (normal + shiny)
        #
        #  Idem for backsprites
        self.rom = rom
        md = rom.metadata
        
        #sprite pointers
        _, self.sp_front = rom.readPointer(md['table_pokemon_sprites'] + 8 * pkmnid)
        _, self.sp_back  = rom.readPointer(md['table_pokemon_sprites_back'] + 8 * pkmnid)
        
        #palette pointers
        _, self.pal_normal = rom.readPointer(md['table_pokemon_palettes'] + 8 * pkmnid)
        _, self.pal_shiny  = rom.readPointer(md['table_pokemon_palettes_shiny'] + 8 * pkmnid)
        
    
    def toPNG(self, f, back=False, shiny=False):
        if not back:
            sp_offset = self.sp_front
        else:
            sp_offset = self.sp_back
        
        if not shiny:
            palettebytes = decompress_bytes(self.rom.bytes[self.pal_normal:])
        else:
            palettebytes = decompress_bytes(self.rom.bytes[self.pal_shiny:])

        palette = Palette16.read(ByteArrayReader(palettebytes), 0)
        sprite = readCompressedSprite(self.rom, sp_offset, 64, 64)
        return toPNG(f, sprite, palette)
        
        