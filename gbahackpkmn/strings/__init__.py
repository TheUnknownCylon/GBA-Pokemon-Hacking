
"""
Submodule that handles all text stuff for pokemon games.
  Meaning it can encode / decode text from / to game byte code.
  Meaning it can add, update or remove text from the ROM.
  
TODO: Only one pre-defined alphabet can be used now, extend to
      support more (possibly by implementing a new PokeString object.
"""

import os, sys
from array import array

from gbahack import Resource
from gbahack.tools.numbers import toint

class PokeString(Resource):
    '''
    Class that represents a String resource in the ROM.
    '''
    
    name = "string"
    
    def __init__(self, text=""):
        '''Initialize a new PokeString, with a given text.'''
        self.text = text
        
        
    def getText(self):
        '''Returns the unicode text of this string.'''
        return self.text
    
    def append(self, appendtext):
        '''Appends some text to the actual string.'''
        self.text += appendtext
    
    
    @classmethod
    def read(cls, rom, pointer):
        #print("Decompile string %X\n"%pointer)

        p = pointer
        text = ""
        while True:
            p, byte = rom.readByte(p)
            if byte == 0xFF: break
            if byte == 0xFD:  #\v
                p, nextbyte = rom.readByte(p)
                if nextbyte in texthashinv:
                    text += texthashinv[nextbyte]
                else:
                    text += "\v\h%X"%nextbyte
            else:
                try:
                    text += decodeChar(byte)
                except Exception as e:
                    text += "?"
                    print(repr(e))
        
        return PokeString(text)
    
    
    def bytestring(self):
        #print("Compiling string %s" % self.text)
        text = self.text
        textarray = array('B')
    
        i = 0
        while i < len(text):
            char = text[i]
            i+=1
      
            if char == "[":
                ctrl = "["
                while i < len(text): #read until ]
                    char = text[i]
                    i+=1
                    ctrl += char
                    if char == "]":
                        #print("Looking up: %s"%ctrl)
                        if ctrl.lower() in texthash:
                            textarray.append(texthash["\\v"])
                            textarray.append(texthash[ctrl])
                        else:
                            textarray.append(textchars["?"])
                        break
            
            elif char == "\\":
                nextchar = text[i]
                i+=1
                char = ""+char+nextchar
                if char in texthash:
                    textarray.append(texthash[char])
                else:
                    textarray.append(0x00)
      
            else: #normal char to print
                if char not in textchars:
                    textarray.append(0x00)
                else:
                    textarray.append(textchars[char])
        
        #A text-array is always ended with 0xFF
        textarray.append(0xFF)
        
        return textarray



###################################

## Load chars etc. used by the PokeString encode/decode functions
## definitions are placed in files: ./textchars and ./texthashes

#  texthash: <hash>\t<value>  text hash, replace this complete thing with values in a text-string
#  textchar <char>\t<value>   text letter rewrite to hex

textchars = {}
texthash = {}

dirname = os.path.join(os.path.dirname(sys.argv[0]), "gbahackpkmn", "strings")
for line in open(dirname + "/textchars", 'r', encoding="iso-8859-15"):
    if line:
        (char, val) = line.split("\t")
        if len(char) > 1: #Chars can be represented as hex numers (&hxx)
            char = chr(toint(char))
        #print("Adding char. "+repr(char))
        textchars[char] = toint(val)

for line in open(dirname + "/texthashes", 'r', encoding="iso-8859-15"):
    if line:
        (hashv, val) = line.split("\t")
        texthash[hashv] = toint(val)

textcharsinv = dict(zip(textchars.values(), textchars))
texthashinv = dict(zip(texthash.values(), texthash))


def decodeChar(char):
    if char == 0x00: #special case
        return " "
    if char in texthashinv:
        return texthashinv[char]
        
    try:
        return textcharsinv[char]
    except:
        raise Exception("Can not decode text char %X (not defined)."%char)
    