
"""
Submodule that handles all text stuff for pokemon games.
  Meaning it can encode / decode text from / to game byte code.
  Meaning it can add, update or remove text from the ROM.
  
TODO: Only one pre-defined alphabet can be used now, extend to
      support more (possibly by implementing a new PokeString object.
"""

from gbahackpkmn.strings.pokestring import PokeString
from gbahackpkmn.strings.stringlist import StringList
